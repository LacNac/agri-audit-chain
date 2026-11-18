# agri-audit-chain

Agricultural Product Auditing, Blockchain Verification &amp; Public Traceability System

Nông dân gửi sản phẩm lên --> Kiểm định

## 1. Cài dependency

Trong terminal, *đang ở Backend* và đã activate venv:

pip install fastapi uvicorn sqlalchemy python-dotenv

## 2. Chạy server

uvicorn app.main:app --reload

Frontend hiện gọi backend đã deploy trên Render. Mở tài liệu API tại:

<https://agri-audit-chain-backend.onrender.com/docs>

Health endpoint:

<https://agri-audit-chain-backend.onrender.com/api/v1/health>

Kết quả health:

{
  "status": "OK",
  "database": "connected"
}

## 3. Database sẽ tự xuất hiện

Sau khi chạy lần đầu:

Backend
├── agri_audit.db       ← SQLite tự tạo
├── .env
├── app
│   ├── main.py
│   └── database
│       ├── **init**.py
│       ├── database.py
│       └── models.py
├── qr_codes
├── uploads
└── venv
