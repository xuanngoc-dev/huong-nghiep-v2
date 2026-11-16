# Bộ test hồi quy xét tuyển nhiều trường

Mỗi thư mục `<MA_TRUONG>_<NAM>` là một trường, một năm. `tests/test_hoi_quy_xet_tuyen.py` chạy mọi thư mục:
import `de_an.json` vào SQLite bằng bộ import thật, chuyển đề án sang "đang áp dụng", nạp quy tắc từ CSDL như khi
chạy thật, tính cho từng hồ sơ rồi so với kết quả mong đợi (từng phương án và thứ tự xếp hạng).

**Trường nào cũng phải có thư mục ở đây và test xanh trước khi chuyển đề án sang "đang áp dụng".**

## Cấu trúc một thư mục

| File | Nội dung |
|---|---|
| `de_an.json` | File chuẩn của trường (theo `docs/de-an-tuyen-sinh/chuan_du_lieu/de_an_xet_tuyen.schema.json`), có khối `diem_chuan` làm mốc |
| `truong.json` | Không bắt buộc. Thông tin `dm_truong` cần cho tiêu chí vị trí khi chương trình không khai cơ sở, ví dụ `{"ma_tinh_thanh": "01"}` |
| `ho_so/<ten>.json` | Hồ sơ mẫu, tên trường theo `HoSoXetTuyen` (`app/services/xet_tuyen/mo_hinh.py`) |
| `ket_qua/<ten>.json` | Kết quả mong đợi của hồ sơ cùng tên: `so_phuong_an`, `so_chuong_trinh`, `phuong_an[]`, `xep_hang[]` |

Danh mục (môn, tổ hợp, bài thi, chứng chỉ, tỉnh) lấy từ `tests/du_lieu/xet_tuyen/danh_muc_ma.json`; điểm ưu tiên khu
vực, đối tượng theo Thông tư 06/2026; bộ tiêu chí như migration `0058`. Ngày tính cố định 2026-07-01.

## Thêm một trường

1. Tạo thư mục `<MA_TRUONG>_<NAM>`, chép file chuẩn của trường vào `de_an.json`, thêm điểm chuẩn năm trước vào `diem_chuan`.
2. Viết ít nhất 2 hồ sơ mẫu trong `ho_so/`: một hồ sơ đạt nhiều phương án, một hồ sơ không đạt ngưỡng hoặc điều kiện.
   Nên có hồ sơ chạm đúng ngưỡng (điểm sàn, trung bình môn, ngưỡng THPT) nếu đề án có ngưỡng.
3. Xem kết quả hiện tại: `cd backend && .venv/bin/python -m tests.hoi_quy_xet_tuyen <MA_TRUONG>_<NAM>`.
4. **Đối chiếu tay** vài phương án tiêu biểu với đề án gốc (điểm xét, điều kiện, lý do không đạt). Chỉ khi đúng mới ghi:
   `.venv/bin/python -m tests.hoi_quy_xet_tuyen <MA_TRUONG>_<NAM> --ghi`.
5. Chạy `.venv/bin/python -B -m unittest tests.test_hoi_quy_xet_tuyen` và commit cả thư mục.

Khi sửa bộ tính mà test của một trường đỏ: xem phương án nào lệch trong thông báo lỗi. Chỉ ghi lại kết quả mong đợi
(`--ghi`) khi đã xác định kết quả mới mới là đúng, và ghi lý do trong commit.

## Trường đang có

| Thư mục | Nguồn kết quả mong đợi |
|---|---|
| `NTH_2026` (FTU) | Bản JavaScript `docs/de-an-tuyen-sinh/test_xet_tuyen.html`, đã đối chiếu với thủ tục MySQL |
| `BKA_2026` | Như trên |

Hồ sơ `A`, `B`, `C` là ba hồ sơ mẫu của trang HTML. Điểm chuẩn trong `de_an.json` là số **giả định** của trang
HTML (không phải điểm chuẩn thật), chỉ dùng để kiểm tra cách chấm điểm phù hợp.

Còn thiếu theo kế hoạch (mục "Bộ trường mẫu cho nghiệm thu"): một trường dùng bài thi đánh giá năng lực riêng, một
trường xét học bạ có ngưỡng, một trường sư phạm, một trường y, một trường có sơ tuyển hoặc thi năng khiếu.
