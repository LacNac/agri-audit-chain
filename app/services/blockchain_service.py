import hashlib
import json
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

_CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "eventHash", "type": "bytes32"}],
        "name": "anchorAuditHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


def _configuration() -> dict[str, str] | None:
    names = (
        "AGRI_BLOCKCHAIN_RPC_URL",
        "AGRI_BLOCKCHAIN_CONTRACT_ADDRESS",
        "AGRI_BLOCKCHAIN_PRIVATE_KEY",
    )
    values = {name: os.getenv(name, "").strip() for name in names}
    configured = {name for name, value in values.items() if value}
    if not configured:
        return None

    missing = sorted(set(names) - configured)
    if missing:
        raise RuntimeError(
            "Blockchain anchoring requires all of: "
            + ", ".join(names)
            + f". Missing: {', '.join(missing)}."
        )
    return values


def validate_blockchain_config() -> bool:
    return _configuration() is not None


def _ensure_blockchain_anchors_table(db):
    timestamp_type = (
        "DATETIME"
        if isinstance(db, sqlite3.Connection)
        else "TIMESTAMP WITHOUT TIME ZONE"
    )
    db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS blockchain_anchors (
            audit_id INTEGER PRIMARY KEY,
            event_hash TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'PENDING',
            transaction_hash TEXT,
            block_number BIGINT,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_error TEXT,
            created_at {timestamp_type} DEFAULT CURRENT_TIMESTAMP,
            anchored_at {timestamp_type}
        )
        """
    )


def enqueue_audit_anchor(db, audit_id: int):
    if _configuration() is None:
        return

    _ensure_blockchain_anchors_table(db)
    audit = db.execute(
        """
        SELECT id, user_id, action, entity_type, entity_id, old_value, new_value,
               created_at
        FROM audit_trails
        WHERE id = ?
        """,
        (audit_id,),
    ).fetchone()
    canonical_event = json.dumps(
        dict(
            zip(
                (
                    "audit_id",
                    "user_id",
                    "action",
                    "entity_type",
                    "entity_id",
                    "old_value",
                    "new_value",
                    "created_at",
                ),
                audit,
            )
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    event_hash = hashlib.sha256(canonical_event.encode("utf-8")).hexdigest()
    db.execute(
        """
        INSERT INTO blockchain_anchors (audit_id, event_hash)
        VALUES (?, ?)
        """,
        (audit_id, event_hash),
    )


def get_audit_anchor(db, audit_id: int):
    _ensure_blockchain_anchors_table(db)
    row = db.execute(
        """
        SELECT event_hash, status, transaction_hash, block_number, attempts,
               created_at, anchored_at
        FROM blockchain_anchors
        WHERE audit_id = ?
        """,
        (audit_id,),
    ).fetchone()
    if not row:
        return None
    return dict(
        zip(
            (
                "event_hash",
                "status",
                "transaction_hash",
                "block_number",
                "attempts",
                "created_at",
                "anchored_at",
            ),
            row,
        )
    )


def _submit_hash(event_hash: str, config: dict[str, str]):
    from web3 import Web3

    web3 = Web3(
        Web3.HTTPProvider(
            config["AGRI_BLOCKCHAIN_RPC_URL"], request_kwargs={"timeout": 15}
        )
    )
    if not web3.is_connected():
        raise ConnectionError("Could not connect to the configured blockchain RPC.")

    account = web3.eth.account.from_key(config["AGRI_BLOCKCHAIN_PRIVATE_KEY"])
    contract_address = Web3.to_checksum_address(
        config["AGRI_BLOCKCHAIN_CONTRACT_ADDRESS"]
    )
    contract = web3.eth.contract(address=contract_address, abi=_CONTRACT_ABI)
    transaction = contract.functions.anchorAuditHash(
        bytes.fromhex(event_hash)
    ).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address, "pending"),
            "chainId": web3.eth.chain_id,
            "gas": 150_000,
            "gasPrice": web3.eth.gas_price,
        }
    )
    signed = web3.eth.account.sign_transaction(
        transaction, config["AGRI_BLOCKCHAIN_PRIVATE_KEY"]
    )
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hex = tx_hash.hex()
    return f"0x{tx_hex.removeprefix('0x')}"


def _get_transaction_receipt(transaction_hash: str, config: dict[str, str]):
    from web3 import Web3
    from web3.exceptions import TransactionNotFound

    web3 = Web3(
        Web3.HTTPProvider(
            config["AGRI_BLOCKCHAIN_RPC_URL"], request_kwargs={"timeout": 15}
        )
    )
    if not web3.is_connected():
        raise ConnectionError("Could not connect to the configured blockchain RPC.")
    if not transaction_hash.startswith("0x"):
        transaction_hash = f"0x{transaction_hash}"
    try:
        receipt = web3.eth.get_transaction_receipt(transaction_hash)
    except TransactionNotFound:
        return None
    return receipt


def process_blockchain_outbox(db) -> int:
    config = _configuration()
    if config is None:
        return 0

    _ensure_blockchain_anchors_table(db)
    pending_rows = db.execute(
        """
        SELECT audit_id, event_hash
        FROM blockchain_anchors
        WHERE status = 'PENDING'
        ORDER BY audit_id
        LIMIT 50
        """
    ).fetchall()
    for audit_id, event_hash in pending_rows:
        try:
            transaction_hash = _submit_hash(event_hash, config)
        except Exception as error:
            logger.exception("Could not submit audit event %s to blockchain", audit_id)
            db.execute(
                """
                UPDATE blockchain_anchors
                SET attempts = attempts + 1, last_error = ?
                WHERE audit_id = ?
                """,
                (str(error)[:1000], audit_id),
            )
        else:
            db.execute(
                """
                UPDATE blockchain_anchors
                SET status = 'SUBMITTED', transaction_hash = ?,
                    attempts = attempts + 1, last_error = NULL
                WHERE audit_id = ?
                """,
                (transaction_hash, audit_id),
            )
        db.commit()

    submitted_rows = db.execute(
        """
        SELECT audit_id, transaction_hash
        FROM blockchain_anchors
        WHERE status = 'SUBMITTED'
        ORDER BY audit_id
        LIMIT 50
        """
    ).fetchall()
    anchored = 0
    for audit_id, transaction_hash in submitted_rows:
        try:
            receipt = _get_transaction_receipt(transaction_hash, config)
        except Exception as error:
            logger.exception(
                "Could not check blockchain transaction for audit %s", audit_id
            )
            db.execute(
                """
                UPDATE blockchain_anchors SET last_error = ?
                WHERE audit_id = ?
                """,
                (str(error)[:1000], audit_id),
            )
        else:
            if receipt is None:
                continue
            if receipt["status"] != 1:
                db.execute(
                    """
                    UPDATE blockchain_anchors
                    SET status = 'FAILED', last_error = ?
                    WHERE audit_id = ?
                    """,
                    ("Blockchain transaction reverted.", audit_id),
                )
                db.commit()
                continue
            db.execute(
                """
                UPDATE blockchain_anchors
                SET status = 'ANCHORED', transaction_hash = ?, block_number = ?,
                    anchored_at = CURRENT_TIMESTAMP, last_error = NULL
                WHERE audit_id = ?
                """,
                (transaction_hash, receipt["blockNumber"], audit_id),
            )
            anchored += 1
        db.commit()
    return anchored
