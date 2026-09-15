from fastapi import FastAPI

app = FastAPI(
    title="Agricultural Traceability API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Agricultural Traceability API is running"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "OK"
    }