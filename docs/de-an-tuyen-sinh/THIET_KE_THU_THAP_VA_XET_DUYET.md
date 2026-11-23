# Thiết kế CMS thu thập và xét duyệt dữ liệu tuyển sinh

Quản trị viên thu thập đề án cho một trường trong một năm tuyển sinh, xét duyệt trên CMS và tải JSON đúng mẫu.

Nút **Duyệt và đưa vào hệ thống** thực hiện việc duyệt và nhập MySQL trong cùng một giao dịch. Khi thành công, quản trị viên có thể mở đề án vừa tạo hoặc tải JSON của phiên bản đã duyệt. Quy tắc xét tuyển mới nhập ở trạng thái **Thử nghiệm**.

Backend dùng model từ `OPENAI_MODEL` trong `backend/.env`, mặc định là `gpt-6.2-sol`. **Thu thập toàn bộ** chạy nền từ mã trường và năm. AI chọn nguồn HTML chính thức, đọc các bảng, ảnh và liên kết liên quan rồi lập bản nháp theo cấu trúc nhập. Chế độ tự động tạm bỏ qua PDF.

Trong cùng lượt chạy, AI rà các trường còn trống, dẫn chứng và liên kết giữa mã xét tuyển, diện, tổ hợp và công thức. Khi còn thiếu, AI chọn các trang đã biết để đọc lại một lượt. Nếu vẫn cần nguồn mới, phiên có thể tìm thêm trang HTML chính thức tối đa ba lượt và rà lại bản gộp sau mỗi lần bổ sung dữ liệu. Khi kết thúc, CMS lưu một phiên bản để người duyệt xem dữ liệu đã lấy và các mục còn thiếu.

AI kiểm kê mã xét tuyển, diện, tổ hợp và biểu thức từ các phần tài liệu đọc được. Công thức được giữ cùng phạm vi áp dụng, điều kiện, thang điểm và đoạn trích. Màn xét duyệt cho biết từng công thức đã vào trường dữ liệu nào, công thức nào mới lưu dưới dạng mô tả và công thức nào còn thiếu trong bản nháp. Người duyệt có thể mở nguồn để xem lại biểu thức gốc. Số lượng báo cáo tính trên các mục đã nhận diện từ các nguồn đọc được. Các phần tài liệu cần xác minh thêm được liệt kê trong cùng báo cáo.

## 1. Luồng của quản trị viên

1. Vào **Đề án tuyển sinh → Thu thập dữ liệu**, nhập mã trường và năm. Kiểm tra tên trường, cơ sở rồi bấm **Thu thập toàn bộ**.
2. Theo dõi bước tìm nguồn, đọc tài liệu, đối chiếu theo mã xét tuyển, đọc lại hoặc tìm nguồn bổ sung và lưu bản nháp trong phiên. Có thể dừng lượt đang chạy hoặc mở lại phiên để xem tiến độ. Để tự chọn tài liệu trước khi trích xuất, dùng **Tìm nguồn để chọn**, kiểm tra các trang và bấm **Tạo nháp từ nguồn đã chọn**.
3. Mở **Xét duyệt dữ liệu** để xem dẫn chứng, các mục còn thiếu theo chương trình và các nguồn chưa dùng được. Các nhóm dữ liệu gồm đề án và cơ sở, chỉ tiêu, phương thức, tổ hợp, công thức, điều kiện, chính sách, lịch và hồ sơ, quy đổi, điểm chuẩn, học phí, nhân sự, cơ sở vật chất, quy mô đào tạo và việc làm sau tốt nghiệp.
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

Hàng đợi mặc định hiển thị các bản **Chờ duyệt**. Người dùng có thể lọc theo trường, năm hoặc trạng thái. Khi mở một bản, CMS hiển thị mã phiên, số phiên bản, người tạo và những mục cần đối chiếu. Nếu AI chưa hoàn tất rà soát, màn hình hiển thị trạng thái này, các khoảng trống đã ghi nhận và ghi chú để người duyệt kiểm tra tiếp.

| Khung dữ liệu | Khung dẫn chứng |
| --- | --- |
| Nhóm theo thông tin chung, cơ sở, chương trình, chỉ tiêu, phương thức, tổ hợp, điều kiện, công thức, điểm và học phí. Mỗi mục có giá trị AI đề xuất và trạng thái kiểm tra. | Chọn một mục để thấy tài liệu làm căn cứ, URL, trang PDF hoặc mục trên website, đoạn trích và ngày hiệu lực nếu có. Khi có nhiều nguồn mâu thuẫn, hiển thị từng giá trị cạnh dẫn chứng tương ứng. |

Người duyệt chọn thao tác phù hợp với kết quả đối chiếu.

- **Sửa và lưu nháp** để chỉnh giá trị, thêm hoặc bỏ dẫn chứng và ghi chú nếu cần. CMS lưu giá trị trước và sau cùng tài khoản đã sửa.
- **Yêu cầu bổ sung** để trả hồ sơ cho người xử lý, kèm mục cần làm rõ và lý do. Lần gửi lại tạo phiên bản mới để người duyệt nhìn thấy phần đã thay đổi.
- **Duyệt và đưa vào hệ thống** để xác nhận đúng phiên bản đang mở. Nếu một người khác vừa sửa, CMS yêu cầu mở phiên bản mới nhất trước khi duyệt.

**Ví dụ minh họa.** Đề án tháng 3 ghi 80 chỉ tiêu cho chương trình A. Phụ lục tháng 5 điều chỉnh lên 95. Màn duyệt hiển thị cả hai số cùng số trang. Người duyệt chọn 95, gắn phụ lục làm căn cứ và lưu lý do. Nếu trường chưa công bố học phí, người duyệt có thể giữ `null` và ghi chú về nguồn đã kiểm tra.

## 3. Hướng dẫn đầu vào, đầu ra và xét duyệt

AI nhận mã trường, cơ sở, năm, nội dung nguồn chính thức và danh mục mã Bộ của mùa tương ứng. Mỗi phần tài liệu có mã nguồn và vị trí để AI trích dẫn lại. Mẫu JSON và schema mô tả ba nhánh dữ liệu, kiểu của từng trường, cách biểu diễn giá trị trống và các khóa dùng để liên kết chương trình, diện, tổ hợp và công thức.

Ví dụ, nếu một diện xếp hạng bằng tổng điểm thi tốt nghiệp THPT và IELTS chỉ mang lại điểm thưởng, AI đề xuất mã `"100"`, lưu điểm thưởng riêng và trích đoạn mô tả cách xét. Nếu trường chỉ nêu tên diện và chưa công bố cách xếp hạng, AI có thể trả `null`, giải thích điều còn thiếu ở `ghi_chu`. Cả hai kết quả đều có thể lưu để người duyệt xem.

- Nguồn làm căn cứ phải đúng trường, cơ sở và năm áp dụng. Điểm chuẩn lịch sử có năm và nguồn riêng. Nguồn thứ cấp chỉ dùng để lần tới tài liệu gốc.
- AI đối chiếu mã xét tuyển và các liên kết giữa `dats_tuyen_sinh.dats_chuong_trinh_dao_tao` và `quy_tac_xet_tuyen.chuong_trinh`. Kiểm tra thêm chỉ tiêu theo đúng phạm vi, mã cơ sở, tổ hợp, tham chiếu công thức, loại điểm, năm và thang điểm.
- Đối chiếu phương thức và phương án theo hai chiều. Nếu một phương thức có nhiều công thức hoặc các phương thức dùng chung mã Bộ, có thể khai `phuong_an[].ma_phuong_thuc_cua_truong` để chỉ rõ dòng áp dụng. Các phương án đã đối chiếu dùng đúng dòng đó khi ghi vào MySQL.
- Khi công thức đã có giá trị nhưng còn thiếu dẫn chứng, AI rà lại các phần tài liệu theo lô. Trên màn thu thập có thể theo dõi số trường đã rà và dừng trước lô kế tiếp.
- Từng diện, công thức và dòng điểm chuẩn dùng danh mục mã Bộ của năm xét tuyển. Mùa 2026 dùng 19 mã. Mùa 2027 dùng 11 mã theo Phụ lục V. Khi một trang nhắc lại điểm năm trước, dẫn chứng cần xác định được năm của dòng điểm và giữ URL công bố. [Công văn 2304/BGDĐT-GDĐH năm 2026](https://xaydungchinhsach.chinhphu.vn/toan-van-cong-van-2304-bgddt-gddh-huong-dan-tuyen-sinh-dai-hoc-cao-dang-2026-119260505052505936.htm) · [Thông tư 95/2026/TT-BGDĐT cho mùa 2027](https://vanban.chinhphu.vn/?classid=1&docid=220267&pageid=27160)
- AI xác định mã Bộ theo từng diện, ghi rõ mã do trường công bố hoặc do AI suy luận, kèm trích dẫn và lý do. AI đọc vai trò thực tế của từng thành phần trong cách xét của trường. Ví dụ, chứng chỉ có thể là căn cứ xếp hạng, điều kiện, điểm cộng hoặc dùng thay một môn. Nếu chưa đủ căn cứ, AI giữ `null` và ghi mã ứng viên. Khi suy luận mã `500` cho năm 2026, AI nêu cơ chế xét và lý do các mã cụ thể chưa phù hợp. Chỉ đánh dấu mã đã công bố khi nguồn chính thức nêu mã cho đúng diện.
- AI đọc bảng điểm theo mã xét tuyển, năm, diện và tổ hợp. AI tự xác định điểm trúng tuyển gốc, thang điểm, cột quy đổi và vị trí còn thiếu. Màn duyệt hiển thị số dòng AI đề xuất, số dòng có dẫn chứng điểm đang được chọn và các vị trí AI chưa xác minh. Có trạng thái riêng khi AI chưa rà hết tài liệu.
- AI đánh giá phạm vi bảng mã, các đợt tuyển và cách phân bổ chỉ tiêu theo từng trường. Backend kiểm tra cấu trúc nhập, tham chiếu dữ liệu và đối chiếu trích dẫn với nguồn đã tải. Người duyệt quyết định nhập bản chốt.
- AI được hướng dẫn dùng `null` cho giá trị chưa rõ và `[]` khi chưa có bản ghi. Người duyệt có thể giữ, sửa hoặc trả lại đề xuất, kể cả khi còn thiếu trích dẫn hay các nguồn mâu thuẫn. CMS hiển thị các cảnh báo đó để tham khảo. Dữ liệu chốt để nhập phải đúng cấu trúc, kiểu và các liên kết cần cho cơ sở dữ liệu.
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
