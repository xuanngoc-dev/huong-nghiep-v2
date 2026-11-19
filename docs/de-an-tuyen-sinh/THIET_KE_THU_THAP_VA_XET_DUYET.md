# Thiết kế CMS thu thập và xét duyệt dữ liệu tuyển sinh

Quản trị viên thu thập đề án cho một trường trong một năm tuyển sinh, xét duyệt trên CMS và tải JSON đúng mẫu.

Nút **Duyệt và đưa vào hệ thống** thực hiện việc duyệt và nhập MySQL trong cùng một giao dịch. Khi thành công, quản trị viên có thể mở đề án vừa tạo hoặc tải JSON của phiên bản đã duyệt. Quy tắc xét tuyển mới nhập ở trạng thái **Thử nghiệm**.

Backend dùng model từ `OPENAI_MODEL` trong `backend/.env`, mặc định là `gpt-6.2-sol`. Bước **Tìm nguồn** dùng công cụ tìm kiếm web để lấy URL tài liệu. AI quyết định số lượng nguồn theo mức độ liên quan và phạm vi tuyển sinh. Sau khi quản trị viên chọn nguồn, backend đọc nội dung trang web hoặc PDF và gửi nội dung đó cho model để tạo bản nháp JSON có dẫn chứng.

## 1. Luồng của quản trị viên

1. Vào **Đề án tuyển sinh → Thu thập dữ liệu**, nhập mã trường và năm. CMS hiện tên trường, cơ sở tương ứng để quản trị viên kiểm tra trước khi bấm **Tìm nguồn**.
2. AI tìm đề án, phụ lục và thông báo điều chỉnh đúng năm. CMS **hiển thị danh sách nguồn trước khi trích xuất**. Quản trị viên mở tài liệu, chọn nguồn áp dụng, loại nguồn sai hoặc bổ sung URL chính thức.
3. Bấm **Tạo bản nháp** để theo dõi thời gian đã chạy, bước đang xử lý và số mục đã xử lý khi có. Có thể bấm **Dừng** rồi tạo lại. AI gắn dẫn chứng từ các nguồn đọc và xác minh được. Các nguồn lỗi được ghi riêng trong bản nháp để người duyệt kiểm tra. Bản nháp được gửi vào hàng đợi **Xét duyệt dữ liệu**.
4. Người duyệt đối chiếu từng mục, sửa giá trị có căn cứ hoặc trả lại để bổ sung. Khi bản nháp đạt yêu cầu, người duyệt bấm **Duyệt và đưa vào hệ thống**.
5. CMS báo **Đã duyệt và nhập**, hiển thị **Mở đề án** và **Tải JSON**. Việc công bố đề án cho chatbot và kích hoạt quy tắc cho bộ tính xét tuyển tiếp tục theo quy trình hiện hành.

## 2. Hai màn hình CMS

### Thu thập dữ liệu

| Thành phần | Thiết kế |
| --- | --- |
| Thông tin phiên | Mã trường, tên trường hoặc cơ sở đã nhận diện, năm tuyển sinh, người tạo và trạng thái. Có thể mở lại phiên từ danh sách. |
| Danh sách nguồn | Mỗi dòng hiển thị tên tài liệu, cơ quan công bố, loại tài liệu, URL gốc, năm áp dụng, ngày công bố nếu có và thời điểm truy cập. Có nút **Mở tài liệu** và lựa chọn dùng hoặc loại nguồn. |
| Tài liệu điều chỉnh | Hiển thị tài liệu được thay thế, ngày hiệu lực và phạm vi điều chỉnh. Một phụ lục sửa chỉ tiêu của một chương trình chỉ thay thế số liệu trong phạm vi đó. |
| Thiếu nguồn | Hiển thị những tài liệu đã tìm và lý do chưa dùng được. Cho phép bổ sung URL chính thức hoặc tìm lại. Phiên chỉ tạo bản nháp khi có nguồn phù hợp với trường và năm. |

### Xét duyệt dữ liệu

Hàng đợi mặc định hiển thị các bản **Chờ duyệt**. Người dùng có thể lọc theo trường, năm hoặc trạng thái. Khi mở một bản, CMS hiển thị mã phiên, số phiên bản, người tạo và những mục cần đối chiếu.

| Khung dữ liệu | Khung dẫn chứng |
| --- | --- |
| Nhóm theo thông tin chung, cơ sở, chương trình, chỉ tiêu, phương thức, tổ hợp, điều kiện, công thức, điểm và học phí. Mỗi mục có giá trị AI đề xuất và trạng thái kiểm tra. | Chọn một mục để thấy tài liệu làm căn cứ, URL, trang PDF hoặc mục trên website, đoạn trích và ngày hiệu lực nếu có. Khi có nhiều nguồn mâu thuẫn, hiển thị từng giá trị cạnh dẫn chứng tương ứng. |

Người duyệt chọn thao tác phù hợp với kết quả đối chiếu.

- **Sửa và lưu nháp** để chỉnh giá trị, chọn dẫn chứng và ghi lý do. CMS lưu giá trị trước và sau khi sửa.
- **Yêu cầu bổ sung** để trả hồ sơ cho người xử lý, kèm mục cần làm rõ và lý do. Lần gửi lại tạo phiên bản mới để người duyệt nhìn thấy phần đã thay đổi.
- **Duyệt và đưa vào hệ thống** để xác nhận đúng phiên bản đang mở. Nếu một người khác vừa sửa, CMS yêu cầu mở phiên bản mới nhất trước khi duyệt.

**Ví dụ minh họa.** Đề án tháng 3 ghi 80 chỉ tiêu cho chương trình A. Phụ lục tháng 5 điều chỉnh lên 95. Màn duyệt hiển thị cả hai số cùng số trang. Người duyệt chọn 95, gắn phụ lục làm căn cứ và lưu lý do. Nếu trường chưa công bố học phí, người duyệt có thể giữ `null` và ghi chú về nguồn đã kiểm tra.

## 3. Điều kiện để duyệt và tải JSON

- Nguồn làm căn cứ phải đúng trường, cơ sở và năm áp dụng. Điểm chuẩn lịch sử có năm và nguồn riêng. Nguồn thứ cấp chỉ dùng để lần tới tài liệu gốc.
- Danh sách mã xét tuyển phải đồng bộ giữa `dats_tuyen_sinh.dats_chuong_trinh_dao_tao` và `quy_tac_xet_tuyen.chuong_trinh`. Kiểm tra thêm chỉ tiêu theo đúng phạm vi, mã cơ sở, tổ hợp, tham chiếu công thức, loại điểm, năm và thang điểm.
- Đối chiếu phương thức và phương án theo hai chiều. Nếu một phương thức có nhiều công thức hoặc các phương thức dùng chung mã Bộ, có thể khai `phuong_an[].ma_phuong_thuc_cua_truong` để chỉ rõ dòng áp dụng. Các phương án đã đối chiếu dùng đúng dòng đó khi ghi vào MySQL.
- CMS chặn duyệt nếu thiếu mã có căn cứ trong bảng công bố toàn trường đang áp dụng, hoặc tổng chỉ tiêu lệch khi các chương trình có phần phân bổ riêng cùng phạm vi. Khi bảng mã hoặc phạm vi chỉ tiêu chưa đủ căn cứ để kiểm tự động, người duyệt chọn nguồn và lưu lý do xác nhận cùng phiên bản nháp.
- Số liệu đã điền phải có căn cứ. Giá trị đơn chưa xác minh được dùng `null`, nhóm chưa có bản ghi dùng `[]`, kèm ghi chú phù hợp. Lỗi cấu trúc, tham chiếu sai hoặc mâu thuẫn chưa xử lý phải được giải quyết trước khi duyệt.
- File tải về dùng UTF-8, tên `<MA_TRUONG>_<NAM>_tuyen_sinh.json`, với đúng ba nhánh `thong_tin_import`, `dats_tuyen_sinh` và `quy_tac_xet_tuyen`. File được tạo từ bản chốt đã dùng để nhập. Nhật ký duyệt và dẫn chứng chi tiết được lưu riêng trong CMS để giữ đúng cấu trúc mẫu. [Mẫu XDA](chuan_du_lieu/du_lieu_mau_da_sua.json) · [Schema quy tắc xét tuyển](chuan_du_lieu/de_an_xet_tuyen.schema.json)

## 4. Cách xử lý nút “Duyệt và đưa vào hệ thống”

Backend kiểm tra quyền quản trị, trạng thái **Chờ duyệt** và phiên bản người dùng đang xem. Trong một transaction, backend nhập đề án và quy tắc, ghi người duyệt, thời điểm duyệt, liên kết đến đề án và chuyển phiên sang **Đã duyệt và nhập**. Trạng thái công bố và kích hoạt quy tắc do hệ thống quản lý.

| Tình huống | Kết quả trên CMS |
| --- | --- |
| Nhập thành công | Hiện mã đề án, người duyệt, thời điểm và hai nút **Mở đề án**, **Tải JSON**. |
| Lỗi nhập, ví dụ mã ngành thiếu trong danh mục | Rollback toàn bộ giao dịch. Bản vẫn **Chờ duyệt**. CMS chỉ rõ bản ghi hoặc trường dữ liệu cần xử lý. |
| Đã có đề án cho cùng mã trường và năm | CMS báo trùng và hiển thị liên kết đến đề án hiện có để quản trị viên đối chiếu. Bản nháp vẫn **Chờ duyệt**. |
| Bấm hai lần, hai người duyệt đồng thời hoặc trình duyệt gửi lại sau khi mất kết nối | Cùng một phiên bản chỉ tạo một đề án. Nếu lần đầu đã thành công, yêu cầu sau trả về đề án đó. |

Quyền duyệt, nhập và tải bản chính thức được kiểm tra ở backend. CMS giữ dấu vết từ nguồn đã chọn đến phiên bản đã duyệt và đề án đã nhập. Với quy tắc xét tuyển, quản trị viên chạy thử và đối chiếu kết quả trước khi chuyển sang **Đang áp dụng**. [Quy trình nhập đầy đủ](chuan_du_lieu/HUONG_DAN_IMPORT_DAY_DU.md) · [Quy trình đưa một trường vào bộ tính](QUY_TRINH_DUA_TRUONG_VAO.md)

## 5. Kế hoạch triển khai và nghiệm thu

| Đợt | Phần triển khai | Điều kiện nghiệm thu |
| --- | --- | --- |
| 1 | Tạo phiên, tìm nguồn chính thức và hiển thị nguồn | Từ mã trường và năm, người dùng mở được tài liệu gốc, bổ sung hoặc loại nguồn và quay lại phiên đang làm. |
| 2 | Trích xuất theo mẫu, gắn dẫn chứng, hàng đợi và màn xét duyệt | Từ một chỉ tiêu hoặc công thức, người duyệt lần được tới đúng đoạn nguồn. Có thể sửa, trả lại hoặc gửi lại bản nháp. Dữ liệu chờ duyệt chỉ xuất hiện trong CMS. |
| 3 | Duyệt và nhập trong một giao dịch, tải JSON, chạy thử | Một lần duyệt tạo một đề án và một bản JSON tương ứng. Kiểm thử cả tình huống trùng trường–năm, nhập lỗi, hai người duyệt và gửi lại sau khi mất kết nối. |
