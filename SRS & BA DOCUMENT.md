# SRS & BA Doc

**Đề tài: AgriTrace Platform \- Phân hệ Kiểm định (Auditor Gatekeeper), Blockchain & Tra cứu công khai**

**2\. Tổng quan bài toán**  
***2.1. Bối cảnh bài toán***  
Hệ thống được xây dựng nhằm giải quyết bài toán quản lý, kiểm định và truy xuất nguồn gốc nông sản theo hướng minh bạch, an toàn và có khả năng xác minh. Hệ thống cho phép nông dân tạo lô hàng ở trạng thái UNVERIFIED, sau đó Auditor thực hiện kiểm định dựa trên báo cáo kiểm nghiệm phòng lab. Chỉ những lô hàng đáp ứng điều kiện kiểm định và có bằng chứng SHA-256 hợp lệ mới được chuyển sang trạng thái AUDITED.  
Hệ thống áp dụng RBAC tại Backend để kiểm soát quyền thực hiện các API, đồng thời sử dụng Proof of Integrity dựa trên chuỗi hash được lưu trong cơ sở dữ liệu nhằm đảm bảo khả năng kiểm tra tính toàn vẹn của dữ liệu. Mỗi lô hàng được gắn mã QR để người tiêu dùng có thể truy cập cổng tra cứu nguồn gốc công khai. Admin Dashboard được cung cấp để quản trị tập trung toàn hệ thống. Việc tích hợp Ethereum Testnet/Smart Contract và NFC NTAG424 DNA được định hướng là các chức năng mở rộng tùy theo phạm vi triển khai.  
***2.2. Vấn đề cần giải quyết***  
Hoạt động quản lý và truy xuất nguồn gốc nông sản đặt ra yêu cầu cao về tính chính xác, minh bạch và khả năng xác minh của thông tin. Tuy nhiên, trong quá trình quản lý lô hàng, một số vấn đề có thể phát sinh:  
\- Thiếu cơ chế kiểm định độc lập: Thông tin về lô hàng do nông dân cung cấp chưa có cơ chế rõ ràng để xác nhận rằng lô hàng đã được một bên có thẩm quyền kiểm định và đáp ứng các yêu cầu về chất lượng.  
\- Chưa kiểm soát chặt quyền thao tác trên hệ thống: Nếu quyền của người dùng không được kiểm soát ở phía Backend, người dùng có thể thực hiện các thao tác vượt quá phạm vi trách nhiệm, dẫn đến nguy cơ thay đổi trạng thái, tạo hoặc chỉnh sửa dữ liệu không đúng thẩm quyền.  
\- Khó xác minh tính toàn vẹn của hồ sơ kiểm nghiệm: Báo cáo kiểm nghiệm phòng lab là một trong những bằng chứng quan trọng của quá trình kiểm định. Nếu không có cơ chế ghi nhận và đối chiếu tính toàn vẹn của tài liệu, việc xác định báo cáo có bị thay đổi sau khi được ghi nhận hay không sẽ gặp khó khăn.
\- Chưa có cơ chế kiểm soát vòng đời của lô hàng: Lô hàng cần có trạng thái rõ ràng trong suốt quá trình từ khi được tạo, kiểm định đến khi được công khai. Đặc biệt, cần ngăn chặn việc một lô hàng chưa được kiểm định nhưng đã được coi là hợp lệ hoặc được cung cấp cho người tiêu dùng dưới trạng thái đã kiểm định.  
\- Người tiêu dùng khó tiếp cận thông tin nguồn gốc: Người tiêu dùng cần một phương thức đơn giản để xác minh nguồn gốc và thông tin kiểm định của sản phẩm mà không cần truy cập vào hệ thống quản trị nội bộ.  
\- Thiếu khả năng quản trị và giám sát tập trung: Các hoạt động liên quan đến người dùng, phân quyền, lô hàng, kiểm định và truy xuất cần được quản lý tập trung để hỗ trợ việc giám sát, kiểm tra và vận hành hệ thống.  
***2.3. Mục tiêu hệ thống***  
Hệ thống hướng tới các mục tiêu sau:

1. Quản lý tập trung thông tin các lô nông sản.  
2. Kiểm soát vòng đời của lô hàng từ khi tạo đến khi được kiểm định.  
3. Đảm bảo chỉ Auditor có quyền thực hiện phê duyệt kiểm định.  
4. Liên kết chặt chẽ giữa Batch, Sample và Laboratory Test Report.  
5. Sử dụng SHA-256 để đảm bảo tính toàn vẹn của báo cáo kiểm nghiệm.  
6. Xây dựng Proof of Integrity nhằm mô phỏng cơ chế bất biến của Blockchain.  
7. Kiểm soát quyền truy cập ở phía Backend bằng RBAC.  
8. Cung cấp QR Code để người tiêu dùng truy xuất thông tin.  
9. Cung cấp cổng tra cứu nguồn gốc công khai.  
10. Cung cấp Admin Dashboard để quản trị và theo dõi toàn bộ hệ thống.  
11. Có khả năng mở rộng sang Blockchain và NFC chống làm giả trong tương lai.

***2.4. Phạm vi hệ thống***  
Trong phạm vi, hệ thống bao gồm:  
\- Quản lý người dùng và phân quyền.  
\- Quản lý thông tin nông dân.  
\- Quản lý lô hàng.  
\- Quản lý mẫu kiểm nghiệm.  
\- Quản lý Laboratory Test Report.  
\- Upload và lưu trữ báo cáo kiểm nghiệm.  
\- Tính toán và xác minh SHA-256.  
\- Quy trình Auditor kiểm tra và phê duyệt.  
\- Quản lý trạng thái lô hàng.  
\- Proof of Integrity bằng chuỗi hash lưu trong Database.  
\- Sinh và quản lý QR Code.  
\- Cổng tra cứu nguồn gốc công khai.  
\- Admin Dashboard.  
\- Logging và Audit Trail.  
Ngoài phạm vi / tùy chọn:  
\- Triển khai Smart Contract thực tế trên Ethereum Testnet.  
\- Kết nối Web3.  
\- Tích hợp NFC NTAG424 DNA và Dynamic SUN MAC.  
\- Tích hợp trực tiếp với hệ thống của phòng thí nghiệm.  
\- Tự động kiểm nghiệm nông sản.  
**Lưu ý:** Hệ thống không trực tiếp thực hiện kiểm nghiệm chất lượng nông sản. Việc kiểm nghiệm được thực hiện bởi phòng thí nghiệm; hệ thống có nhiệm vụ quản lý, xác thực và liên kết thông tin kiểm nghiệm với lô hàng.  
***2.5. Tổng quan giải pháp***  
Giải pháp được xây dựng dựa trên việc tạo một chuỗi liên kết định danh giữa lô hàng và thông tin kiểm nghiệm.  
Batch → Sample → Laboratory Test Report → SHA-256 → Auditor Review → Audit Proof → AUDITED → Package / Trace ID → QR Code → Consumer  
Khi nông dân tạo một lô hàng, hệ thống cấp cho lô hàng một Batch ID/Batch Code duy nhất và đặt trạng thái UNVERIFIED.  
Sau khi mẫu của lô hàng được gửi đi kiểm nghiệm, kết quả được thể hiện trong Laboratory Test Report. Báo cáo phải có thông tin định danh tương ứng với mẫu và Batch.  
Auditor tiếp nhận báo cáo, kiểm tra tính hợp lệ và thực hiện phê duyệt. Backend tự động tính SHA-256 của báo cáo và lưu Proof of Integrity.  
Chỉ khi đáp ứng các điều kiện kiểm định, Batch mới được chuyển sang trạng thái:  
UNVERIFIED → AUDITED  
Sau khi Batch được xác nhận, hệ thống mới cho phép kích hoạt thông tin truy xuất và liên kết QR Code với Batch/Package tương ứng.  
***2.6. Các bên liên quan (Stakeholders)***

| Stakeholder | Vai trò |
| ----- | ----- |
| Nông dân/Farmer | Tạo và cung cấp thông tin lô hàng |
| Phòng thí nghiệm/Laboratory | Thực hiện kiểm nghiệm và phát hành báo cáo |
| Auditor | Kiểm tra và phê duyệt kết quả kiểm định |
| Doanh nghiệp/Đơn vị quản lý | Quản lý chuỗi cung ứng và vận hành hệ thống |
| Quản trị viên/Administrator | Quản trị người dùng, phân quyền và dữ liệu |
| Người tiêu dùng/Consumer | Tra cứu thông tin nguồn gốc sản phẩm |
| Đơn vị đóng gói/xuất hàng | Đóng gói, gắn định danh và đưa sản phẩm ra thị trường |

***2.7. Đối tượng sử dụng (Actors)***  
Các Actor chính của hệ thống:

| Actor | Mô tả |
| ----- | ----- |
| Farmer | Tạo và quản lý lô hàng của mình |
| Auditor | Thẩm định lô hàng và phê duyệt/từ chối |
| Admin | Quản trị toàn hệ thống |
| Consumer | Tra cứu nguồn gốc bằng QR |
| Company/Operator | Quản lý hoạt động chuỗi cung ứng |

***2.8. Các module chính***  
Hệ thống dự kiến bao gồm các module:  
1\. Authentication & Authorization

- Đăng nhập.  
- JWT Authentication.  
- RBAC.  
- Kiểm soát quyền ở Backend/API.

2\. Batch Management

- Tạo lô hàng.  
- Cập nhật thông tin lô.  
- Quản lý trạng thái.  
- Quản lý Batch ID/Batch Code.

3\. Sample Management

- Tạo Sample ID.  
- Liên kết Sample với Batch.  
- Theo dõi mẫu được gửi kiểm nghiệm.

4\. Auditor Gatekeeper

- Danh sách lô chờ kiểm định.  
- Xem thông tin Batch.  
- Upload Laboratory Test Report.  
- Kiểm tra báo cáo.  
- Tính SHA-256.  
- Approve/Reject.  
- Ghi nhận Audit Trail.

5\. Proof of Integrity

- Tạo hash.  
- Lưu hash của Laboratory Test Report.  
- Xây dựng chuỗi hash.  
- Kiểm tra tính toàn vẹn dữ liệu.

6\. QR & Traceability

- Sinh QR.  
- Liên kết QR với Batch/Package.  
- Kích hoạt QR sau khi Batch được phê duyệt.  
- Tra cứu nguồn gốc.

7\. Public Traceability Portal  
Người tiêu dùng có thể:

- Quét QR;  
- Xem thông tin sản phẩm;  
- Xem nguồn gốc;  
- Xem trạng thái kiểm định;  
- Xem thông tin kiểm nghiệm được phép công khai.

8\. Admin Dashboard

- Quản lý người dùng.  
- Quản lý role/permission.  
- Theo dõi Batch.  
- Theo dõi Audit.  
- Thống kê hệ thống.  
- Theo dõi Audit Log.

9\. Blockchain / NFC Extension  
Các chức năng mở rộng:

- Smart Contract.  
- Ethereum Testnet.  
- Web3.  
- NFC NTAG424 DNA.  
- Dynamic SUN MAC.

2.9. Ràng buộc và giả định

- Ràng buộc:  
  - Mỗi Batch phải có một định danh duy nhất.  
  - Batch mới tạo phải có trạng thái UNVERIFIED.  
  - Farmer không được tự chuyển Batch sang AUDITED.  
  - Chỉ Auditor có quyền phê duyệt Batch.  
  - Laboratory Test Report phải được liên kết với đúng Batch/Sample.  
  - SHA-256 phải được Backend tự động tạo khi tiếp nhận báo cáo.  
  - QR chỉ được sử dụng để xác nhận/truy xuất Batch đã được hệ thống phê duyệt.  
  - Quyền truy cập API phải được kiểm tra tại Backend.  
  - Proof of Integrity được lưu trong Database trong phiên bản hiện tại.  
  - Blockchain là chức năng tùy chọn.  
  - Hệ thống không trực tiếp thực hiện kiểm nghiệm vật lý nông sản.  
- Giả định:  
  - Thông tin do phòng Lab cung cấp là hợp lệ.  
  - Mẫu kiểm nghiệm được lấy từ đúng Batch và được quản lý theo quy trình của đơn vị kiểm nghiệm.  
  - Auditor là người có thẩm quyền thực hiện việc thẩm định.  
  - Thông tin Batch được nhập vào hệ thống là chính xác.  
  - Quy trình đóng gói và gắn QR/NFC được thực hiện theo quy trình của doanh nghiệp.  
  - Hệ thống phần mềm chịu trách nhiệm xác minh tính nhất quán của dữ liệu số, trong khi việc bảo đảm hàng hóa vật lý đúng với Batch cần có quy trình kiểm soát vật lý tương ứng.

**3\. Business Requirements – Yêu cầu nghiệp vụ**  
***3.1. Business Goals – Mục tiêu nghiệp vụ***  
Hệ thống được xây dựng nhằm hỗ trợ doanh nghiệp quản lý quy trình kiểm định và truy xuất nguồn gốc đối với các lô sản phẩm nông nghiệp, đồng thời nâng cao tính minh bạch và khả năng xác thực của thông tin được cung cấp cho người tiêu dùng.  
Các mục tiêu nghiệp vụ chính bao gồm:

- BG-01 Quản lý tập trung thông tin lô hàng: Xây dựng một hệ thống tập trung để quản lý thông tin Batch, Sample, Laboratory Test Report và trạng thái kiểm định thay cho việc quản lý phân tán hoặc thủ công.  
- BG-02 Kiểm soát quy trình kiểm định: Đảm bảo một Batch chỉ được xác nhận là AUDITED sau khi trải qua quy trình kiểm tra và phê duyệt bởi Auditor có thẩm quyền.  
- BG-03 Đảm bảo liên kết dữ liệu: Đảm bảo thông tin giữa Batch, Sample và Laboratory Test Report được liên kết chính xác, hạn chế tình trạng sử dụng kết quả kiểm nghiệm của Batch này cho Batch khác.  
- BG-04 – Đảm bảo tính toàn vẹn của tài liệu: Sử dụng SHA-256 để xác định tính toàn vẹn của Laboratory Test Report và sử dụng Proof of Integrity để ghi nhận tính toàn vẹn của các thông tin và thao tác quan trọng trong hệ thống.  
- BG-05 Minh bạch thông tin với người tiêu dùng: Cung cấp cơ chế QR để người tiêu dùng truy cập thông tin truy xuất nguồn gốc của Batch đã được kiểm định.  
- BG-06 Kiểm soát quyền truy cập: Đảm bảo mỗi nhóm người dùng chỉ được thực hiện các nghiệp vụ phù hợp với vai trò được cấp thông qua cơ chế RBAC.  
- BG-07 Hỗ trợ quản trị và kiểm tra: Cung cấp Audit Trail và Admin Dashboard để doanh nghiệp quản lý hệ thống, theo dõi hoạt động và kiểm tra lịch sử xử lý.  
- BG-08 Tạo nền tảng mở rộng: Thiết kế hệ thống có khả năng mở rộng để tích hợp Blockchain hoặc công nghệ NFC chống giả trong các phiên bản tương lai.

***3.2. Business Requirements – Yêu cầu nghiệp vụ***  
*3.2.1. BR-01 \- Quản lý Batch*  
Hệ thống phải cho phép Farmer tạo và quản lý Batch của mình.  
Khi tạo Batch:

- Batch Code/Batch ID phải do hệ thống sinh và đảm bảo duy nhất.  
- Farmer phải cung cấp các thông tin bắt buộc của Batch, bao gồm thông tin sản phẩm, ngày sản xuất/thu hoạch, số lượng, đơn vị và nguồn gốc.  
- Batch mới phải có trạng thái mặc định là UNVERIFIED.  
- Farmer không được tự đặt trạng thái Batch thành AUDITED.

Farmer được phép chỉnh sửa hoặc xóa Batch khi Batch chưa được Auditor xác nhận, theo các trạng thái được hệ thống cho phép.  
Batch đã ở trạng thái AUDITED không được Farmer chỉnh sửa hoặc xóa trực tiếp.  
*3.2.2. BR-02 \- Quản lý Sample*  
Hệ thống phải cho phép tạo Sample thuộc một Batch cụ thể.

- Sample ID phải được hệ thống tạo và đảm bảo duy nhất.  
- Mỗi Sample chỉ thuộc về một Batch.  
- Một Batch có thể có nhiều Sample.  
- Sample phải chứa thông tin cần thiết để xác định nguồn gốc và quá trình lấy mẫu.  
- Sample phải được liên kết với Batch trước khi được sử dụng trong quá trình kiểm nghiệm.

Quan hệ nghiệp vụ: Batch → Sample(s) → Laboratory Test Report  
*3.2.3. BR-03 \- Quản lý Laboratory Test Report*  
Hệ thống phải cho phép lưu trữ Laboratory Test Report liên quan đến Sample và Batch.  
Laboratory Test Report phải có khả năng xác định:

- Report ID;  
- Sample ID;  
- Batch Code/Batch ID;  
- Thông tin kết quả kiểm nghiệm;  
- Thông tin phòng thí nghiệm;  
- Ngày kiểm nghiệm;  
- Tài liệu báo cáo được tải lên hệ thống.

Hệ thống phải kiểm tra sự tương ứng giữa Report, Sample và Batch trước khi cho phép Auditor phê duyệt.  
Nếu Report thuộc Sample hoặc Batch khác với Batch đang được kiểm định, hệ thống phải từ chối quá trình phê duyệt.  
*3.2.4. BR-04 \- Kiểm định và phê duyệt Batch*  
Auditor là vai trò có quyền thực hiện nghiệp vụ kiểm định và phê duyệt Batch.  
Auditor phải kiểm tra tối thiểu:

1. Thông tin Batch;  
2. Sample liên quan;  
3. Laboratory Test Report;  
4. SHA-256 của Report;  
5. Proof of Integrity;  
6. Tính nhất quán giữa Batch – Sample – Report.

Batch chỉ được chuyển sang trạng thái AUDITED khi tất cả điều kiện kiểm định bắt buộc đều hợp lệ.  
Nếu thiếu Report, SHA-256 hoặc Proof of Integrity, hoặc dữ liệu không hợp lệ, hệ thống phải chặn thao tác Approve.  
*3.2.5. BR-05 \- Từ chối và kiểm định lại*  
Auditor có quyền Reject Batch nếu Batch không đáp ứng các điều kiện kiểm định.  
Khi Reject:

- Batch chuyển sang trạng thái REJECTED.  
- Auditor phải ghi nhận lý do từ chối.  
- Farmer có thể xem lý do Reject.  
- Farmer được phép sửa đổi hoặc bổ sung thông tin cần thiết.  
- Farmer có thể gửi lại Batch để Auditor kiểm định.  
- Farmer không được tự chuyển Batch từ REJECTED sang AUDITED.

Mỗi lần kiểm định và kết quả kiểm định phải được ghi nhận trong Audit Trail.  
*3.2.6. BR-06 \- Tính toàn vẹn của Laboratory Test Report*  
Khi Laboratory Test Report được tải lên hệ thống, backend phải tính toán giá trị SHA-256 của file và lưu giá trị này cùng với thông tin Report.  
SHA-256 được sử dụng để kiểm tra xem file Report có bị thay đổi sau khi được ghi nhận hay không.  
Nếu nội dung file thay đổi làm giá trị SHA-256 không còn khớp với giá trị đã lưu, Report phải được xác định là không hợp lệ và không được sử dụng để hoàn tất quá trình Audit.  
*3.2.7. BR-07 \- Proof of Integrity*  
Hệ thống phải tạo và lưu Proof of Integrity cho các bản ghi hoặc thao tác nghiệp vụ quan trọng.  
Trong phạm vi phiên bản hiện tại, Proof of Integrity được mô phỏng bằng cơ chế hash chain và lưu trữ trong cơ sở dữ liệu.  
Mục đích của cơ chế này là hỗ trợ phát hiện việc thay đổi trái phép đối với dữ liệu hoặc lịch sử xử lý đã được ghi nhận.  
*3.2.8. BR-08 – Quản lý QR và truy xuất nguồn gốc*  
QR chỉ được hệ thống tạo sau khi Batch được Auditor Approve và chuyển sang trạng thái AUDITED.  
Các quy tắc:

- Batch UNVERIFIED không có QR.  
- Batch REJECTED không có QR.  
- Batch chỉ được tạo QR sau khi Audit thành công.  
- Mỗi Batch chỉ có một QR chính thức.  
- QR phải liên kết với một Trace ID duy nhất.  
- QR không được sử dụng để xác nhận Audit nếu Batch chưa ở trạng thái AUDITED.  
- Người tiêu dùng quét QR để truy cập Public Traceability Portal.

Thông tin hiển thị trên Public Traceability Portal phải được lấy từ dữ liệu Batch đã được hệ thống ghi nhận.  
*3.2.9. BR-09 – Phân quyền người dùng*  
Hệ thống phải áp dụng RBAC để kiểm soát quyền thực hiện nghiệp vụ.  
Các quyền cơ bản:

| Actor | Quyền nghiệp vụ chính |
| ----- | ----- |
| Farmer | Tạo/quản lý Batch, tạo Sample, bổ sung Report theo phạm vi được cấp |
| Auditor | Review, Approve, Reject Batch |
| Admin | Quản lý người dùng, vai trò, cấu hình và theo dõi hệ thống |
| Consumer | Quét QR và xem thông tin truy xuất công khai |

Quyền phải được kiểm tra tại backend/API, không chỉ kiểm soát trên giao diện.  
*3.2.10. BR-10 \- Audit Trail*  
Hệ thống phải lưu lịch sử các thao tác nghiệp vụ quan trọng, bao gồm:

- Người thực hiện;  
- Thời gian thực hiện;  
- Đối tượng được thao tác;  
- Loại thao tác;  
- Trạng thái trước và sau thao tác;  
- Lý do Reject nếu có.

Audit Trail phải hỗ trợ việc truy vết quá trình xử lý của một Batch.  
***3.3. Business Objectives – Mục tiêu cụ thể***  
***3.4. Business Scope – Phạm vi nghiệp vụ***  
***3.5. Business Success Criteria – Tiêu chí thành công***  
**4\. Business Analysis – Phân tích nghiệp vụ**  
***4.1. Stakeholder Analysis***  
***4.2. Actor Analysis***  
***4.3. As-Is Process – Quy trình hiện tại***  
***4.4. To-Be Process – Quy trình đề xuất***  
***4.5. Business Process / BPMN***  
***4.6. Business Rules – Quy tắc nghiệp vụ***  
***4.7. Permission Matrix / RBAC***  
*4.7.1. Mục đích*  
Hệ thống áp dụng cơ chế Role-Based Access Control (RBAC – Kiểm soát truy cập dựa trên vai trò) nhằm kiểm soát quyền truy cập và thao tác của người dùng trên hệ thống.  
Mỗi người dùng được gán một hoặc nhiều vai trò (Role), mỗi vai trò được liên kết với một tập hợp các quyền (Permission) tương ứng. Quyền truy cập được kiểm soát tại Backend/API, nhằm đảm bảo người dùng không thể thực hiện các thao tác vượt quá phạm vi được cấp, kể cả trong trường hợp người dùng trực tiếp gửi request đến API mà không thông qua giao diện Frontend.  
Cơ chế phân quyền được áp dụng cho các nhóm chức năng chính như:

- Quản lý người dùng;  
- Quản lý lô hàng;  
- Kiểm định lô hàng;  
- Quản lý báo cáo kiểm nghiệm;  
- Xác minh tính toàn vẹn dữ liệu;  
- Tra cứu nguồn gốc;  
- Quản trị và giám sát hệ thống.

*4.7.2. Các vai trò trong hệ thống*  
Hệ thống bao gồm các vai trò chính sau:

| Role | Tên tiếng Việt | Mô tả |
| ----- | ----- | ----- |
| **ADMIN** | Quản trị viên | Quản trị người dùng, vai trò, quyền hạn và giám sát toàn bộ hệ thống |
| **FARMER** | Nông dân | Tạo và quản lý thông tin các lô hàng do mình tạo |
| **AUDITOR** | Kiểm định viên | Kiểm tra, xác minh và phê duyệt/từ chối lô hàng |
| **PUBLIC** | Người tiêu dùng | Tra cứu thông tin nguồn gốc được công khai thông qua mã QR |

**Lưu ý:** Người tiêu dùng không nhất thiết phải đăng nhập vào hệ thống. Các chức năng tra cứu công khai có thể được cung cấp thông qua Public API với quyền PUBLIC\_TRACE\_VIEW.  
*4.7.3. Định nghĩa Permission*  
Permission là quyền thực hiện một hành động cụ thể trên hệ thống.  
a. Authentication – Xác thực

| Permission | Mô tả |
| ----- | ----- |
| AUTH\_LOGIN | Đăng nhập |
| AUTH\_LOGOUT | Đăng xuất |
| AUTH\_REFRESH\_TOKEN | Làm mới Access Token |

b. User & Role Management – Quản lý người dùng và phân quyền

| Permission | Mô tả |
| ----- | ----- |
| USER\_VIEW | Xem thông tin người dùng |
| USER\_CREATE | Tạo người dùng |
| USER\_UPDATE | Cập nhật người dùng |
| USER\_DELETE | Xóa/vô hiệu hóa người dùng |
| ROLE\_VIEW | Xem vai trò |
| ROLE\_CREATE | Tạo vai trò |
| ROLE\_UPDATE | Cập nhật vai trò |
| ROLE\_DELETE | Xóa vai trò |
| PERMISSION\_VIEW | Xem danh sách quyền |
| PERMISSION\_ASSIGN | Gán quyền cho vai trò |

c. Batch Management – Quản lý lô hàng

| Permission | Mô tả |
| ----- | ----- |
| BATCH\_CREATE | Tạo lô hàng |
| BATCH\_VIEW\_OWN | Xem lô hàng do chính mình tạo |
| BATCH\_VIEW\_ALL | Xem toàn bộ lô hàng |
| BATCH\_UPDATE\_OWN | Cập nhật lô hàng của mình |
| BATCH\_DELETE\_OWN | Xóa lô hàng của mình |
| BATCH\_STATUS\_VIEW | Xem trạng thái lô hàng |

d. Audit – Kiểm định

| Permission | Mô tả |
| ----- | ----- |
| AUDIT\_VIEW | Xem các lô hàng cần kiểm định |
| AUDIT\_REVIEW | Xem và đánh giá thông tin kiểm định |
| AUDIT\_UPLOAD\_REPORT | Tải báo cáo kiểm nghiệm |
| AUDIT\_APPROVE | Phê duyệt lô hàng |
| AUDIT\_REJECT | Từ chối lô hàng |
| AUDIT\_VIEW\_HISTORY | Xem lịch sử kiểm định |

e. Integrity – Tính toàn vẹn dữ liệu

| Permission | Mô tả |
| ----- | ----- |
| HASH\_GENERATE | Tạo mã băm SHA-256 |
| HASH\_VERIFY | Xác minh mã băm |
| PROOF\_VIEW | Xem Proof of Integrity |

f. Traceability – Truy xuất nguồn gốc

| Permission | Mô tả |
| ----- | ----- |
| QR\_GENERATE | Tạo mã QR cho lô hàng |
| PUBLIC\_TRACE\_VIEW | Tra cứu thông tin nguồn gốc công khai |

g. Administration – Quản trị hệ thống

| Permission | Mô tả |
| ----- | ----- |
| `DASHBOARD_VIEW` | Xem Admin Dashboard |
| `AUDIT_LOG_VIEW` | Xem nhật ký hoạt động |
| `SYSTEM_CONFIG_VIEW` | Xem cấu hình hệ thống |

*4.7.4. Ma trận Role – Permission*

| Permission | ADMIN | FARMER | AUDITOR | PUBLIC |
| ----- | ----- | ----- | ----- | ----- |
| AUTH\_LOGIN | ✓ | ✓ | ✓ | – |
| USER\_VIEW | ✓ | – | – | – |
| USER\_CREATE | ✓ | – | – | – |
| USER\_UPDATE | ✓ | – | – | – |
| USER\_DELETE | ✓ | – | – | – |
| ROLE\_VIEW | ✓ | – | – | – |
| ROLE\_CREATE | ✓ | – | – | – |
| ROLE\_UPDATE | ✓ | – | – | – |
| ROLE\_DELETE | ✓ | – | – | – |
| BATCH\_CREATE | ✓ | ✓ | – | – |
| BATCH\_VIEW\_OWN | ✓ | ✓ | – | – |
| BATCH\_VIEW\_ALL | ✓ | – | ✓ | – |
| BATCH\_UPDATE\_OWN | ✓ | ✓ | – | – |
| BATCH\_DELETE\_OWN | ✓ | ✓\* | – | – |
| AUDIT\_VIEW | ✓ | – | ✓ | – |
| AUDIT\_REVIEW | ✓ | – | ✓ | – |
| AUDIT\_UPLOAD\_REPORT | ✓ | – | ✓ | – |
| AUDIT\_APPROVE | ✓ | – | ✓ | – |
| AUDIT\_REJECT | ✓ | – | ✓ | – |
| AUDIT\_VIEW\_HISTORY | ✓ | – | ✓ | – |
| HASH\_GENERATE | ✓ | – | ✓ | – |
| HASH\_VERIFY | ✓ | – | ✓ | – |
| PROOF\_VIEW | ✓ | – | ✓ | – |
| QR\_GENERATE | ✓ | ✓ | – | – |
| PUBLIC\_TRACE\_VIEW | ✓ | – | – | ✓ |
| DASHBOARD\_VIEW | ✓ | – | – | – |
| AUDIT\_LOG\_VIEW | ✓ | – | – | – |

**Chú thích:**

✓: Được phép

–: Không được phép

\*: Việc xóa lô hàng phải tuân thủ Business Rule và trạng thái hiện tại của lô hàng. 

*4.7.5. Phạm vi dữ liệu (Data Scope)*

| Role | Data Scope |
| ----- | ----- |
| **ADMIN** | Toàn bộ dữ liệu trong hệ thống |
| **FARMER** | Các lô hàng do chính Farmer tạo |
| **AUDITOR** | Các lô hàng thuộc phạm vi được phân công/được phép kiểm định |
| **PUBLIC** | Chỉ dữ liệu đã được hệ thống cho phép công khai |

*4.7.6. Phân quyền theo API*

| Method | API | Permission | Role |
| ----- | ----- | ----- | ----- |
| POST | /api/v1/batches | BATCH\_CREATE | FARMER |
| GET | /api/v1/batches/my | BATCH\_VIEW\_OWN | FARMER |
| GET | /api/v1/batches | BATCH\_VIEW\_ALL | ADMIN, AUDITOR |
| GET | /api/v1/auditor/batches | AUDIT\_VIEW | AUDITOR |
| GET | /api/v1/auditor/batches/{id} | AUDIT\_REVIEW | AUDITOR |
| POST | /api/v1/auditor/batches/{id}/report | AUDIT\_UPLOAD\_REPORT | AUDITOR |
| POST | /api/v1/auditor/batches/{id}/approve | AUDIT\_APPROVE | AUDITOR |
| POST | /api/v1/auditor/batches/{id}/reject | AUDIT\_REJECT | AUDITOR |
| GET | /api/v1/auditor/batches/{id}/history | AUDIT\_VIEW\_HISTORY | AUDITOR |
| GET | /api/v1/public/trace/{batch\_code} | PUBLIC\_TRACE\_VIEW | PUBLIC |
| GET | /api/v1/admin/dashboard | DASHBOARD\_VIEW | ADMIN |

*4.7.7. Nguyên tắc kiểm tra quyền tại Backend*  
Mọi request tới API có yêu cầu xác thực phải được kiểm tra theo thứ tự: Request → Xác thực JWT (Authentication) → Xác định User → Xác định Role → Kiểm tra Permission → Kiểm tra Data Scope → Kiểm tra Business Rule → Cho phép / Từ chối.  
*4.7.8. RBAC kết hợp với trạng thái của lô hàng*  
Quyền của người dùng phải được kết hợp với trạng thái hiện tại của lô hàng (Batch Status).

*4.7.9. Ví dụ các trường hợp phân quyền*

a. Trường hợp 1 – Farmer tạo lô hàng

Farmer → POST /api/v1/batches → BATCH\_CREATE ✓ → Tạo Batch → Status \= UNVERIFIED

b. Trường hợp 2 – Farmer cố gắng phê duyệt

Farmer → POST /api/v1/auditor/batches/{id}/approve → AUDIT\_APPROVE ✗ → 403 Forbidden

c. Trường hợp 3 – Auditor phê duyệt lô hợp lệ

Auditor → AUDIT\_APPROVE ✓ → Batch \= UNVERIFIED ✓ → Lab Report ✓ → SHA-256 ✓ → Proof of Integrity ✓ → Batch \= AUDITED

d. Trường hợp 4 – Người tiêu dùng tra cứu

Consumer → Scan QR → GET /api/v1/public/trace/{batch\_code} → PUBLIC\_TRACE\_VIEW ✓ → Public Traceability Portal

**4.8. State Machine – Trạng thái lô hàng**

**4.9. Business Glossary**

# LAB TEST REPORT

**Phụ lục 1:**

**LABORATORY TEST REPORT**

**BÁO CÁO KẾT QUẢ KIỂM NGHIỆM**

I. THÔNG TIN BÁO CÁO

| Thông tin | Nội dung |
| ----- | ----- |
| **Report ID** | LTR-2026-000128 |
| **Ngày phát hành** | 28/08/2026 |
| **Ngày nhận mẫu** | 25/08/2026 |
| **Ngày kiểm nghiệm** | 25/08/2026 – 27/08/2026 |
| **Trạng thái** | FINAL |
| **Loại kiểm nghiệm** | Kiểm nghiệm chất lượng và an toàn nông sản |

II. THÔNG TIN PHÒNG THÍ NGHIỆM

**Tên đơn vị:** Trung tâm Kiểm nghiệm Nông sản ABC  
**Laboratory:** ABC Agricultural Testing Laboratory

**Mã phòng lab:** LAB-ABC-001

**Địa chỉ:** 123 Đường Nguyễn Trãi, Thanh Xuân, Hà Nội, Việt Nam

**Email:** laboratory@example.com

**Điện thoại:** (+84) 24 1234 5678

III. THÔNG TIN KHÁCH HÀNG / ĐƠN VỊ GỬI MẪU

| Thông tin | Nội dung |
| ----- | ----- |
| **Đơn vị gửi mẫu** | Hợp tác xã Nông nghiệp Xanh |
| **Mã khách hàng** | CUS-00045 |
| **Người gửi mẫu** | Nguyễn Văn An |
| **Địa chỉ** | Hà Nội, Việt Nam |
| **Mục đích kiểm nghiệm** | Đánh giá chất lượng và an toàn lô nông sản |

IV. THÔNG TIN MẪU KIỂM NGHIỆM

| Thông tin | Nội dung |
| ----- | ----- |
| **Sample ID** | SMP-2026-008721 |
| **Batch Code** | BATCH-HN-2026-0825-001 |
| **Tên sản phẩm** | Dưa lưới |
| **Product Type** | Nông sản tươi |
| **Nguồn gốc** | Hà Nội, Việt Nam |
| **Nhà sản xuất** | Hợp tác xã Nông nghiệp Xanh |
| **Ngày thu hoạch** | 23/08/2026 |
| **Khối lượng mẫu** | 2,0 kg |
| **Tình trạng mẫu khi tiếp nhận** | Nguyên vẹn, phù hợp kiểm nghiệm |
| **Phương thức lấy mẫu** | Mẫu đại diện từ lô hàng |

V. NỘI DUNG KIỂM NGHIỆM

Các chỉ tiêu dưới đây được thực hiện trên mẫu có mã **SMP-2026-008721**.

| STT | Chỉ tiêu kiểm nghiệm | Phương pháp kiểm nghiệm | Kết quả | Đơn vị | Giới hạn tham chiếu | Đánh giá |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | Dư lượng thuốc bảo vệ thực vật | Phương pháp phân tích mẫu phù hợp | Không phát hiện | mg/kg | ≤ giới hạn áp dụng | **ĐẠT** |
| 2 | Hàm lượng Nitrat (NO₃⁻) | Phương pháp phân tích hóa học | 18,4 | mg/kg | ≤ 200 | **ĐẠT** |
| 3 | Chì (Pb) | Phương pháp phân tích kim loại nặng | \< 0,010 | mg/kg | ≤ 0,10 | **ĐẠT** |
| 4 | Cadimi (Cd) | Phương pháp phân tích kim loại nặng | \< 0,005 | mg/kg | ≤ 0,05 | **ĐẠT** |
| 5 | Tổng số vi sinh vật hiếu khí | Phương pháp đếm khuẩn lạc | 1,2 × 10³ | CFU/g | ≤ 1,0 × 10⁵ | **ĐẠT** |
| 6 | Coliforms | Phương pháp định lượng vi sinh | \< 10 | CFU/g | ≤ 10² | **ĐẠT** |
| 7 | E. coli | Phương pháp định lượng vi sinh | Không phát hiện | CFU/g | Không phát hiện/giới hạn áp dụng | **ĐẠT** |
| 8 | Salmonella | Phương pháp phát hiện vi sinh | Không phát hiện | /25g | Không phát hiện | **ĐẠT** |

VI. KẾT LUẬN KIỂM NGHIỆM

Căn cứ trên kết quả phân tích các chỉ tiêu được thực hiện đối với mẫu:

**Sample ID:** SMP-2026-008721  
**Batch Code:** BATCH-HN-2026-0825-001  
**Product:** Dưa lưới

Kết quả kiểm nghiệm cho thấy các chỉ tiêu được kiểm tra **đáp ứng các giới hạn tham chiếu được áp dụng cho mục đích kiểm nghiệm của mẫu**.

KẾT LUẬN:

> **MẪU ĐẠT YÊU CẦU KIỂM NGHIỆM**

Kết luận này chỉ áp dụng cho mẫu được cung cấp và kiểm nghiệm với mã **SMP-2026-008721**.

VII. THÔNG TIN XÁC NHẬN

| Vai trò | Họ tên | Chữ ký |
| ----- | ----- | ----- |
| Người thực hiện kiểm nghiệm | Trần Minh Anh | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| Người kiểm tra kết quả | Lê Quốc Bảo | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| Người phê duyệt báo cáo | Phạm Thu Hà | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

**Ngày phê duyệt:** 28/08/2026

VIII. THÔNG TIN TOÀN VẸN TÀI LIỆU

Phần này được sử dụng để phục vụ hệ thống **Auditor Gatekeeper**.

| Trường | Giá trị |
| ----- | ----- |
| **Document Type** | Laboratory Test Report |
| **Report ID** | LTR-2026-000128 |
| **Sample ID** | SMP-2026-008721 |
| **Batch Code** | BATCH-HN-2026-0825-001 |
| **File Format** | PDF |
| **File Version** | 1.0 |
| **SHA-256** | Được hệ thống Backend tự động tính toán sau khi upload file |

**Lưu ý:** SHA-256 của báo cáo không được ghi thủ công trong tài liệu mẫu. Khi Auditor upload file PDF vào hệ thống, Backend sẽ đọc nội dung file và tự động tạo mã băm SHA-256 tương ứng.

IX. LỊCH SỬ PHIÊN BẢN

| Version | Ngày | Nội dung | Người thực hiện |
| ----- | ----- | ----- | ----- |
| 1.0 | 28/08/2026 | Phát hành báo cáo kiểm nghiệm | ABC Laboratory |

X. GHI CHÚ

1. Kết quả kiểm nghiệm chỉ áp dụng cho mẫu được cung cấp và tiếp nhận với thông tin nêu trong báo cáo.

2. Không được tự ý sao chép một phần báo cáo nếu không có sự cho phép của đơn vị phát hành.

3. Báo cáo này là **dữ liệu mẫu phục vụ kiểm thử hệ thống**, không phải chứng nhận chất lượng hoặc tài liệu kiểm nghiệm có giá trị pháp lý.

4. Các giới hạn tham chiếu và phương pháp kiểm nghiệm trong tài liệu mẫu được xây dựng nhằm phục vụ việc mô phỏng nghiệp vụ của hệ thống.

5. Trong môi trường thực tế, các chỉ tiêu, phương pháp, giới hạn và thông tin pháp lý phải được thay thế bằng dữ liệu do phòng thí nghiệm có thẩm quyền cung cấp.

---

**END OF REPORT**

**ABC AGRICULTURAL TESTING LABORATORY**

*Sample document for system testing purposes only.*

# NOTE

Được. Và **đây mới là vấn đề cốt lõi của hệ thống**: không chỉ chứng minh “có một báo cáo kiểm nghiệm”, mà phải chứng minh **báo cáo đó đúng với chính lô hàng đang được đưa ra thị trường**.

Nếu không thiết kế chỗ này chặt, đúng như bạn nói:

> Nông dân có 2 lô A và B → chỉ mang A đi kiểm nghiệm → A đạt → nhưng lại lấy B bán ra thị trường và gắn thông tin/QR của A.

Hệ thống phần mềm **không thể tự giải quyết gian lận vật lý 100%** nếu không có cơ chế liên kết vật lý giữa mẫu kiểm nghiệm và hàng hóa. Vì vậy quy trình phải thiết kế **từ lúc tạo lô → lấy mẫu → kiểm nghiệm → đóng gói → xuất hàng → người tiêu dùng**, chứ không chỉ từ PDF → QR.

---

# **1\. Trước hết, hiểu hệ thống này như thế này**

Có **5 bên**:

NÔNG DÂN  
   ↓  
ĐƠN VỊ/PHÒNG LAB  
   ↓  
AUDITOR  
   ↓  
ĐƠN VỊ ĐÓNG GÓI / XUẤT HÀNG  
   ↓  
NGƯỜI TIÊU DÙNG

Trong đó:

* **Farmer**: tạo và cung cấp lô hàng.  
* **Lab**: lấy mẫu và kiểm nghiệm.  
* **Auditor**: kiểm tra hồ sơ \+ kết quả kiểm nghiệm \+ xác nhận lô.  
* **Đơn vị đóng gói/xuất hàng**: đưa đúng lô đã được xác nhận ra thị trường.  
* **Consumer**: quét QR để kiểm tra.

Nếu project của bạn **không có một Actor riêng cho “đóng gói/xuất hàng”**, thì có thể coi chức năng này thuộc **Farmer hoặc Company**, nhưng nghiệp vụ vẫn phải tồn tại.

---

# **2\. Quy trình từ ĐẦU đến CUỐI**

## **BƯỚC 1 — Nông dân tạo lô hàng**

Ví dụ nông dân Nguyễn Văn A có:

> 1.000 kg dưa lưới.

Anh A vào hệ thống tạo:

Batch Code: BATCH-001  
Product: Dưa lưới  
Farm: Trang trại A  
Harvest Date: 01/09/2026  
Quantity: 1.000 kg

Status \= UNVERIFIED

**Quan trọng:**

Ngay lúc này hệ thống đã tạo ra **một định danh duy nhất cho lô**.

BATCH-001

Từ đây về sau, mọi thứ liên quan đến lô này đều phải gắn với `BATCH-001`.

---

# **3\. BƯỚC 2 — Lô hàng được chia mẫu để kiểm nghiệm**

Đây là chỗ mình muốn **sửa cách hiểu trước đó**.

Không phải:

> “Nông dân upload một cái PDF rồi bảo đây là lô A.”

Mà phải có **Sample ID**.

Ví dụ:

BATCH-001  
1.000 kg dưa lưới  
       │  
       ├── Sample 001 → gửi Lab  
       │  
       └── 1.000 kg còn lại → niêm phong/chờ kiểm định

Hệ thống tạo:

Batch:  
BATCH-001

Sample:  
SAMPLE-001

Sample → BATCH-001

Như vậy:

> **SAMPLE-001 là mẫu được lấy từ BATCH-001.**

---

# **4\. BƯỚC 3 — Lab nhận mẫu**

Phòng Lab nhận:

SAMPLE-001  
↓  
thuộc  
↓  
BATCH-001

Lab kiểm nghiệm mẫu.

Ví dụ:

* dư lượng thuốc bảo vệ thực vật  
* kim loại nặng  
* vi sinh  
* nitrat...

Sau khi kiểm nghiệm xong, Lab tạo:

Laboratory Test Report

Report ID: LTR-001  
Sample ID: SAMPLE-001  
Batch Code: BATCH-001

Result: PASS

Điểm cực kỳ quan trọng:

> **Lab Report không chỉ ghi “Dưa lưới đạt”. Nó phải gắn với Sample ID và Batch ID.**

---

# **5\. BƯỚC 4 — Báo cáo được đưa vào hệ thống**

Auditor nhận báo cáo:

LTR-001.pdf

Upload lên hệ thống.

Backend kiểm tra:

LTR-001  
   ↓  
SAMPLE-001  
   ↓  
BATCH-001

Database cũng đang có:

SAMPLE-001 → BATCH-001

Nếu report nói:

SAMPLE-001 → BATCH-002

→ **Không khớp → từ chối.**

---

# **6\. BƯỚC 5 — Backend tạo SHA-256**

Backend lấy file:

LTR-001.pdf

Tính:

SHA-256  
↓  
ABC123XYZ...

Lưu:

BATCH-001  
    │  
    ├── SAMPLE-001  
    │  
    ├── LTR-001  
    │  
    ├── SHA-256  
    │  
    └── Audit Proof

Như vậy về mặt dữ liệu, bạn đã tạo được **chuỗi liên kết**.

---

# **7\. BƯỚC 6 — Auditor kiểm định**

Auditor vào hệ thống và thấy:

BATCH-001

Product: Dưa lưới  
Quantity: 1.000 kg

Sample:  
SAMPLE-001

Lab Report:  
LTR-001

Result:  
PASS

Auditor kiểm tra:

* Batch có tồn tại?  
* Sample có thuộc Batch?  
* Report có đúng Sample?  
* Report có đúng Batch?  
* File có hợp lệ?  
* Hash có hợp lệ?  
* Kết quả có đạt yêu cầu?  
* Các thông tin khác có phù hợp?

Nếu tất cả hợp lệ:

APPROVE

Hệ thống:

BATCH-001  
UNVERIFIED  
     ↓  
AUDITED  
---

# **8\. Nhưng câu hỏi quan trọng nhất của bạn vẫn còn**

Bạn hỏi:

> **“Tôi kiểm nghiệm BATCH-001 nhưng sau đó lấy BATCH-002 bán thì sao?”**

Đúng.

**Nếu chỉ có QR thì vẫn chưa giải quyết được.**

Ví dụ:

BATCH-001 → ĐẠT  
BATCH-002 → CHƯA KIỂM NGHIỆM

Nông dân lấy hàng BATCH-002.

Dán QR của BATCH-001 lên.

Người tiêu dùng quét:

QR  
 ↓  
BATCH-001  
 ↓  
AUDITED

→ Người tiêu dùng tưởng hàng BATCH-002 là BATCH-001.

**Đây là gian lận vật lý.**

---

# **9\. Vì vậy cần một bước cực kỳ quan trọng: ĐÓNG GÓI / NIÊM PHONG**

Sau khi Auditor approve:

BATCH-001  
AUDITED

hệ thống cho phép tạo **Trace ID / QR ID**.

Ví dụ:

Batch:  
BATCH-001

Trace ID:  
TRC-8F92A1

QR:

┌───────────────┐  
│ ███ █ ███ ███ │  
│ █ █ ███ █ █ █ │  
│ ███ █ ███ ███ │  
│               │  
│ TRC-8F92A1    │  
└───────────────┘

QR này được **gắn với hàng hóa của BATCH-001**.

---

# **10\. Nhưng QR vẫn có thể bị bóc ra\!**

Chính xác.

Nếu QR là **tem giấy thông thường**, nông dân vẫn có thể:

> bóc QR BATCH-001 → dán lên BATCH-002.

Vì vậy nếu muốn chống gian lận tốt hơn, requirement **Optional NFC NTAG424 DNA** của project bắt đầu có ý nghĩa.

---

# **11\. Nếu dùng NFC chống giả**

Thay vì chỉ:

QR

có thể dùng:

QR \+ NFC Dynamic Authentication

Mỗi sản phẩm/lô được gắn một **NFC tag duy nhất**.

Ví dụ:

BATCH-001  
    ↓  
NFC TAG-001  
    ↓  
Dynamic SUN MAC

Khi người tiêu dùng chạm/đọc tag:

NFC  
 ↓  
Dynamic authentication  
 ↓  
Backend  
 ↓  
TAG-001  
 ↓  
BATCH-001  
 ↓  
AUDITED

Nếu kẻ gian lấy tem/tag từ BATCH-001 để dùng lại, hệ thống có thể phát hiện các hành vi xác thực không phù hợp tùy cách triển khai.

**Đây là lớp chống giả vật lý**, khác với SHA-256.

---

# **12\. Nhưng còn một vấn đề nữa: 1.000 kg chia thành 100 gói thì sao?**

Đây là chỗ BA phải làm rõ **Batch vs Package**.

Ví dụ:

BATCH-001  
1.000 kg  
      ↓  
┌─────┬─────┬─────┬─────┐  
│ 1kg │ 1kg │ 1kg │ ... │  
└─────┴─────┴─────┴─────┘

Không thể tạo 1 QR rồi dán đại lên tất cả nếu muốn truy xuất từng đơn vị.

Có thể thiết kế:

BATCH-001  
   │  
   ├── PACKAGE-001  
   ├── PACKAGE-002  
   ├── PACKAGE-003  
   └── ...

Mỗi package có:

Package ID  
    ↓  
QR / NFC  
    ↓  
Batch ID

Ví dụ:

PACKAGE-0001  
      ↓  
BATCH-001  
      ↓  
AUDITED  
---

# **13\. Và phải có kiểm soát số lượng**

Đây lại là một Business Rule cực quan trọng.

Nếu:

BATCH-001  
1.000 kg

đã được kiểm định.

Không thể để hệ thống cho phép người dùng tạo:

2.000 kg

sản phẩm đã kiểm định từ Batch-001.

Phải có:

Certified Quantity \= 1.000 kg

và:

Total Released Quantity ≤ Certified Quantity

Ví dụ:

BATCH-001  
Certified: 1.000 kg

Released:  
200 kg  
\+ 300 kg  
\+ 500 kg  
──────────  
\= 1.000 kg

Đã hết.

Không được tạo thêm:

\+ 500 kg

và gọi đó là hàng đã kiểm định.

---

# **14\. Vậy quy trình hoàn chỉnh nên là**

                FARMER  
                    │  
                    │ Tạo lô  
                    ▼  
              ┌─────────────┐  
              │   BATCH     │  
              │  BATCH-001  │  
              │ UNVERIFIED  │  
              └──────┬──────┘  
                     │  
                 Lấy mẫu  
                     │  
                     ▼  
              ┌─────────────┐  
              │   SAMPLE    │  
              │ SAMPLE-001  │  
              └──────┬──────┘  
                     │  
                     ▼  
                  LAB  
                     │  
              Kiểm nghiệm  
                     │  
                     ▼  
           Laboratory Report  
                LTR-001  
                     │  
                     │  
                     ▼  
                AUDITOR  
                     │  
          ┌──────────┴──────────┐  
          │                     │  
       REJECT                APPROVE  
          │                     │  
          ▼                     ▼  
       REJECTED              AUDITED  
                                │  
                       SHA-256 \+ Proof  
                                │  
                                ▼  
                         ĐÓNG GÓI / XUẤT  
                                │  
                       ┌────────┴────────┐  
                       ▼                 ▼  
                    QR / NFC        Package ID  
                       │                 │  
                       └────────┬────────┘  
                                ▼  
                           THỊ TRƯỜNG  
                                │  
                                ▼  
                            CONSUMER  
                                │  
                             Scan QR  
                                │  
                                ▼  
                      PUBLIC TRACE PORTAL  
                                │  
                                ▼  
                    Backend kiểm tra Batch  
                                │  
                                ▼  
                      AUDITED / VALID  
---

# **15\. Như vậy chống gian lận bằng nhiều lớp**

Đây mới là kiến trúc nghiệp vụ mình nghĩ project của bạn đang hướng tới:

| Lớp | Cơ chế | Giải quyết gì? |
| ----- | ----- | ----- |
| **1\. Batch Identity** | Batch ID duy nhất | Xác định lô nào |
| **2\. Sample Identity** | Sample ID | Xác định mẫu lấy từ lô nào |
| **3\. Lab Report** | Report ID \+ Sample ID \+ Batch ID | Chứng minh mẫu/lô đã kiểm nghiệm |
| **4\. SHA-256** | Hash file | Phát hiện báo cáo bị thay đổi |
| **5\. Auditor** | Independent approval | Không cho Farmer tự xác nhận |
| **6\. State Machine** | UNVERIFIED → AUDITED | Kiểm soát vòng đời |
| **7\. Quantity Control** | Certified/Released Quantity | Không cho “nhân” hàng đạt |
| **8\. QR** | Trace ID → Batch/Package | Truy xuất đúng bản ghi |
| **9\. NFC** | Dynamic authentication | Chống giả tem vật lý tốt hơn |

---

# **16\. Tuy nhiên phải nói thật một điều**

**Không có hệ thống phần mềm nào chỉ bằng QR \+ SHA-256 mà đảm bảo 100% rằng “thùng hàng vật lý này chính là thùng hàng đã được Lab kiểm nghiệm”.**

Muốn giải quyết bài toán đó thực sự, phải có **chain of custody – chuỗi kiểm soát vật lý**:

Lấy mẫu  
 ↓  
Niêm phong  
 ↓  
Kiểm nghiệm  
 ↓  
Đối chiếu  
 ↓  
Đóng gói  
 ↓  
Gắn tem định danh  
 ↓  
Xuất hàng

Nếu project của bạn chỉ làm **phần mềm**, thì nên xác định rõ phạm vi:

> **Hệ thống đảm bảo tính nhất quán và khả năng xác minh của thông tin số liên quan đến lô hàng; việc kiểm soát hàng hóa vật lý cần được hỗ trợ bằng quy trình lấy mẫu, niêm phong và gắn định danh/tem chống giả.**

Đây là câu **rất quan trọng để đưa vào Business Analysis**, vì nó xác định giới hạn của hệ thống.

---

## **Và mình nghĩ requirement hiện tại của project bạn đang thiếu 4 thứ**

Nếu bạn muốn hệ thống thực sự giải quyết đúng vấn đề bạn vừa nêu, mình sẽ **bổ sung vào requirement**:

**① Sample Management**

Batch → Sample → Lab Report

**② Chain of Custody**

Lấy mẫu → kiểm nghiệm → phê duyệt → đóng gói → xuất hàng

**③ Quantity Control**

Certified Quantity ≥ Released Quantity

**④ Package/Label Identity**

Batch → Package → QR/NFC → Consumer

Nếu chưa có 4 cái này mà chỉ có **Farmer → Lab Report → Auditor → QR**, thì đúng như bạn nghi ngờ: **vẫn còn một lỗ hổng rất lớn cho việc “kiểm nghiệm lô A nhưng bán lô B”.**

Và **đây chính là thứ bạn nên đem hỏi PM/PO/BA lead của project trước khi tiếp tục viết SRS**, vì nó ảnh hưởng trực tiếp đến Actor, Business Process, Database, API, RBAC, User Story và cả thiết kế QR/NFC.
