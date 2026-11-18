# AgriTrace — Agricultural Product Auditing & Traceability

AgriTrace là ứng dụng quản lý kiểm định và truy xuất nguồn gốc nông sản. Nông dân tạo lô hàng và gửi kiểm định; kiểm định viên ghi nhận mẫu, tải báo cáo phòng thí nghiệm và phê duyệt hoặc từ chối lô hàng. Sau khi được duyệt, thông tin truy xuất có thể được tra cứu công khai bằng mã lô hoặc mã truy xuất/QR.

> **Phạm vi hiện tại:** AgriTrace dùng PostgreSQL khi được cấu hình, ghi lịch sử thao tác (audit trail) và tính SHA-256/hash proof cho file báo cáo; nếu thiếu cấu hình PostgreSQL, backend có chế độ SQLite phát triển để khởi động với database sẵn có. Có thể bật thêm tính năng neo hash audit lên mạng EVM bằng smart contract; dữ liệu gốc và PDF vẫn ở database/file storage. Khi tích hợp đầy đủ, AgriTrace và Cold Chain dùng hai database PostgreSQL riêng, trao đổi dữ liệu qua API; không dùng chung bảng hoặc ghi trực tiếp vào database của nhau.

## Chức năng chính

- **Nông dân:** đăng ký/đăng nhập, tạo và quản lý lô hàng, gửi lô để kiểm định, xem trạng thái và lý do từ chối, tạo mã QR truy xuất.
- **Kiểm định viên:** xem hàng đợi lô hàng, tạo mẫu, tải/cập nhật báo cáo PDF, kiểm tra tính toàn vẹn báo cáo và phê duyệt hoặc từ chối lô.
- **Quản trị viên:** xem dashboard, quản lý tài khoản và vai trò, theo dõi lô hàng và lịch sử hoạt động.
- **Tra cứu công khai:** xem hồ sơ của lô đã được kiểm định bằng mã lô hoặc mã truy xuất.
- **Backend API:** FastAPI, PostgreSQL, xác thực bằng bearer token và phân quyền theo vai trò.

## Công nghệ

- **Backend:** Python, FastAPI, PostgreSQL (`psycopg2`); SQLite dự phòng cho phát triển cục bộ
- **Blockchain tùy chọn:** Solidity / EVM qua Web3.py; neo hash SHA-256 của audit trail
- **Frontend:** HTML, CSS, JavaScript thuần
- **Tệp báo cáo:** PDF; hệ thống tính SHA-256 và lưu thông tin integrity proof
- **QR:** thư viện `qrcode` và Pillow

## Yêu cầu

- Python 3.10 trở lên
- PostgreSQL đang chạy và một database riêng cho AgriTrace
- Trình duyệt web hiện đại

## Cài đặt và chạy

Mở các terminal riêng cho PostgreSQL, Cold Chain, AgriTrace backend và frontend.

### 1. Tạo database PostgreSQL riêng cho AgriTrace

Tạo database một lần trong PostgreSQL; không dùng tên database Cold Chain:

```sql
CREATE DATABASE agri_audit_chain;
```

### 2. Chuyển dữ liệu SQLite hiện có sang PostgreSQL

Trong PowerShell tại thư mục `agri-audit-chain\Backend`, cài các package và đặt URL kết nối đến database AgriTrace. Thay `<USER>` và `<PASSWORD>` bằng thông tin PostgreSQL của bạn:

```powershell
Set-Location "C:\Users\DELL\OneDrive - National Economics University\Desktop\blockchain\agri-audit-chain\Backend"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:AGRI_DATABASE_URL = "postgresql://<USER>:<PASSWORD>@localhost:5432/agri_audit_chain"
python scripts\migrate_sqlite_to_postgres.py
```

Migration đọc `Backend/app/database/db.db`, chép dữ liệu vào các bảng PostgreSQL và cập nhật ID sequence. Nó dừng nếu database đích đã có dữ liệu hoặc phát hiện các bảng Cold Chain. File SQLite gốc được giữ nguyên làm bản dự phòng. Chỉ chạy migration một lần trên database AgriTrace trống.

### 3. Khởi động AgriTrace backend

Trong cùng terminal đã đặt `AGRI_DATABASE_URL`, chạy:

```powershell
$env:COLD_CHAIN_API_BASE_URL = "https://cold-chain-telemetry-system-1.onrender.com/api"
$env:COLD_CHAIN_API_USERNAME = "<Cold Chain STAFF username>"
$env:COLD_CHAIN_API_PASSWORD = "<Cold Chain STAFF password>"
$env:COLD_CHAIN_INTEGRATION_SECRET = "<same-random-secret-as-AGRI_INTEGRATION_SECRET>"
uvicorn app.main:app --reload
```

`AGRI_DATABASE_URL` phải trỏ đến database AgriTrace; ứng dụng chủ động từ chối khởi động nếu phát hiện các bảng nghiệp vụ Cold Chain. `COLD_CHAIN_API_BASE_URL` trỏ đến API server Cold Chain (mặc định là endpoint trên Render ở trên; nếu chạy Cold Chain cục bộ, đổi thành `http://127.0.0.1:3000/api`). `COLD_CHAIN_API_USERNAME` và `COLD_CHAIN_API_PASSWORD` là tài khoản dịch vụ có vai trò STAFF của Cold Chain; backend dùng chúng để đăng nhập và gọi `GET /api/agri-batches`, không gửi thông tin này xuống frontend. Cấu hình hai biến này trong môi trường chạy backend AgriTrace (bao gồm Render) để trang Auditor đọc được lô và trạng thái vận chuyển. Đặt cùng secret trong biến `AGRI_INTEGRATION_SECRET` của Cold Chain và `COLD_CHAIN_INTEGRATION_SECRET` của AgriTrace để đồng bộ Batch/trạng thái và timeline; các sự kiện chưa gửi được sẽ được retry nền. AgriTrace mặc định chạy tại <http://127.0.0.1:8000>; tài liệu API tại <http://127.0.0.1:8000/docs>. Schema, vai trò và quyền được khởi tạo khi backend chạy. File báo cáo PDF vẫn lưu tại `Backend/app/uploads/`.

Nếu không dùng dữ liệu SQLite cũ, có thể bỏ qua lệnh migration; khi `AGRI_DATABASE_URL` được đặt, backend tạo schema và tài khoản demo trong database PostgreSQL mới. Nếu không đặt biến này, backend dùng SQLite hiện có ở chế độ phát triển và in cảnh báo; nó không tự tạo hay chuyển schema SQLite.

Để chạy thử backend khi PostgreSQL chưa cài/chưa bật, bỏ trống `AGRI_DATABASE_URL` rồi chạy `uvicorn app.main:app --reload`. Backend sẽ dùng `Backend/app/database/db.db` ở chế độ SQLite phát triển và in cảnh báo; chế độ này không thay thế cấu hình PostgreSQL riêng khi kết nối đầy đủ với Cold Chain.

### 4. Bật neo audit lên blockchain EVM (tùy chọn)

Smart contract nằm tại `Backend/contracts/AgriAuditAnchor.sol`. Có thể biên dịch và triển khai contract lên một mạng EVM tương thích (ví dụ Sepolia hoặc mạng local) bằng Remix hoặc công cụ Solidity tương đương. Ví triển khai là owner và writer mặc định; nếu dùng ví backend khác, owner gọi `setWriter(<BACKEND_ADDRESS>, true)` trên contract. Dùng ví thử nghiệm riêng có ít gas token, không dùng private key của ví có tài sản thật.

Trong terminal backend, đặt các biến môi trường sau trước khi khởi động ứng dụng:

```powershell
$env:AGRI_BLOCKCHAIN_RPC_URL = "https://<evm-rpc-endpoint>"
$env:AGRI_BLOCKCHAIN_CONTRACT_ADDRESS = "0x<deployed-contract-address>"
$env:AGRI_BLOCKCHAIN_PRIVATE_KEY = "<private-key-of-authorized-writer>"
uvicorn app.main:app --reload
```

Khi cả ba biến được cấu hình, mỗi audit trail mới sẽ tạo một bản ghi chờ trong `blockchain_anchors`; worker nền gửi giao dịch và tự retry khi RPC lỗi. Hash được tính từ ID, người thực hiện, hành động, đối tượng, giá trị cũ/mới và thời điểm audit. Với upload báo cáo, dữ liệu audit có chứa SHA-256 của file, nên hash neo cũng cam kết nội dung báo cáo. Chỉ hash sự kiện được ghi on-chain; không gửi thông tin cá nhân, nội dung kiểm định, PDF hay secret lên blockchain. Khi không đặt biến blockchain, ứng dụng giữ nguyên chế độ hoạt động hiện tại và không gửi giao dịch.

Trạng thái neo cho một audit ID có thể xem qua `GET /audit-trails/{audit_id}/blockchain` (yêu cầu ADMIN hoặc AUDITOR). Trạng thái ban đầu là `PENDING`; sau khi giao dịch được xác nhận là `ANCHORED`, phản hồi có transaction hash và block number. Đây là neo hash theo từng audit event, không phải blockchain riêng do ứng dụng tự vận hành.

### 5. Chạy frontend

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
| Tích hợp kho lạnh (chỉ đọc, yêu cầu quyền Auditor) | `/cold-chain` |

Xem danh sách endpoint, schema và thử API tại `/docs` khi backend đang chạy. Dữ liệu AgriTrace được lưu trong PostgreSQL; báo cáo PDF nằm trong thư mục uploads và thông tin hash/lịch sử được ghi trong database.

Các endpoint `/cold-chain/warehouses`, `/cold-chain/vehicles`, `/cold-chain/telemetry` và các đường dẫn chi tiết tương ứng chuyển tiếp yêu cầu GET đến Cold Chain API. Auditor xem được xe, trạng thái chuyến đi, điểm lấy/giao hàng và telemetry mới nhất; Batch đang vận chuyển sẽ bị chặn thao tác kiểm định cả ở giao diện lẫn API. Đồng bộ danh sách Batch/trạng thái và cập nhật mốc vận chuyển dùng các API tích hợp riêng, không dùng chung database.

Batch có điểm đến giao hàng; khi tạo mới, Batch và mọi thay đổi AUDITED/REJECTED được gửi sang danh sách AgriTrace Batches của Cold Chain. Kho lạnh ghi nhận các mốc đã lấy hàng, nhập kho, gửi mẫu, giao đến điểm đích và trả hàng. Tác vụ kiểm tra các lô REJECTED chưa được cập nhật chạy tự động mỗi phút; mặc định thời hạn là 24 giờ.

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
│   │   ├── database/      # Schema PostgreSQL, kết nối và dữ liệu demo
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
- Cấu hình riêng `AGRI_DATABASE_URL`, `COLD_CHAIN_API_BASE_URL`, `COLD_CHAIN_API_USERNAME` và `COLD_CHAIN_API_PASSWORD`; không đưa thông tin xác thực database hoặc Cold Chain vào mã nguồn hay frontend.
