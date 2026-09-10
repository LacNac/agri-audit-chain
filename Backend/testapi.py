from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cho phép React gọi đến FastAPI
origins = [
    "http://localhost:5173",  # React Vite
    "http://localhost:3000",  # React thường
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Agri Audit Chain API!"
    }