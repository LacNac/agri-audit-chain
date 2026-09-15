from fastapi import FastAPI
from routers import auth, admin, auditor, batches, public, users

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
