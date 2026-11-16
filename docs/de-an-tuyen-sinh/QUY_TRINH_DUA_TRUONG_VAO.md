# Quy trình đưa một trường vào bộ tính xét tuyển

Bước 5.4 của `KE_HOACH_TRIEN_KHAI.md`. Áp dụng cho mỗi trường, mỗi năm tuyển sinh. Nguyên tắc: **file JSON chuẩn là
nguồn sự thật**; sửa quy tắc là sửa file rồi import lại. Không trường nào được chuyển sang "đang áp dụng" khi chưa có
bộ test hồi quy xanh.

| # | Việc | Ai | Công cụ | Xong khi |
|---|---|---|---|---|
| 1 | Soạn file JSON quy tắc từ đề án gốc | Nhập liệu | `chuan_du_lieu/de_an_xet_tuyen.schema.json`, mẫu `mau_BKA_2026.json`, `mau_NTH_2026.json` | Có file `<MA_TRUONG>_<NAM>.json` |
| 2 | Kiểm tra file | Nhập liệu | `python docs/de-an-tuyen-sinh/chuan_du_lieu/kiem_tra_de_an.py <file>` | Không còn LỖI; CẢNH BÁO đã xem từng dòng |
| 3 | Có đề án và chương trình trong hệ thống | Quản trị | Trang Đề án tuyển sinh (import đề án / sao chép từ năm trước) | Đề án đúng trường, năm; chương trình có mã xét tuyển |
| 4 | Gắn ngành, cơ sở; nhập học phí, điểm chuẩn năm trước | Quản trị | Trang "Gắn ngành & cơ sở", "Trụ sở", "Điểm chuẩn" | Chương trình có mã ngành; điểm chuẩn có ít nhất 1 năm |
| 5 | Import quy tắc, để trạng thái **thử nghiệm** | Quản trị | Chi tiết đề án → tab "Quy tắc xét tuyển" → Import | Import không lỗi; mục "Chưa tính được" đã ghi nhận |
| 6 | Chạy thử trên dữ liệu thật | Quản trị + người hiểu đề án | Tab "Quy tắc xét tuyển" → **Chạy thử** | Đối chiếu tay vài phương án tiêu biểu với đề án gốc: điểm xét, điều kiện, lý do không đạt |
| 7 | Thêm bộ test hồi quy | Lập trình | Thư mục `backend/tests/du_lieu/hoi_quy_xet_tuyen/<MA_TRUONG>_<NAM>/` (xem README trong đó) | `unittest tests.test_hoi_quy_xet_tuyen` xanh, đã commit |
| 8 | Chuyển sang **đang áp dụng** | Chủ dự án duyệt, quản trị thao tác | Tab "Quy tắc xét tuyển" → chọn trạng thái | Lượt tìm trường năm đó dùng bộ tính mới |
| 9 | Đối chiếu CSDL với bộ test | Lập trình | `cd backend && .venv/bin/python -m app.scripts.kiem_tra_bo_test_hoi_quy` | Đề án "đang áp dụng" đều ĐỦ (không THIẾU, không LỆCH) |

## Bước 6–7 chi tiết: từ chạy thử ra bộ test

1. Trong hộp "Chạy thử", dán hồ sơ (dạng `PUT /ho-so-xet-tuyen/cua-toi`), bấm **Lấy hồ sơ của tôi** hoặc **Điền mẫu**
   rồi sửa. Đặt **Ngày tính** cố định `2026-07-01` (hoặc ngày giữa mùa tuyển sinh của năm đó) để hạn chứng chỉ không
   đổi theo ngày chạy test.
2. Cần ít nhất 2 hồ sơ: một hồ sơ đạt nhiều phương án, một hồ sơ trượt ngưỡng / điều kiện. Có ngưỡng (điểm sàn,
   trung bình môn, ngưỡng THPT) thì thêm hồ sơ chạm đúng ngưỡng.
3. Đối chiếu tay. Đúng thì bấm **Tải hồ sơ mẫu** → lưu thành `ho_so/<ten>.json`, **Tải kết quả mong đợi** → lưu thành
   `ket_qua/<ten>.json`.
4. Chép file JSON đã import ở bước 5 thành `de_an.json` (đúng nguyên file, để bước 9 so được mã băm), thêm
   `truong.json` nếu chương trình không khai cơ sở (ví dụ `{"ma_tinh_thanh": "01"}`).
5. Chạy `cd backend && .venv/bin/python -m tests.hoi_quy_xet_tuyen <MA_TRUONG>_<NAM>`: số phương án phải khớp lúc
   chạy thử. Lệch thì thường do danh mục trong test (`tests/du_lieu/xet_tuyen/danh_muc_ma.json`) thiếu mã mà CSDL có,
   hoặc điểm chuẩn trong `de_an.json` khác CSDL; sửa dữ liệu test, không sửa kết quả mong đợi cho khớp.

## Khi đề án thay đổi giữa mùa

- Sửa file JSON → kiểm tra (bước 2) → import lại (bước 5; kết quả đánh giá cũ của đề án tự xóa theo) → chạy thử
  (bước 6) → cập nhật `de_an.json` và kết quả mong đợi trong bộ test, ghi lý do trong commit → bước 9.
- Bước 9 báo LỆCH nghĩa là CSDL đang chạy quy tắc khác file trong bộ test: hoặc quên cập nhật bộ test, hoặc ai đó
  import file khác. Xử lý trước khi kết thúc ngày.

## Theo dõi tiến độ

Trang quản trị "Độ phủ dữ liệu xét tuyển" (bước 5.5): số đề án theo trạng thái, tỷ lệ chương trình có điểm chuẩn,
mã ngành, học phí, và các quy định chưa mô hình hóa theo trường.
