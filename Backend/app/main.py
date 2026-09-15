from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agricultural Traceability API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Agricultural Traceability API is running"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "OK",
        "database": "connected"
    }
