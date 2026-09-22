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

- Quản lý người dùng và phân quyền.  
- Quản lý thông tin nông dân.  
- Quản lý lô hàng.  
- Quản lý mẫu kiểm nghiệm.  
- Quản lý Laboratory Test Report.  
- Upload và lưu trữ báo cáo kiểm nghiệm.  
- Tính toán và xác minh SHA-256.  
- Quy trình Auditor kiểm tra và phê duyệt.  
- Quản lý trạng thái lô hàng.  
- Proof of Integrity bằng chuỗi hash lưu trong Database.  
- Sinh và quản lý QR Code.  
- Cổng tra cứu nguồn gốc công khai.  
- Admin Dashboard.  
- Logging và Audit Trail.

Ngoài phạm vi / tùy chọn:

- Triển khai Smart Contract thực tế trên Ethereum Testnet.  
- Kết nối Web3.  
- Tích hợp NFC NTAG424 DNA và Dynamic SUN MAC.  
- Tích hợp trực tiếp với hệ thống của phòng thí nghiệm.  
- Tự động kiểm nghiệm nông sản.

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

***2.9. Ràng buộc và giả định***

- Ràng buộc:  
* Mỗi Batch phải có một định danh duy nhất.  
* Batch mới tạo phải có trạng thái UNVERIFIED.  
* Farmer không được tự chuyển Batch sang AUDITED.  
* Chỉ Auditor có quyền phê duyệt Batch.  
* Laboratory Test Report phải được liên kết với đúng Batch/Sample.  
* SHA-256 phải được Backend tự động tạo khi tiếp nhận báo cáo.  
* QR chỉ được sử dụng để xác nhận/truy xuất Batch đã được hệ thống phê duyệt.  
* Quyền truy cập API phải được kiểm tra tại Backend.  
* Proof of Integrity được lưu trong Database trong phiên bản hiện tại.  
* Blockchain là chức năng tùy chọn.  
* Hệ thống không trực tiếp thực hiện kiểm nghiệm vật lý nông sản.  
- Giả định:  
* Thông tin do phòng Lab cung cấp là hợp lệ.  
* Mẫu kiểm nghiệm được lấy từ đúng Batch và được quản lý theo quy trình của đơn vị kiểm nghiệm.  
* Auditor là người có thẩm quyền thực hiện việc thẩm định.  
* Thông tin Batch được nhập vào hệ thống là chính xác.  
* Quy trình đóng gói và gắn QR/NFC được thực hiện theo quy trình của doanh nghiệp.  
* Hệ thống phần mềm chịu trách nhiệm xác minh tính nhất quán của dữ liệu số, trong khi việc bảo đảm hàng hóa vật lý đúng với Batch cần có quy trình kiểm soát vật lý tương ứng.

**3\. Business Requirements \- Yêu cầu nghiệp vụ**  
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

***3.2. Business Requirements \- Yêu cầu nghiệp vụ***  
*3.2.1. BR-01 \- Quản lý Batch*  
Hệ thống phải cho phép Farmer tạo và quản lý Batch của mình.  
Khi tạo Batch:

- Batch Code/Batch ID phải do hệ thống sinh và đảm bảo duy nhất.  
- Farmer phải cung cấp các thông tin bắt buộc của Batch, bao gồm thông tin sản phẩm, ngày sản xuất/thu hoạch, số lượng, đơn vị và nguồn gốc.  
- Batch mới phải có trạng thái mặc định là UNVERIFIED.  
- Farmer không được tự đặt trạng thái Batch thành AUDITED.

Farmer không được phép chỉnh sửa hoặc xóa Batch sau khi đã tạo.  
*3.2.2. BR-02 \- Quản lý Sample*  
Hệ thống phải cho phép tạo Sample thuộc một Batch cụ thể.

- Sample ID phải được hệ thống tạo và đảm bảo duy nhất.  
- Mỗi Sample chỉ thuộc về một Batch.  
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
***3.3. Business Objectives \- Mục tiêu cụ thể***  
Để cụ thể hóa các mục tiêu nghiệp vụ, hệ thống hướng tới các kết quả sau:

- **BO-01:** 100% Batch được tạo mới phải bắt đầu ở trạng thái UNVERIFIED.  
- **BO-02:** 100% Batch chuyển sang AUDITED phải được xử lý bởi Auditor có quyền.  
- **BO-03:** Không cho phép Approve Batch khi thiếu Laboratory Test Report, SHA-256 hoặc Proof of Integrity.  
- **BO-04:** Đảm bảo Report được liên kết với đúng Sample và Sample thuộc đúng Batch trước khi Audit.  
- **BO-05:** Không cho phép Farmer tự thay đổi trạng thái Batch thành AUDITED.  
- **BO-06:** Batch bị Reject phải có lý do và có khả năng được Farmer bổ sung/sửa đổi để gửi kiểm định lại.  
- **BO-07:** Chỉ Batch ở trạng thái AUDITED mới được tạo QR.  
- **BO-08:** Mỗi Batch đã được Audit có một QR/Trace ID duy nhất để phục vụ truy xuất.  
- **BO-09:** Các thao tác Audit quan trọng phải có lịch sử trong Audit Trail.  
- **BO-10:** Các API nghiệp vụ phải kiểm tra quyền truy cập theo vai trò người dùng.

***3.4. Business Scope \- Phạm vi nghiệp vụ***  
*3.4.1. In-Scope – Trong phạm vi*  
Phạm vi nghiệp vụ của hệ thống bao gồm:  
1\. Quản lý Batch

- Tạo Batch;  
- Theo dõi trạng thái Batch.

2\. Quản lý Sample

- Tạo Sample;  
- Liên kết Sample với Batch;

3\. Quản lý Laboratory Test Report

- Upload Report;  
- Liên kết Report với Sample/Batch;  
- Kiểm tra tính hợp lệ của Report;  
- Tính và lưu SHA-256.  
  4\. Auditor Gatekeeper  
- Review Batch;  
- Review Sample và Report;  
- Approve;  
- Reject;  
- Review lại Batch sau khi Farmer bổ sung thông tin.

5\. Integrity Management

- SHA-256;  
- Proof of Integrity;  
- Audit Trail.

6\. QR & Traceability

- Tạo QR sau khi Batch được AUDITED;  
- Tạo Trace ID;  
- Tra cứu thông tin Batch thông qua QR;  
- Public Traceability Portal.

7\. User & Access Management

- Authentication;  
- RBAC;  
- Quản lý quyền truy cập.

8\. Administration

- Admin Dashboard;  
- Quản lý người dùng;  
- Theo dõi hoạt động hệ thống.

*3.4.2. Out-of-Scope – Ngoài phạm vi*  
Các nội dung sau không thuộc phạm vi bắt buộc của phiên bản hiện tại:

- Thực hiện kiểm nghiệm vật lý đối với sản phẩm tại phòng thí nghiệm.  
- Tự động điều khiển hoặc quản lý thiết bị phòng thí nghiệm.  
- Tích hợp trực tiếp với hệ thống của phòng thí nghiệm.  
- Triển khai Smart Contract thực tế trên Ethereum.  
- Xử lý giao dịch Web3 thực tế.  
- Triển khai NFC NTAG424 DNA và Dynamic SUN MAC trong phiên bản cơ bản.  
- Kiểm soát vật lý toàn bộ quá trình vận chuyển và đóng gói sản phẩm.

Blockchain và NFC có thể được xem là các hướng mở rộng trong tương lai.  
*3.5. Business Success Criteria \- Tiêu chí thành công*  
Hệ thống được xem là đáp ứng mục tiêu nghiệp vụ khi đạt được các tiêu chí sau:

| ID | Tiêu chí thành công | Điều kiện đạt |
| ----- | ----- | ----- |
| SC-01 | Quản lý Batch | Farmer có thể tạo và quản lý Batch theo đúng trạng thái được phép |
| SC-02 | Kiểm soát trạng thái | Batch mới luôn ở UNVERIFIED và Farmer không thể tự chuyển sang AUDITED |
| SC-03 | Liên kết dữ liệu | Batch, Sample và Laboratory Test Report được liên kết chính xác |
| SC-04 | Kiểm định | Chỉ Auditor có quyền mới có thể Approve/Reject |
| SC-05 | Điều kiện Approve | Không thể Approve khi thiếu Report, SHA-256 hoặc Proof of Integrity |
| SC-06 | Reject & Re-review | Batch bị Reject có lý do và Farmer có thể sửa/bổ sung để gửi review lại |
| SC-07 | Tính toàn vẹn | Hệ thống có thể phát hiện Report bị thay đổi thông qua SHA-256 |
| SC-08 | QR | Chỉ Batch AUDITED mới được tạo QR |
| SC-09 | Truy xuất | Người tiêu dùng có thể quét QR và xem thông tin Batch công khai |
| SC-10 | Phân quyền | Người dùng không thể thực hiện nghiệp vụ vượt quá quyền được cấp |
| SC-11 | Audit Trail | Các thao tác Audit quan trọng được lưu và có thể truy vết |
| SC-12 | Quản trị | Admin có thể quản lý người dùng, quyền và theo dõi hoạt động hệ thống |

**4\. Business Analysis \- Phân tích nghiệp vụ**  
***4.1. Stakeholder Analysis***  
Stakeholder là các cá nhân, tổ chức hoặc nhóm có liên quan trực tiếp hoặc gián tiếp đến hoạt động quản lý, kiểm định và truy xuất nguồn gốc của Batch. 

| Stakeholder | Vai trò / Mối quan tâm | Nhu cầu chính | Mức độ tham gia |
| ----- | ----- | ----- | ----- |
| Farmer | Tạo và cung cấp thông tin về Batch | Tạo Batch, quản lý Sample, cung cấp hồ sơ kiểm nghiệm và theo dõi kết quả Audit | Cao |
| Laboratory | Thực hiện kiểm nghiệm sản phẩm | Thực hiện kiểm nghiệm và cung cấp Laboratory Test Report | Trung bình |
| Auditor | Kiểm tra và xác nhận tính hợp lệ của Batch | Tạo Sample, kiểm tra Batch, Sample, Report, SHA-256, Proof và Approve/Reject | Rất cao |
| Company / Operator | Quản lý hoạt động sản xuất và lưu thông sản phẩm | Theo dõi Batch, kiểm soát quy trình và đảm bảo sản phẩm đủ điều kiện lưu thông | Cao |
| System Administrator | Quản trị hệ thống | Quản lý tài khoản, vai trò, quyền truy cập và theo dõi hoạt động | Cao |
| Consumer | Người sử dụng thông tin truy xuất | Kiểm tra nguồn gốc, trạng thái kiểm định và thông tin sản phẩm thông qua QR | Thấp |
| Packaging / Release Staff | Đóng gói và đưa sản phẩm ra thị trường | Sử dụng thông tin Batch đã được Audit để thực hiện đóng gói và gắn QR | Trung bình |

**4.2. Actor Analysis**  
Actor là đối tượng trực tiếp tương tác với hệ thống để thực hiện một hoặc nhiều chức năng.  
*4.2.1. Farmer*  
Mục đích: Quản lý các Batch do mình tạo.  
Các nghiệp vụ chính:

- Đăng nhập hệ thống.  
- Tạo Batch.  
- Tạo một hoặc nhiều Sample thuộc Batch.  
- Upload/bổ sung Laboratory Test Report theo quy trình.  
- Xem trạng thái Audit.  
- Xem lý do Reject.

**Giới hạn quyền:**

- Không được tự chuyển Batch sang AUDITED.  
- Không được Approve hoặc Reject Batch.  
- Không được sửa trực tiếp Batch đã AUDITED.  
- Không được tạo QR cho Batch.

*4.2.2. Laboratory*  
Mục đích: Thực hiện kiểm nghiệm và cung cấp kết quả kiểm nghiệm.  
Trong phiên bản cơ bản, Laboratory có thể được xem là external stakeholder, không nhất thiết phải đăng nhập trực tiếp vào hệ thống.  
Quy trình:

Nếu trong phiên bản tương lai Laboratory được tích hợp trực tiếp vào hệ thống, có thể bổ sung Actor với các quyền như:

- Tiếp nhận Sample;  
- Upload Laboratory Test Report;  
- Cập nhật trạng thái kiểm nghiệm;  
- Tra cứu Sample được giao.

*4.2.3. Auditor*  
Mục đích: Kiểm tra và xác nhận Batch trước khi được đưa vào trạng thái đã kiểm định.  
Auditor có quyền:

- Xem Batch được gửi kiểm định.  
- Upload Laboratory Test Report  
- Xem Sample liên quan.  
- Xem Laboratory Test Report.  
- Kiểm tra sự tương ứng giữa Batch – Sample – Report.  
- Kiểm tra SHA-256.  
- Kiểm tra Proof of Integrity.  
- Approve Batch.  
- Reject Batch.  
- Ghi nhận lý do Reject.  
- Xem lịch sử Audit.

Điều kiện Approve: (Laboratory Test Report hợp lệ) AND (Sample thuộc đúng Batch) AND (Report thuộc đúng Sample/Batch) AND (SHA-256 hợp lệ) AND (Proof of Integrity hợp lệ)  
*4.2.4. System Administrator*  
Mục đích: Quản trị và duy trì hoạt động của hệ thống.  
Admin có quyền:

- Quản lý tài khoản người dùng.  
- Tạo/chỉnh sửa/vô hiệu hóa tài khoản.  
- Gán Role.  
- Quản lý quyền truy cập.  
- Theo dõi Audit Trail.  
- Theo dõi trạng thái hoạt động của hệ thống.  
- Quản lý các cấu hình hệ thống trong phạm vi được cấp.

Admin không thay thế vai trò Auditor trong nghiệp vụ kiểm định. Việc có quyền quản trị hệ thống không đồng nghĩa với việc được tự động Approve Batch.  
*4.2.5. Consumer*  
Mục đích: Kiểm tra thông tin truy xuất nguồn gốc của sản phẩm.  
Consumer không cần tài khoản trong phiên bản cơ bản.  
Quy trình:

Consumer có thể xem các thông tin công khai như:

- Tên sản phẩm;  
- Batch Code;  
- Nguồn gốc;  
- Ngày sản xuất/thu hoạch;  
- Trạng thái kiểm định;  
- Thông tin kiểm nghiệm được công khai;  
- Thông tin truy xuất liên quan.

Consumer không có quyền:

- Tạo Batch;  
- Chỉnh sửa dữ liệu;  
- Approve/Reject;  
- Thay đổi trạng thái;  
- Tạo QR.

*4.2.6. Packaging / Release Staff*  
Mục đích: Thực hiện đóng gói và đưa Batch đã được kiểm định vào lưu thông.  
Actor này có thể được triển khai trong phiên bản mở rộng.  
Nghiệp vụ:

- Tiếp nhận Batch đã AUDITED.  
- Xác định số lượng được phép đưa vào lưu thông.  
- Thực hiện đóng gói.  
- Gắn QR tương ứng.  
- Chuyển Batch/Package sang trạng thái Release.

Actor này không được:

- Approve Batch;  
- Thay đổi kết quả kiểm nghiệm;  
- Tạo QR trước khi Batch được Audit.

***4.3. As-Is Process \- Quy trình hiện tại***  
*4.3.1. Quy trình hiện tại*  
![][image2]  
Thông tin có thể được lưu trữ tại nhiều nơi khác nhau như:

- File PDF;  
- Email;  
- Hồ sơ giấy;  
- Excel;  
- Các hệ thống riêng lẻ.

Do chưa có một cơ chế liên kết tập trung và xuyên suốt giữa Batch – Sample – Report – Audit nên quá trình xác minh có thể phụ thuộc nhiều vào việc đối chiếu thủ công.  
*4.3.2. Các vấn đề của As-Is Process*  
Vấn đề 1 \- Thông tin phân tán  
Thông tin Batch, Sample và Laboratory Test Report có thể được lưu trữ ở các nguồn khác nhau.  
Điều này làm tăng thời gian tìm kiếm và đối chiếu thông tin.  
Vấn đề 2 \- Liên kết Batch và Report chưa chặt chẽ  
Nếu Report chỉ được lưu dưới dạng file độc lập, việc xác định Report thuộc chính xác Batch nào có thể phụ thuộc vào thông tin trên tài liệu hoặc thao tác của người dùng.  
Vấn đề 3 \- Nguy cơ sử dụng sai Report  
Có thể xảy ra tình huống: Batch A → Sample A → Lab Test Report A nhưng trong quá trình quản lý lại sử dụng Report A cho Batch B.  
Nếu không có cơ chế kiểm tra quan hệ dữ liệu tự động, việc phát hiện sai lệch sẽ khó khăn hơn.  
Vấn đề 4 \- Khó kiểm tra tính toàn vẹn của tài liệu  
Nếu Laboratory Test Report được lưu dưới dạng file thông thường, việc phát hiện file đã bị thay đổi sau khi tiếp nhận sẽ khó khăn nếu không có cơ chế kiểm tra Integrity.  
Vấn đề 5 \- Kiểm soát quyền hạn chưa tập trung  
Nếu quy trình phê duyệt được thực hiện thông qua email, file hoặc trao đổi thủ công, khó đảm bảo rằng chỉ người có thẩm quyền mới thực hiện được thao tác Approve.  
Vấn đề 6 \- Khó truy vết lịch sử xử lý  
Việc xác định:

- Ai đã kiểm tra?  
- Kiểm tra lúc nào?  
- Đã Reject bao nhiêu lần?  
- Vì sao Reject?  
- Ai đã thay đổi thông tin?

có thể khó khăn nếu không có Audit Trail tập trung.  
Vấn đề 7 \- Consumer khó xác minh  
Consumer có thể không có một phương thức thống nhất để kiểm tra thông tin Batch và trạng thái kiểm định của sản phẩm.  
***4.4. To-Be Process \- Quy trình đề xuất***  
![][image3]  
***4.5. Business Process / BPMN***  
***4.6. Business Rules \- Quy tắc nghiệp vụ***  
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
| BATCH\_STATUS\_VIEW | Xem trạng thái lô hàng |

*d. Sample Management – Quản lý mẫu kiểm nghiệm*

| Permission | Mô tả |
| ----- | ----- |
| SAMPLE\_CREATE | Tạo mẫu kiểm nghiệm thuộc lô hàng |
| SAMPLE\_VIEW\_OWN | Xem mẫu kiểm nghiệm thuộc lô hàng |
| SAMPLE\_VIEW\_ALL | Xem toàn bộ mẫu kiểm nghiệm |
| SAMPLE\_UPDATE\_OWN | Cập nhật mẫu kiểm nghiệm |
| SAMPLE\_DELETE\_OWN | Xóa mẫu kiểm nghiệm |

*e. Audit – Kiểm định*

| Permission | Mô tả |
| ----- | ----- |
| AUDIT\_VIEW | Xem các lô hàng cần kiểm định |
| AUDIT\_REVIEW | Xem và đánh giá thông tin kiểm định |
| AUDIT\_UPLOAD\_REPORT | Tải báo cáo kiểm nghiệm |
| AUDIT\_APPROVE | Phê duyệt lô hàng |
| AUDIT\_REJECT | Từ chối lô hàng |
| AUDIT\_VIEW\_HISTORY | Xem lịch sử kiểm định |

f. Integrity – Tính toàn vẹn dữ liệu

| Permission | Mô tả |
| ----- | ----- |
| HASH\_GENERATE | Tạo mã băm SHA-256 |
| HASH\_VERIFY | Xác minh mã băm |
| PROOF\_VIEW | Xem Proof of Integrity |

g. Traceability – Truy xuất nguồn gốc

| Permission | Mô tả |
| ----- | ----- |
| QR\_GENERATE | Tạo mã QR cho lô hàng |
| PUBLIC\_TRACE\_VIEW | Tra cứu thông tin nguồn gốc công khai |

h. Administration – Quản trị hệ thống

| Permission | Mô tả |
| ----- | ----- |
| DASHBOARD\_VIEW | Xem Admin Dashboard |
| AUDIT\_LOG\_VIEW | Xem nhật ký hoạt động |
| SYSTEM\_CONFIG\_VIEW | Xem cấu hình hệ thống |

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
| SAMPLE\_CREATE | ✓ | – | ✓ | – |
| SAMPLE\_VIEW\_OWN | ✓ | – | ✓ | – |
| SAMPLE\_VIEW\_ALL | ✓ | – | ✓ | – |
| SAMPLE\_UPDATE\_OWN | ✓ | – | ✓ | – |
| SAMPLE\_DELETE\_OWN | ✓ | – | ✓ | – |
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
***4.8. State Machine – Trạng thái lô hàng***  
***4.9. Business Glossary***  
**5\.**  
**5.1. Epic**  
Epic là nhóm chức năng nghiệp vụ lớn, bao quát một mục tiêu hoặc một nhóm năng lực chính của hệ thống.

| Epic ID | Epic | Mô tả |
| ----- | ----- | ----- |
| EP01 | Authentication & Authorization | Quản lý đăng nhập, xác thực và phân quyền người dùng |
| EP02 | Batch Management | Quản lý thông tin và vòng đời của Batch |
| EP03 | Sample Management | Quản lý Sample thuộc Batch |
| EP04 | Laboratory Test Report | Tiếp nhận và quản lý Laboratory Test Report |
| EP05 | Auditor Gatekeeper | Kiểm tra, Approve/Reject Batch |
| EP06 | Data Integrity & Proof | Đảm bảo tính toàn vẹn của dữ liệu bằng SHA-256 và Proof of Integrity |
| EP07 | QR & Traceability | Tạo QR và cung cấp khả năng truy xuất nguồn gốc |
| EP08 | Public Traceability Portal | Cho phép Consumer tra cứu thông tin công khai |
| EP09 | Administration & Audit Trail | Quản trị hệ thống và theo dõi lịch sử hoạt động |

***5.2. Feature***  
Feature là chức năng cụ thể thuộc một Epic, cung cấp một năng lực có ý nghĩa cho người sử dụng hoặc hệ thống.

| Feature ID | Epic | Feature | Mô tả |
| ----- | ----- | ----- | ----- |
| F01 | EP01 | User Login | Cho phép người dùng đăng nhập hệ thống |
| F02 | EP01 | RBAC | Phân quyền theo Role |
| F03 | EP02 | Create Batch | Farmer tạo Batch mới |
| F04 | EP02 | Batch Status Management | Quản lý trạng thái Batch |
| F05 | EP02 | Batch Immutability | Không cho phép chỉnh sửa/xóa Batch sau khi tạo |
| F06 | EP03 | Create Sample | Tạo Sample thuộc Batch |
| F07 | EP03 | Sample-Batch Association | Liên kết Sample với Batch |
| F08 | EP04 | Upload Laboratory Test Report | Upload Laboratory Test Report |
| F09 | EP04 | Report Validation | Kiểm tra Report thuộc đúng Sample/Batch |
| F10 | EP05 | Submit for Audit | Gửi Batch để Auditor review |
| F11 | EP05 | Auditor Review | Auditor kiểm tra hồ sơ Batch |
| F12 | EP05 | Approve Batch | Auditor Approve Batch |
| F13 | EP05 | Reject Batch | Auditor Reject Batch và ghi nhận lý do |
| F14 | EP05 | Resubmit Rejected Batch | Bổ sung/thay thế hồ sơ và gửi lại Batch bị Reject |
| F15 | EP06 | SHA-256 Generation | Tạo SHA-256 cho Laboratory Test Report |
| F16 | EP06 | Proof of Integrity | Tạo và lưu Proof of Integrity |
| F17 | EP07 | QR Generation | Tạo QR sau khi Batch đạt AUDITED |
| F18 | EP07 | Trace ID | Tạo định danh truy xuất cho Batch |
| F19 | EP08 | QR Scanning | Consumer quét QR |
| F20 | EP08 | Public Batch Information | Hiển thị thông tin Batch công khai |
| F21 | EP09 | User Management | Admin quản lý tài khoản |
| F22 | EP09 | Audit Trail | Ghi nhận lịch sử các thao tác quan trọng |

***5.3. User Story***  
*5.3.1. Authentication & Authorization*

| ID | User Story |
| ----- | ----- |
| US01 | Là **người dùng**, tôi muốn đăng nhập bằng tài khoản được cấp để truy cập các chức năng phù hợp với Role của mình. |
| US02 | Là **System Administrator**, tôi muốn phân quyền người dùng theo Role để ngăn người dùng thực hiện các chức năng không được phép. |

*5.3.2. Batch Management*

| ID | User Story |
| ----- | ----- |
| US03 | Là **Farmer**, tôi muốn tạo Batch với đầy đủ thông tin bắt buộc để đăng ký một lô sản phẩm vào hệ thống. |
| US04 | Là **Farmer**, tôi muốn xem thông tin và trạng thái Batch để theo dõi quá trình xử lý của lô hàng. |
| US05 | Là **System**, tôi muốn tự động sinh Batch ID/Batch Code duy nhất để định danh Batch. |
| US06 | Là **System**, tôi muốn đặt Batch mới ở trạng thái UNVERIFIED để đảm bảo Batch chưa được xem là đã kiểm định. |
| US07 | Là **System**, tôi muốn khóa thông tin Batch sau khi tạo để tránh thay đổi dữ liệu của lô hàng trong quá trình kiểm nghiệm và Audit. |

*5.3.3. Sample Management*

| ID | User Story |
| ----- | ----- |
| US08 | Là **Farmer**, tôi muốn tạo Sample thuộc một Batch để quản lý mẫu được lấy từ lô hàng. |
| US09 | Là **System**, tôi muốn mỗi Sample có Sample ID duy nhất để có thể truy xuất Sample về đúng Batch. |
| US10 | Là **System**, tôi muốn kiểm tra Sample thuộc Batch hợp lệ để ngăn việc sử dụng Sample của Batch khác. |

*5.3.4. Laboratory Test Report*

| ID | User Story |
| ----- | ----- |
| US11 | Là **Auditor**, tôi muốn upload Laboratory Test Report để bổ sung kết quả kiểm nghiệm cho Batch. |
| US12 | Là **System**, tôi muốn kiểm tra Report có liên kết đúng với Sample và Batch hay không để ngăn sử dụng sai Report. |
| US13 | Là **System**, tôi muốn lưu Laboratory Test Report cùng thông tin định danh liên quan để phục vụ quá trình Audit. |

Trong phiên bản hiện tại, Laboratory là bên thực hiện kiểm nghiệm và cung cấp Report; không nhất thiết phải là Actor đăng nhập trực tiếp vào hệ thống.  
*5.3.5. Auditor Gatekeeper*

| ID | User Story |
| ----- | ----- |
| US14 | Là **Farmer**, tôi muốn Submit Batch for Audit để yêu cầu Auditor kiểm tra Batch. |
| US15 | Là **Auditor**, tôi muốn xem thông tin Batch, Sample và Laboratory Test Report để thực hiện kiểm tra. |
| US16 | Là **Auditor**, tôi muốn kiểm tra SHA-256 và Proof of Integrity để xác nhận tính toàn vẹn của dữ liệu. |
| US17 | Là **Auditor**, tôi muốn Approve Batch khi tất cả điều kiện Audit được đáp ứng để xác nhận Batch đạt yêu cầu. |
| US18 | Là **Auditor**, tôi muốn Reject Batch và ghi nhận lý do khi Batch chưa đáp ứng yêu cầu. |
| US19 | Là **Farmer**, tôi muốn bổ sung hoặc thay thế hồ sơ theo lý do Reject để có thể gửi Batch review lại. |
| US20 | Là **System**, tôi muốn ngăn Farmer Approve hoặc thay đổi trạng thái Audit để đảm bảo quyền quyết định thuộc về Auditor. |

*5.3.6. Data Integrity & Proof*

| ID | User Story |
| ----- | ----- |
| US21 | Là **System**, tôi muốn tự động tính SHA-256 khi Laboratory Test Report được upload để xác định giá trị hash của file. |
| US22 | Là **System**, tôi muốn lưu SHA-256 cùng Report để có thể kiểm tra tính toàn vẹn của file. |
| US23 | Là **System**, tôi muốn tạo Proof of Integrity cho dữ liệu/lịch sử xử lý để hỗ trợ kiểm tra tính toàn vẹn. |
| US24 | Là **Auditor**, tôi muốn kiểm tra Proof of Integrity để có thêm cơ sở xác nhận dữ liệu trong quá trình Audit. |

*5.3.7. QR & Traceability*

| ID | User Story |
| ----- | ----- |
| US25 | Là **System**, tôi muốn chỉ tạo QR cho Batch đã có trạng thái AUDITED để ngăn sản phẩm chưa được kiểm định được phát hành QR chính thức. |
| US26 | Là **System**, tôi muốn tạo Trace ID duy nhất cho Batch đã AUDITED để phục vụ truy xuất nguồn gốc. |
| US27 | Là **Consumer**, tôi muốn quét QR trên sản phẩm để truy cập thông tin truy xuất của Batch. |
| US28 | Là **System**, tôi muốn kiểm tra Trace ID khi Consumer quét QR để đảm bảo thông tin được truy xuất từ Batch hợp lệ. |
| US29 | Là **Consumer**, tôi muốn xem thông tin công khai của Batch để kiểm tra nguồn gốc và trạng thái kiểm định của sản phẩm. |

*5.3.8. Administration & Audit Trail*

| ID | User Story |
| ----- | ----- |
| US30 | Là **Admin**, tôi muốn quản lý tài khoản người dùng để kiểm soát việc sử dụng hệ thống. |
| US31 | Là **Admin**, tôi muốn gán Role cho người dùng để xác định quyền truy cập. |
| US32 | Là **Admin**, tôi muốn xem Audit Trail để theo dõi các thao tác quan trọng trên hệ thống. |
| US33 | Là **System**, tôi muốn ghi nhận người thực hiện, thời gian, hành động và đối tượng bị tác động để hỗ trợ truy vết. |

***5.4. Acceptance Criteria***  
Acceptance Criteria (AC) là các điều kiện cần đạt để một User Story được xem là hoàn thành về mặt nghiệp vụ.  
*5.4.1. Create Batch – US03*  
**AC01:** Farmer phải đăng nhập trước khi tạo Batch.  
**AC02:** Các trường bắt buộc của Batch phải được nhập đầy đủ.  
**AC03:** System phải sinh Batch ID/Batch Code duy nhất.  
**AC04:** Batch được tạo thành công phải có trạng thái UNVERIFIED.  
**AC05:** Batch không được tạo nếu thiếu thông tin bắt buộc hoặc dữ liệu không hợp lệ.  
*5.4.2. Batch Immutability – US07*  
**AC01:** Sau khi Batch được tạo, Farmer không được chỉnh sửa thông tin Batch.  
**AC02:** Farmer không được xóa Batch đã tạo.  
**AC03:** Batch ID/Batch Code không được thay đổi.  
**AC04:** Status của Batch chỉ được thay đổi thông qua workflow được hệ thống kiểm soát.  
*5.4.3. Create Sample – US08*  
**AC01:** Sample phải được liên kết với một Batch tồn tại.  
**AC02:** Sample phải có Sample ID duy nhất.  
**AC03:** Một Sample không được thuộc đồng thời nhiều Batch.  
*5.4.4. Upload Laboratory Test Report – US11*  
**AC01:** Chỉ người dùng có quyền mới được upload Report.  
**AC02:** Report phải được liên kết với Sample và Batch tương ứng.  
**AC03:** System phải kiểm tra tính hợp lệ của định dạng file.  
**AC04:** System phải lưu thông tin Report sau khi upload thành công.  
*5.4.5. Report Validation – US12*  
**AC01:** System phải xác định được Batch liên quan đến Report.  
**AC02:** Sample trong Report phải thuộc Batch đang được kiểm định.  
**AC03:** Report không khớp Batch/Sample phải bị từ chối hoặc không được sử dụng để Approve.  
*5.4.6. SHA-256 – US21*  
**AC01:** System tự động tính SHA-256 khi Report được upload.  
**AC02:** SHA-256 được lưu cùng Report.  
**AC03:** Nếu nội dung file thay đổi, giá trị SHA-256 phải thay đổi.  
**AC04:** Auditor không được tự ý sửa giá trị SHA-256 do System tạo.  
*5.4.7. Auditor Approve – US17*  
Auditor chỉ được Approve khi tất cả điều kiện sau được đáp ứng:  
Laboratory Test Report tồn tại AND Report thuộc đúng Sample AND Sample thuộc đúng Batch AND SHA-256 hợp lệ AND Proof of Integrity hợp lệ  
Nếu thiếu bất kỳ điều kiện bắt buộc nào, nút/chức năng Approve phải bị chặn.  
Khi Approve thành công: Batch status: UNVERIFIED → AUDITED  
*5.4.8. Auditor Reject – US18*  
**AC01:** Auditor có quyền Reject Batch.  
**AC02:** Khi Reject, Auditor phải cung cấp lý do Reject.  
**AC03:** System cập nhật trạng thái Batch thành REJECTED.  
**AC04:** System ghi nhận Reject vào Audit Trail.  
**AC05:** Farmer nhận được thông báo về lý do Reject.  
*5.4.9. QR Generation – US25*  
Đây là Business Rule quan trọng của hệ thống:  
**AC01:** Batch phải có trạng thái AUDITED.  
**AC02:** Batch chưa AUDITED không được tạo QR.  
**AC03:** Batch REJECTED không được tạo QR.  
**AC04:** Batch UNVERIFIED không được tạo QR.  
**AC05:** QR phải liên kết với Trace ID/Batch hợp lệ.  
**AC06:** QR được tạo sau khi Batch chuyển sang AUDITED.  
*5.4.10. Consumer Traceability – US27/US29*  
**AC01:** Consumer có thể quét QR mà không cần đăng nhập.  
**AC02:** System phải lấy Trace ID từ QR.  
**AC03:** System phải kiểm tra Trace ID tồn tại và hợp lệ.  
**AC04:** Nếu Trace ID hợp lệ, System hiển thị thông tin được phép công khai.  
**AC05:** Nếu Trace ID không hợp lệ hoặc không tồn tại, System hiển thị thông báo lỗi.  
***5.5. Priority – Mức độ ưu tiên***  
Mức độ ưu tiên được sử dụng để xác định thứ tự triển khai các chức năng.

| Priority | Ý nghĩa |
| :---: | :---: |
| P0 – Critical | Bắt buộc để hệ thống có thể thực hiện nghiệp vụ cốt lõi |
| P1 – High | Quan trọng, cần triển khai trong phiên bản chính |
| P2 – Medium | Có giá trị nhưng có thể triển khai sau chức năng cốt lõi |
| P3 – Low | Chức năng mở rộng hoặc cải tiến |

Product Backlog ưu tiên

| ID | User Story | Priority |
| ----- | ----- | ----- |
| US01 | User Login | P0 |
| US02 | RBAC | P0 |
| US03 | Create Batch | P0 |
| US05 | Sinh Batch ID/Code | P0 |
| US06 | Batch UNVERIFIED | P0 |
| US08 | Create Sample | P0 |
| US10 | Validate Sample-Batch | P0 |
| US11 | Upload Laboratory Test Report | P0 |
| US12 | Validate Report | P0 |
| US14 | Submit for Audit | P0 |
| US15 | Auditor Review | P0 |
| US17 | Approve Batch | P0 |
| US18 | Reject Batch | P0 |
| US21 | Generate SHA-256 | P0 |
| US23 | Proof of Integrity | P0 |
| US25 | Generate QR after AUDITED | P0 |
| US27 | Scan QR | P0 |
| US29 | Public Traceability | P0 |
| US04 | View Batch | P1 |
| US07 | Batch Immutability | P1 |
| US19 | Resubmit Rejected Batch | P1 |
| US22 | Store SHA-256 | P1 |
| US24 | Verify Proof | P1 |
| US30 | User Management | P1 |
| US32 | Audit Trail | P1 |
| US26 | Trace ID | P1 |
| US31 | Role Management | P1 |
| US33 | Detailed Activity Logging | P1 |

***5.6. Dependencies – Phụ thuộc***  
Dependencies xác định các User Story hoặc Feature cần được hoàn thành trước khi một chức năng khác có thể hoạt động.

| User Story | Phụ thuộc vào | Giải thích |
| ----- | ----- | ----- |
| US03 Create Batch | US01, US02 | Phải đăng nhập và có quyền Farmer |
| US08 Create Sample | US03 | Sample phải thuộc một Batch tồn tại |
| US11 Upload Report | US08 | Report phải gắn với Sample |
| US12 Validate Report | US08, US11 | Cần Batch, Sample và Report để đối chiếu |
| US21 SHA-256 | US11 | SHA-256 được tạo từ Report |
| US23 Proof of Integrity | US11, US21 | Proof được tạo dựa trên dữ liệu đã được lưu và kiểm tra Integrity |
| US14 Submit for Audit | US12, US21, US23 | Batch phải có hồ sơ và Integrity data cần thiết |
| US15 Auditor Review | US14 | Auditor chỉ review Batch đã được Submit |
| US17 Approve | US15, US12, US21, US23 | Approve phụ thuộc vào toàn bộ điều kiện Audit |
| US18 Reject | US15 | Chỉ xảy ra sau quá trình Review |
| US19 Resubmit | US18 | Chỉ áp dụng cho Batch bị Reject |
| US25 Generate QR | US17 | Chỉ tạo QR sau khi Batch AUDITED |
| US27 Scan QR | US25 | Phải có QR trước khi Consumer quét |
| US29 Public Traceability | US25, US27 | Cần QR/Trace ID để truy xuất |
| US32 Audit Trail | US01, US02 | Cần xác định User/Role để ghi nhận hành động |

***5.7. Definition of Done***  
Definition of Done (DoD) là tập hợp các điều kiện để xác định một User Story hoặc Feature đã được hoàn thành và có thể được nghiệm thu.  
Một User Story được xem là Done khi đáp ứng đầy đủ các điều kiện sau:  
*5.7.1. Functional*

- Chức năng được phát triển đúng theo User Story.  
- Đáp ứng đầy đủ Acceptance Criteria.  
- Workflow nghiệp vụ hoạt động đúng.  
- Các trạng thái và điều kiện chuyển trạng thái được kiểm soát chính xác.

*5.7.2. Authorization & Security*

- Người dùng phải được xác thực trước khi thực hiện chức năng yêu cầu đăng nhập.  
- Role và Permission được kiểm tra tại Backend/API.  
- User không thể thực hiện chức năng ngoài quyền được cấp.  
- Các API quan trọng không chỉ dựa vào việc ẩn nút trên Frontend để bảo vệ quyền.

*5.7.3. Data Integrity*

- Dữ liệu được lưu đúng cấu trúc.  
- Quan hệ Batch → Sample → Report được kiểm tra.  
- SHA-256 được tạo và lưu đúng.  
- Proof of Integrity được tạo và lưu theo thiết kế.  
- Không cho phép thay đổi dữ liệu Audit trái với Business Rule.

*5.7.4. Testing*

- Developer hoàn thành Unit Test đối với các logic quan trọng.  
- QA hoàn thành Functional Test.  
- Các Acceptance Criteria được kiểm thử.  
- Các trường hợp lỗi và trường hợp biên quan trọng được kiểm thử.  
- Không còn lỗi Critical/Blocker chưa được xử lý trước khi nghiệm thu.

*5.7.5. Audit Workflow*

- Batch mới luôn ở UNVERIFIED.  
- Farmer không thể Approve Batch.  
- Auditor có thể Review.  
- Auditor chỉ Approve khi đủ điều kiện.  
- Auditor có thể Reject và phải ghi nhận lý do.  
- Batch bị Reject có thể được Submit lại sau khi bổ sung hồ sơ theo quy định.  
- Batch AUDITED không được Farmer chỉnh sửa/xóa.

*5.7.6. QR & Traceability*

- QR chỉ được tạo khi Batch có trạng thái AUDITED.  
- QR liên kết đúng với Batch/Trace ID.  
- QR của Batch chưa Audit không tồn tại.  
- Consumer có thể quét QR để truy xuất thông tin.  
- QR không hợp lệ phải trả về thông báo lỗi phù hợp.

*5.7.7. Documentation*

- User Story và Acceptance Criteria được cập nhật nếu có thay đổi.  
- API/documentation liên quan được cập nhật.  
- Test Case và Test Result được lưu lại.  
- Các Business Rule quan trọng được phản ánh trong tài liệu.  
- Feature được Product Owner/BA xác nhận đạt yêu cầu.

Một User Story chỉ được chuyển sang trạng thái Done khi đáp ứng đồng thời yêu cầu nghiệp vụ, kỹ thuật, kiểm thử và tài liệu liên quan.  
**6\. System Analysis – Phân tích hệ thống**  
6.1. Use Case Diagram  
![][image4]

![][image5]

![][image6]

![][image7]  
![][image8]  
![][image9]

6.2. Use Case Specification  
6.2.1. UC01 – Login

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC01 |
| Use Case Name | Login |
| Primary Actor | Farmer / Auditor / Admin |
| Goal | Đăng nhập vào hệ thống |
| Preconditions | Người dùng đã có tài khoản hợp lệ |
| Postconditions | Người dùng được xác thực và truy cập chức năng theo Role |

**Main Flow:**

1. Người dùng nhập username/email và password.  
2. System kiểm tra thông tin đăng nhập.  
3. System xác thực tài khoản.  
4. System xác định Role của người dùng.  
5. System cấp quyền truy cập tương ứng.  
6. Người dùng truy cập Dashboard phù hợp.

**Alternative Flow:**

* Thông tin đăng nhập không đúng → System thông báo lỗi.  
* Tài khoản bị khóa → System từ chối đăng nhập.

6.2.2. UC03 – Create Batch

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC03 |
| Use Case Name | Create Batch |
| Primary Actor | Farmer |
| Goal | Tạo một Batch mới |
| Preconditions | Farmer đã đăng nhập |
| Postconditions | Batch được tạo với trạng thái UNVERIFIED |

**Main Flow:**

1. Farmer chọn chức năng Create Batch.  
2. System hiển thị form tạo Batch.  
3. Farmer nhập các thông tin bắt buộc.  
4. Farmer gửi yêu cầu tạo Batch.  
5. System kiểm tra dữ liệu.  
6. System sinh Batch ID/Batch Code duy nhất.  
7. System tạo Batch.  
8. System đặt trạng thái UNVERIFIED.  
9. System lưu thông tin Batch.  
10. System thông báo tạo Batch thành công.

**Alternative Flow:**

* Thiếu trường bắt buộc → System thông báo lỗi.  
* Dữ liệu không hợp lệ → System từ chối tạo Batch.

**Business Rules:**

* Batch ID/Batch Code do System sinh.  
* Batch mới luôn có trạng thái UNVERIFIED.  
* Farmer không được tự đặt Status.  
* Sau khi tạo, Farmer không được chỉnh sửa hoặc xóa Batch.

6.2.3. UC06 – Register Sample

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC06 |
| Use Case Name | Register Sample |
| Primary Actor | Auditor |
| Goal | Đăng ký Sample thực tế thuộc một Batch |
| Preconditions | Batch tồn tại và ở trạng thái phù hợp |
| Postconditions | Sample được tạo và liên kết với Batch |

**Main Flow:**

1. Auditor tiếp nhận Sample từ Farmer.  
2. Auditor chọn Batch tương ứng.  
3. Auditor chọn Register Sample.  
4. System hiển thị form Sample.  
5. Auditor nhập thông tin Sample.  
6. System kiểm tra Batch.  
7. System sinh Sample ID duy nhất.  
8. System liên kết Sample với Batch.  
9. System lưu Sample.

**Business Rules:**

* Mỗi Sample thuộc đúng một Batch.  
* Một Batch có thể có nhiều Sample.  
* Sample ID do System sinh.  
* Sample phải được liên kết với Batch tồn tại.

6.2.4. UC08 – Upload Laboratory Test Report

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC08 |
| Use Case Name | Upload Laboratory Test Report |
| Primary Actor | Auditor |
| Goal | Đưa kết quả kiểm nghiệm của Laboratory vào hệ thống |
| Preconditions | Sample và Batch đã tồn tại |
| Postconditions | Laboratory Test Report được lưu và liên kết với Sample/Batch |

**Main Flow:**

1. Auditor nhận Laboratory Test Report từ Laboratory.  
2. Auditor chọn Batch/Sample tương ứng.  
3. Auditor upload Report.  
4. System kiểm tra file.  
5. System kiểm tra Batch và Sample.  
6. System xác nhận Report thuộc đúng Sample/Batch.  
7. System tính SHA-256.  
8. System tạo Proof of Integrity.  
9. System lưu Report, SHA-256 và Proof.  
10. System thông báo upload thành công.

**Alternative Flow:**

* File không đúng định dạng → từ chối upload.  
* Sample không tồn tại → từ chối.  
* Report không khớp Sample/Batch → từ chối.  
* File không hợp lệ → từ chối xử lý.

6.2.5. UC10 – Submit Batch for Audit

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC10 |
| Use Case Name | Submit Batch for Audit |
| Primary Actor | Farmer |
| Goal | Gửi Batch để Auditor thực hiện kiểm tra |
| Preconditions | Batch tồn tại và có đủ hồ sơ cần thiết |
| Postconditions | Batch chuyển sang trạng thái chờ Review |

**Main Flow:**

1. Farmer chọn Batch.  
2. Farmer chọn Submit for Audit.  
3. System kiểm tra điều kiện Audit.  
4. System kiểm tra Sample.  
5. System kiểm tra Laboratory Test Report.  
6. System kiểm tra SHA-256.  
7. System kiểm tra Proof of Integrity.  
8. Nếu hợp lệ, System chuyển Batch sang REVIEWING.  
9. System thông báo Submit thành công.

**Alternative Flow:**

* Thiếu Sample → không cho Submit.  
* Thiếu Laboratory Test Report → không cho Submit.  
* SHA-256 không tồn tại/không hợp lệ → không cho Submit.  
* Proof không hợp lệ → không cho Submit.

6.2.6. UC11 – Review Batch

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC11 |
| Use Case Name | Review Batch |
| Primary Actor | Auditor |
| Goal | Kiểm tra Batch trước khi quyết định Approve/Reject |
| Preconditions | Batch có trạng thái REVIEWING |
| Postconditions | Auditor có thể Approve hoặc Reject |

**Main Flow:**

1. Auditor mở Batch cần Review.  
2. System hiển thị thông tin Batch.  
3. Auditor kiểm tra Sample.  
4. Auditor kiểm tra Laboratory Test Report.  
5. Auditor kiểm tra SHA-256.  
6. Auditor kiểm tra Proof of Integrity.  
7. Auditor đánh giá hồ sơ.  
8. Auditor chọn Approve hoặc Reject.

6.2.7. UC12 – Approve Batch

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC12 |
| Use Case Name | Approve Batch |
| Primary Actor | Auditor |
| Goal | Xác nhận Batch đạt yêu cầu kiểm định |
| Preconditions | Batch đang ở trạng thái REVIEWING |
| Postconditions | Batch chuyển thành AUDITED |

**Main Flow:**

1. Auditor chọn Approve.  
2. System kiểm tra các điều kiện bắt buộc:  
   * Laboratory Test Report tồn tại.  
   * Report thuộc đúng Sample.  
   * Sample thuộc đúng Batch.  
   * SHA-256 hợp lệ.  
   * Proof of Integrity hợp lệ.  
3. Nếu tất cả điều kiện hợp lệ, System cho phép Approve.  
4. System cập nhật Batch thành AUDITED.  
5. System ghi nhận Auditor và thời điểm Audit.  
6. System ghi Audit Trail.  
7. System cho phép tạo QR cho Batch.

**Alternative Flow:**  
Nếu thiếu bất kỳ điều kiện nào:  
Report thiếu  
      OR  
Sample không khớp  
      OR  
Batch không khớp  
      OR  
SHA-256 không hợp lệ  
      OR  
Proof không hợp lệ  
            ↓  
     KHÔNG CHO APPROVE  
6.2.8. UC13 – Reject Batch

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC13 |
| Use Case Name | Reject Batch |
| Primary Actor | Auditor |
| Goal | Từ chối Batch chưa đáp ứng yêu cầu |
| Preconditions | Batch đang được Review |
| Postconditions | Batch chuyển thành REJECTED |

**Main Flow:**

1. Auditor chọn Reject.  
2. System yêu cầu nhập lý do Reject.  
3. Auditor nhập lý do.  
4. System lưu lý do.  
5. System chuyển Batch thành REJECTED.  
6. System ghi Audit Trail.  
7. System thông báo cho Farmer.

**Alternative Flow:**

* Auditor không nhập lý do → System không cho Reject.

6.2.9. UC14 – Resubmit Rejected Batch

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC14 |
| Use Case Name | Resubmit Rejected Batch |
| Primary Actor | Farmer |
| Goal | Gửi lại hồ sơ của Batch bị Reject |
| Preconditions | Batch có trạng thái REJECTED |
| Postconditions | Batch quay lại trạng thái chờ Review |

**Main Flow:**

1. Farmer xem lý do Reject.  
2. Farmer bổ sung hoặc thay thế hồ sơ được yêu cầu.  
3. Farmer chọn Submit Again.  
4. System kiểm tra hồ sơ.  
5. System kiểm tra SHA-256/Proof nếu Report được thay thế.  
6. System chuyển Batch sang REVIEWING.  
7. Auditor có thể Review lại.

**Business Rule:**  
> Farmer không được chỉnh sửa hoặc xóa thông tin Batch. Việc xử lý Batch bị Reject được thực hiện bằng cách bổ sung/thay thế hồ sơ cần thiết theo lý do Reject.  
6.2.10. UC15 – Generate SHA-256

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC15 |
| Use Case Name | Generate SHA-256 |
| Primary Actor | System |
| Goal | Tạo giá trị hash đại diện cho Laboratory Test Report |
| Preconditions | Report được upload thành công |
| Postconditions | SHA-256 được lưu cùng Report |

**Main Flow:**

1. System nhận file Report.  
2. System tính SHA-256 từ nội dung file.  
3. System lưu giá trị SHA-256.  
4. SHA-256 được sử dụng trong quá trình kiểm tra Integrity.

6.2.11. UC16 – Generate Proof of Integrity

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC16 |
| Use Case Name | Generate Proof of Integrity |
| Primary Actor | System |
| Goal | Ghi nhận bằng chứng toàn vẹn của dữ liệu |
| Preconditions | Report và SHA-256 đã được xử lý |
| Postconditions | Proof được lưu vào hệ thống |

Trong phiên bản hiện tại, Proof of Integrity được lưu trong cơ sở dữ liệu và sử dụng cơ chế hash chain để mô phỏng đặc tính khó thay đổi của Blockchain.  
---

6.2.12. UC18 – Generate QR

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC18 |
| Use Case Name | Generate QR |
| Primary Actor | System |
| Goal | Tạo QR cho Batch đã được Audit |
| Preconditions | Batch có trạng thái AUDITED |
| Postconditions | QR được tạo và liên kết với Batch/Trace ID |

**Main Flow:**

1. Batch chuyển sang AUDITED.  
2. System kiểm tra trạng thái Batch.  
3. System sinh Trace ID.  
4. System tạo QR chứa thông tin truy cập Traceability.  
5. System liên kết QR với Batch.  
6. QR được sử dụng trên sản phẩm.

**Business Rules:**

* Chỉ Batch AUDITED mới được tạo QR.  
* Batch UNVERIFIED, REVIEWING, REJECTED không được tạo QR.  
* QR phải liên kết với đúng Batch/Trace ID.

6.2.13. UC19 – Scan QR

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC19 |
| Use Case Name | Scan QR |
| Primary Actor | Consumer |
| Goal | Truy xuất thông tin sản phẩm |
| Preconditions | QR tồn tại |
| Postconditions | Consumer xem được thông tin công khai hoặc thông báo lỗi |

**Main Flow:**

1. Consumer quét QR.  
2. System nhận Trace ID.  
3. System kiểm tra Trace ID.  
4. System tìm Batch tương ứng.  
5. System kiểm tra trạng thái Batch.  
6. Nếu hợp lệ, System hiển thị thông tin truy xuất.  
7. Consumer xem thông tin Batch.

**Alternative Flow:**

* QR không hợp lệ → hiển thị lỗi.  
* Trace ID không tồn tại → hiển thị lỗi.  
* Batch không hợp lệ → không hiển thị thông tin chứng nhận.

6.2.14. UC20 – View Public Traceability Information  
Thông tin có thể được công khai cho Consumer bao gồm:

* Product Name.  
* Batch Code hoặc Trace ID.  
* Nguồn gốc sản phẩm.  
* Thông tin ngày sản xuất/thu hoạch phù hợp với chính sách công khai.  
* Trạng thái kiểm định.  
* Thông tin Laboratory Test Report được phép công khai.  
* Thông tin Audit phù hợp với chính sách của doanh nghiệp.

Thông tin nhạy cảm hoặc thông tin nội bộ của doanh nghiệp không được công khai nếu không được xác định trong yêu cầu hệ thống.  
6.2.15. UC21 – Manage Users

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC21 |
| Use Case Name | Manage Users |
| Primary Actor | Admin |
| Goal | Quản lý tài khoản người dùng |
| Preconditions | Admin đã đăng nhập |
| Postconditions | Thông tin tài khoản được cập nhật |

Các chức năng bao gồm:

* Tạo User.  
* Xem User.  
* Khóa/Mở khóa User.  
* Gán Role.  
* Cập nhật thông tin User theo quyền.

6.2.16. UC22 – View Audit Trail

| Thuộc tính | Nội dung |
| ----- | ----- |
| Use Case ID | UC22 |
| Use Case Name | View Audit Trail |
| Primary Actor | Admin / Auditor |
| Goal | Theo dõi lịch sử thao tác quan trọng |
| Preconditions | Actor có quyền xem Audit Trail |
| Postconditions | Lịch sử hoạt động được hiển thị |

Audit Trail có thể ghi nhận:

* Actor/User.  
* Action.  
* Object/Batch ID.  
* Thời gian.  
* Kết quả thao tác.  
* Các thông tin liên quan đến Audit.

Các sự kiện quan trọng gồm:

* Create Batch.  
* Create Sample.  
* Upload Report.  
* Generate SHA-256.  
* Generate Proof.  
* Submit for Audit.  
* Approve.  
* Reject.  
* Resubmit.  
* Generate QR.
