import os
import sys
import time
from pathlib import Path

# Đảm bảo đường dẫn import app module đúng
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(ROOT_DIR / ".env")

from app.database.postgres import connect_app_database
from app.services.blockchain_service import (
    enqueue_audit_anchor,
    process_blockchain_outbox,
    validate_blockchain_config,
    _configuration,
)


def run_sync():
    print("=" * 60)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ DỮ LIỆU LÊN BLOCKCHAIN SEPOLIA")
    print("=" * 60)

    if not validate_blockchain_config():
        print("❌ LỖI: Chưa cấu hình đủ 3 biến môi trường trong file .env:")
        print("   - AGRI_BLOCKCHAIN_RPC_URL")
        print("   - AGRI_BLOCKCHAIN_CONTRACT_ADDRESS")
        print("   - AGRI_BLOCKCHAIN_PRIVATE_KEY")
        return

    config = _configuration()
    print(f"📡 RPC URL: {config['AGRI_BLOCKCHAIN_RPC_URL']}")
    print(f"📜 Contract: {config['AGRI_BLOCKCHAIN_CONTRACT_ADDRESS']}")

    conn = connect_app_database()
    try:
        # 1. Tìm các bản ghi trong audit_trails chưa có trong blockchain_anchors
        rows = conn.execute(
            """
            SELECT a.id FROM audit_trails a
            LEFT JOIN blockchain_anchors b ON a.id = b.audit_id
            WHERE b.audit_id IS NULL
            ORDER BY a.id ASC
            """
        ).fetchall()

        if rows:
            print(f"👉 Tìm thấy {len(rows)} bản ghi audit chưa được enqueue. Đang tạo mã băm SHA256...")
            for (audit_id,) in rows:
                enqueue_audit_anchor(conn, audit_id)
            conn.commit()
            print("✅ Đã tạo hash và đưa vào hàng đợi PENDING thành công.")
        else:
            print("ℹ️ Tất cả bản ghi audit đã nằm trong hàng đợi blockchain_anchors.")

        # 2. Xử lý hàng đợi gửi lên Blockchain
        pending_count = conn.execute(
            "SELECT COUNT(*) FROM blockchain_anchors WHERE status = 'PENDING'"
        ).fetchone()[0]
        submitted_count = conn.execute(
            "SELECT COUNT(*) FROM blockchain_anchors WHERE status = 'SUBMITTED'"
        ).fetchone()[0]
        anchored_count = conn.execute(
            "SELECT COUNT(*) FROM blockchain_anchors WHERE status = 'ANCHORED'"
        ).fetchone()[0]

        print(f"\n📊 Trạng thái hiện tại trong CSDL:")
        print(f"   - PENDING:   {pending_count}")
        print(f"   - SUBMITTED: {submitted_count}")
        print(f"   - ANCHORED:  {anchored_count}")

        if pending_count > 0 or submitted_count > 0:
            print("\n🔄 Đang gửi giao dịch lên mạng Sepolia qua Web3...")
            anchored = process_blockchain_outbox(conn)
            print(f"🎉 Đợt 1 hoàn tất: Đã xác nhận {anchored} bản ghi ANCHORED!")

            # In ra các transaction hash vừa gửi
            anchors = conn.execute(
                """
                SELECT audit_id, event_hash, status, transaction_hash, block_number, last_error
                FROM blockchain_anchors
                WHERE transaction_hash IS NOT NULL
                ORDER BY audit_id DESC
                LIMIT 5
                """
            ).fetchall()

            if anchors:
                print("\n🔍 Các giao dịch gần nhất:")
                for aid, h, status, tx, block, err in anchors:
                    print(f"   • Audit #{aid} [{status}]: tx={tx} (block {block})")
                    if tx:
                        print(f"     Explorer: https://sepolia.etherscan.io/tx/{tx}")
                    if err:
                        print(f"     Lỗi: {err}")
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("Hoàn tất!")
    print("=" * 60)


if __name__ == "__main__":
    run_sync()
