from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.init_db import initialize_database
from .routers import audit_trails, auth, admin, auditor, batches, public, qr, samples, users

initialize_database()

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router)
app.include_router(auditor.router)
app.include_router(batches.router)
app.include_router(samples.router)
app.include_router(audit_trails.router)
app.include_router(qr.router)
app.include_router(public.router)
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
