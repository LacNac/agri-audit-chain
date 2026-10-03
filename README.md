# AgriTrace — Agricultural Product Auditing & Traceability

AgriTrace là ứng dụng quản lý kiểm định và truy xuất nguồn gốc nông sản. Nông dân tạo lô hàng và gửi kiểm định; kiểm định viên ghi nhận mẫu, tải báo cáo phòng thí nghiệm và phê duyệt hoặc từ chối lô hàng. Sau khi được duyệt, thông tin truy xuất có thể được tra cứu công khai bằng mã lô hoặc mã truy xuất/QR.

> **Phạm vi hiện tại:** dự án lưu dữ liệu trong SQLite, ghi lịch sử thao tác (audit trail) và tính SHA-256/hash proof cho file báo cáo. Trong mã nguồn hiện tại chưa có tích hợp với một mạng blockchain bên ngoài; không nên xem hash proof là bằng chứng giao dịch trên blockchain công khai.

## Chức năng chính

- **Nông dân:** đăng ký/đăng nhập, tạo và quản lý lô hàng, gửi lô để kiểm định, xem trạng thái và lý do từ chối, tạo mã QR truy xuất.
- **Kiểm định viên:** xem hàng đợi lô hàng, tạo mẫu, tải/cập nhật báo cáo PDF, kiểm tra tính toàn vẹn báo cáo và phê duyệt hoặc từ chối lô.
- **Quản trị viên:** xem dashboard, quản lý tài khoản và vai trò, theo dõi lô hàng và lịch sử hoạt động.
- **Tra cứu công khai:** xem hồ sơ của lô đã được kiểm định bằng mã lô hoặc mã truy xuất.
- **Backend API:** FastAPI, SQLite, xác thực bằng bearer token và phân quyền theo vai trò.

## Công nghệ

- **Backend:** Python, FastAPI, SQLite
- **Frontend:** HTML, CSS, JavaScript thuần
- **Tệp báo cáo:** PDF; hệ thống tính SHA-256 và lưu thông tin integrity proof
- **QR:** thư viện `qrcode` và Pillow

## Yêu cầu

- Python 3.10 trở lên
- Trình duyệt web hiện đại

## Cài đặt và chạy

Mở hai terminal tại thư mục gốc dự án.

### 1. Chạy backend

Trong terminal thứ nhất:

```powershell
cd Backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Nếu PowerShell không cho phép kích hoạt virtual environment, có thể gọi trực tiếp Python trong môi trường ảo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend mặc định chạy tại <http://127.0.0.1:8000>. Tài liệu API tương tác có tại <http://127.0.0.1:8000/docs>.

Khi khởi động, ứng dụng tự khởi tạo/cập nhật schema SQLite, vai trò, quyền và các tài khoản demo. Database mặc định nằm tại `Backend/app/database/db.db`; các file báo cáo được lưu trong `Backend/app/uploads/`.

### 2. Chạy frontend

Trong terminal thứ hai, tại thư mục gốc dự án:

```powershell
py -m http.server 5500 --bind 127.0.0.1 --directory FrontEnd
```

Mở <http://127.0.0.1:5500>. Dùng đúng địa chỉ và cổng này để phù hợp với cấu hình CORS của backend và URL được tạo cho QR.

Các trang chính:

| Trang | Đường dẫn |
|---|---|
| Trang chủ / giới thiệu | `/index.html` |
| Đăng nhập | `/login.html` |
| Trang nông dân | `/farmer/farmer.html` |
| Dashboard kiểm định viên | `/auditor/auditdashboard.html` |
| Đăng nhập quản trị viên | `/admin/admin_login.html` |
| Dashboard quản trị viên | `/admin/admin.html` |
| Tra cứu công khai | `/lookup.html` hoặc trang hồ sơ trace trong `/public/trace.html` |

## Tài khoản và vai trò

Các tài khoản demo được khởi tạo trong `Backend/app/database/init_db.py`. Có thể dùng chúng cho môi trường phát triển cục bộ; xem thông tin đăng nhập trong file đó. **Không sử dụng tài khoản hoặc mật khẩu demo khi triển khai thật.**

Đăng nhập được tách theo vai trò:

- Nông dân: `POST /auth/login`
- Kiểm định viên: `POST /auth/login-auditor`
- Quản trị viên: `POST /auth/login-admin`
- Đăng ký nông dân: `POST /auth/register`

## API và dữ liệu

Các router chính được đăng ký trực tiếp trên ứng dụng, không có tiền tố `/api/v1`:

| Nhóm | Đường dẫn |
|---|---|
| Xác thực | `/auth` |
| Người dùng | `/users` |
| Lô hàng | `/batches` |
| Mẫu kiểm định | `/samples` |
| Nghiệp vụ kiểm định và báo cáo | `/auditor` |
| Quản trị | `/admin` |
| QR | `/qr` |
| Tra cứu công khai | `/public` |
| Lịch sử thao tác | `/audit-trails` |

Xem danh sách endpoint, schema và thử API tại `/docs` khi backend đang chạy. Dữ liệu được lưu trong SQLite; báo cáo PDF nằm trong thư mục uploads và thông tin hash/lịch sử được ghi trong database.

## Chạy kiểm thử

Từ terminal backend, cài `pytest` nếu môi trường chưa có:

```powershell
python -m pip install pytest
python -m pytest tests -q
```

## Cấu trúc dự án

```text
.
├── Backend/
│   ├── app/
│   │   ├── core/          # Cấu hình bảo mật và phân quyền
│   │   ├── database/      # Khởi tạo/migration SQLite và dữ liệu demo
│   │   ├── dependencies/  # Dependency xác thực và RBAC
│   │   ├── routers/       # API endpoints
│   │   ├── schema/        # Pydantic request/response models
│   │   ├── services/      # Nghiệp vụ, audit trail, QR và báo cáo
│   │   └── uploads/       # PDF báo cáo
│   ├── tests/             # Kiểm thử backend
│   └── requirements.txt
├── FrontEnd/
│   ├── admin/
│   ├── auditor/
│   ├── farmer/
│   ├── public/
│   ├── assets/
│   ├── css/
│   └── js/
└── README.md
```

## Lưu ý triển khai

- Cấu hình CORS hiện cho phép frontend tại `http://127.0.0.1:5500` và `http://localhost:5500`.
- Backend có sẵn thông tin demo và các hằng số xác thực phục vụ phát triển. Trước khi đưa vào môi trường thật, cần thay cấu hình bí mật, thay mật khẩu demo và rà soát lại cấu hình bảo mật.
- Không xóa hoặc chia sẻ database/file báo cáo nếu cần giữ lại dữ liệu đã tạo.
