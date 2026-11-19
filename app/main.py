import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.init_db import initialize_database
from .database.postgres import connect_app_database
from .routers import audit_trails, auth, admin, auditor, batches, cold_chain, notifications, public, qr, samples, users
from .services.blockchain_service import process_blockchain_outbox, validate_blockchain_config
from .services.batch_service import process_expired_rejected_batches
from .services.cold_chain_service import process_cold_chain_outbox

initialize_database()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router)
app.include_router(auditor.router)
app.include_router(batches.router)
app.include_router(cold_chain.router)
app.include_router(samples.router)
app.include_router(audit_trails.router)
app.include_router(notifications.router)
app.include_router(qr.router)
app.include_router(public.router)
app.include_router(users.router)


async def background_check_expired_batches():
    while True:
        try:
            await asyncio.sleep(60)
            conn = connect_app_database()
            try:
                process_expired_rejected_batches(conn)
                process_cold_chain_outbox(conn)
                process_blockchain_outbox(conn)
            finally:
                conn.close()
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Background batch processing failed")


@app.on_event("startup")
async def startup_event():
    validate_blockchain_config()
    asyncio.create_task(background_check_expired_batches())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "https://agri-audit-chain.onrender.com,http://127.0.0.1:5500,http://localhost:5500",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
