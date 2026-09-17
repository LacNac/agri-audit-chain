# agri-audit-chain

Agricultural Product Auditing, Blockchain Verification &amp; Public Traceability System

Nông dân gửi sản phẩm lên --> Kiểm định

## 1. Cài dependency

Trong terminal, *đang ở Backend* và đã activate venv:

pip install fastapi uvicorn sqlalchemy python-dotenv

## 2. Chạy server

uvicorn app.main:app --reload

Nếu thành công sẽ thấy:

Uvicorn running on <http://127.0.0.1:8000>

Mở:

<http://127.0.0.1:8000/docs>

và:

<http://127.0.0.1:8000/api/v1/health>

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
