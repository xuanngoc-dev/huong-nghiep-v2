# Hướng dẫn triển khai: xét tuyển tính toán được và tìm trường phù hợp

Tài liệu này dành cho đội backend (Python) và frontend (Vue). Thiết kế chi tiết của các bảng nằm ở `THIET_KE.md`; ở đây chỉ nói **làm gì, theo thứ tự nào**.

**Giả định, cần đội kiểm lại.** Tôi không có mã nguồn backend và frontend, chỉ có các file dump CSDL. Từ dump suy ra được: MySQL 5.7.44, migration bằng Alembic (`alembic_version = 20261113_0051`). Web framework, tên thư mục, cách đặt route và thư viện state của Vue thì tôi không biết, nên các đường dẫn và tên hàm dưới đây là đề xuất.

## 1. Bộ file bàn giao

| File | Vai trò |
|---|---|
| `01_schema.sql` | 26 bảng mới + cột `dats_tru_so.tinh_thanh_id` |
| `02_thu_tuc.sql` | Hàm, 3 thủ tục, view `v_xt_ket_qua_truong` |
| `03_du_lieu_danh_muc.sql` | Danh mục chỉ số, chi tiết tổ hợp môn, bộ tiêu chí mặc định |
| `04_du_lieu_ftu_bka_2026.sql` | Quy tắc 2026 của FTU và BKA (dữ liệu tham chiếu để so với importer) |
| `05_vi_du_truy_van.sql` | Hồ sơ thử và truy vấn mẫu, chỉ dùng ở môi trường thử |
| `chay_sql.py` | Tách file `.sql` thành câu lệnh để chạy trong Alembic |
| `chuan_du_lieu/de_an_xet_tuyen.schema.json` | **Cấu trúc JSON chuẩn** mỗi trường phải theo |
| `chuan_du_lieu/danh_muc_ma.json` | Các mã hợp lệ (môn, tổ hợp, bài thi, chứng chỉ, thành tích, phương thức, tỉnh, trường, ngành) |
| `chuan_du_lieu/mau_NTH_2026.json`, `mau_BKA_2026.json` | Hai file mẫu thật theo chuẩn |
| `chuan_du_lieu/kiem_tra_de_an.py` | Kiểm tra một file đề án trước khi nạp |
| `test_xet_tuyen.html` | Trang thử độc lập; có bản JavaScript của logic tính điểm |

## 2. Thứ tự triển khai

1. Migration tạo bảng, hàm, thủ tục, dữ liệu nền (mục 3).
2. Viết importer nạp file JSON chuẩn vào `xt_*` và chạy với hai file mẫu (mục 4).
3. API hồ sơ học sinh và chuyển dữ liệu cũ từ `nguoi_dung_thong_tin` (mục 5.1, 5.2).
4. API đánh giá và tra cứu kết quả (mục 5.3, 5.4).
5. Màn hình Vue (mục 6).
6. Bộ kiểm thử hồi quy (mục 7).
7. Bổ sung dữ liệu còn thiếu (mục 8). Bước này không chặn việc viết code nhưng chặn việc ra kết quả có nghĩa.

## 3. Database

### 3.1. Migration

Tạo một revision Alembic nối sau `20261113_0051`. Driver MySQL của Python không hiểu `DELIMITER` và không chạy nhiều câu trong một lần gọi, nên dùng `chay_sql.py` để tách (đã thử: file 01 ra 28 câu, file 02 ra 10 câu, các thân thủ tục còn nguyên).

```python
# alembic/versions/xxxx_xet_tuyen.py
from alembic import op
from pathlib import Path
from chay_sql import doc_cau_lenh          # chép chay_sql.py vào nơi import được

SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "xet_tuyen"   # nơi đặt các file .sql

def _chay(ten_file):
    conn = op.get_bind()
    for cau in doc_cau_lenh(SQL_DIR / ten_file):
        conn.exec_driver_sql(cau)          # KHÔNG dùng sa.text(): thân thủ tục có ':=' sẽ bị hiểu là tham số

def upgrade():
    for f in ("01_schema.sql", "02_thu_tuc.sql", "03_du_lieu_danh_muc.sql"):
        _chay(f)

def downgrade():
    conn = op.get_bind()
    conn.exec_driver_sql("DROP VIEW IF EXISTS v_xt_ket_qua_truong")
    for p in ("sp_xt_danh_gia", "sp_xt_tinh_diem", "sp_hs_cap_nhat_chi_so"):
        conn.exec_driver_sql(f"DROP PROCEDURE IF EXISTS {p}")
    conn.exec_driver_sql("DROP FUNCTION IF EXISTS fn_xt_so_sanh")
    for t in ("xt_ket_qua_chuong_trinh", "xt_ket_qua_phuong_an", "xt_lan_danh_gia",
              "xt_muc_phu_hop", "xt_tieu_chi_phu_hop", "xt_bo_tieu_chi",
              "dats_hoc_phi", "xt_diem_chuan", "xt_diem_cong", "xt_dieu_kien", "xt_nhom_dieu_kien",
              "xt_phuong_an", "xt_cong_thuc_thanh_phan", "xt_cong_thuc_he_so_mon", "xt_cong_thuc",
              "xt_bang_quy_doi_chi_tiet", "xt_bang_quy_doi",
              "hs_chi_so", "hs_tieu_chi_mong_muon", "hs_thanh_tich", "hs_chung_chi",
              "hs_diem_bai_thi", "hs_diem_mon", "hs_ket_qua_nam_hoc", "hs_ho_so", "dm_chi_so_xet_tuyen"):
        conn.exec_driver_sql(f"DROP TABLE IF EXISTS {t}")
    conn.exec_driver_sql("ALTER TABLE dats_tru_so DROP FOREIGN KEY fk_dats_tru_so_tinh_thanh_id")
    conn.exec_driver_sql("ALTER TABLE dats_tru_so DROP COLUMN tinh_thanh_id")
```

Lưu ý khi chạy:

- Tài khoản CSDL cần quyền `CREATE ROUTINE`, `ALTER ROUTINE`, `EXECUTE`, `CREATE VIEW`, `CREATE TEMPORARY TABLES`. Nếu máy chủ bật binlog mà tài khoản không có `SUPER`, tạo hàm sẽ báo lỗi 1418; khi đó nhờ quản trị bật `log_bin_trust_function_creators`.
- File 01 dùng `CREATE TABLE IF NOT EXISTS` nhưng câu `ALTER TABLE dats_tru_so` thì không chạy lại được.
- File 03 xóa các dòng trong `dm_to_hop_mon_hoc_chi_tiet` của tổ hợp không dựng đủ 3 vị trí. Bảng này hiện rỗng nên không mất gì; nếu sau này đã nhập tay thì xem lại câu `DELETE` đó.
- Kết nối phải dùng `utf8mb4` với collation `utf8mb4_unicode_ci` (các file đã có `SET NAMES` ở đầu). Sai collation sẽ gặp lỗi "Illegal mix of collations".

Sau migration, khai báo model SQLAlchemy cho 26 bảng (để `alembic revision --autogenerate` các lần sau không đòi xóa chúng). Tên cột lấy đúng theo `01_schema.sql`.

### 3.2. Sửa dữ liệu hiện có

| Việc | Lý do |
|---|---|
| Rà `dm_doi_tuong_uu_tien` theo Phụ lục II Thông tư 06/2026 | Bảng đang có 01–04 cộng 2,0 và 05–07 cộng 1,0; Thông tư quy định 01–03 cộng 2,0 và 04–06 cộng 1,0. Thủ tục lấy mức cộng từ bảng này |
| Điền `dats_chuong_trinh_dao_tao.nganh_dao_tao_id` | Đang NULL ở cả 245 chương trình; thiếu thì tiêu chí Ngành không chấm |
| Điền `dm_truong.ma_tinh_thanh` | Đang trống; thủ tục tạm nối theo `ten_tinh_thanh` |
| Không đổi tên nhóm `dm_mon_hoc.nhom_mon = 'Ngoại ngữ'` | Thủ tục dựa vào chuỗi này để nhận biết môn ngoại ngữ |

## 4. Cấu trúc JSON chuẩn và importer

### 4.1. Quy ước của file chuẩn

Mỗi file là một trường, một năm. Mọi tham chiếu dùng **mã**, không dùng id. Sơ đồ các khối:

```
phien_ban, ma_truong, nam_tuyen_sinh, de_an{}
co_so[]            cơ sở đào tạo + mã tỉnh
to_hop_rieng[]     tổ hợp trường tự định nghĩa (ví dụ K01)
bang_quy_doi[]     bảng quy đổi chứng chỉ / bài thi, mỗi bảng có muc[]
cong_thuc[]        cách tính điểm; kèm he_so_mon[], thanh_phan[], dieu_kien[]
dieu_kien_chung[]  nhóm điều kiện cho mọi công thức, mọi chương trình
diem_cong[]        điểm thưởng / xét thưởng / khuyến khích (mức theo thang 30)
chuong_trinh[]     mã xét tuyển, cơ sở, học phí, phuong_an[], dieu_kien_rieng[]
diem_chuan[]       điểm chuẩn các năm trước
```

Ba quy tắc người nhập hay sai:

- **Tách công thức** khi khác thang điểm, khác hệ số môn hoặc khác ngưỡng, kể cả cùng một phương thức. FTU có 12 công thức chỉ cho thi THPT và học bạ.
- **Điều kiện**: các nhóm phải cùng đạt; trong một nhóm (`mot_trong`) chỉ cần một dòng đạt. `ten_nhom` viết dưới dạng lý do không đạt vì nó được hiển thị cho học sinh.
- **Hệ số là phân số** (4/3, 3/350) phải ghi dạng thập phân đủ 8 chữ số: `1.33333333`, `0.00857143`. Khi viết SQL cũng vậy: `3 / 350` trong MySQL chỉ giữ 4 chữ số và làm lệch kết quả (tôi đã mắc lỗi này trong file 04 và đã sửa).

Người nhập kiểm tra file trước khi gửi:

```
pip install jsonschema
python chuan_du_lieu/kiem_tra_de_an.py chuan_du_lieu/mau_NTH_2026.json
```

Script kiểm tra ba lớp: cấu trúc theo schema, tham chiếu nội bộ, mã danh mục. Nó cũng cảnh báo khi điểm tối đa tính theo hệ số không khớp `thang_diem`. Khi danh mục trong CSDL thay đổi, xuất lại `danh_muc_ma.json` từ các bảng `dm_*`.

### 4.2. Importer (chưa viết, cần làm)

Đề xuất: `POST /admin/xet-tuyen/de-an/import` nhận file JSON, hoặc lệnh CLI. Chạy trong **một transaction**, thay toàn bộ dữ liệu `xt_*` của đề án đó.

Ánh xạ:

| Khối JSON | Bảng đích | Ghi chú |
|---|---|---|
| `ma_truong`, `nam_tuyen_sinh`, `de_an` | `dats_tuyen_sinh` | Tìm theo `(ma_truong, nam_tuyen_sinh)`, chưa có thì tạo |
| `co_so[]` | `dats_tru_so` | Khớp theo `ten_co_so`; `ma_tinh` → `tinh_thanh_id` |
| `to_hop_rieng[]` | `dm_to_hop_mon_hoc` + `dm_to_hop_mon_hoc_chi_tiet` | Chỉ số của vị trí (từ 1) ghi vào `thu_tu_mon`; các môn cùng vị trí dùng chung một số |
| `bang_quy_doi[]`, `muc[]` | `xt_bang_quy_doi`, `xt_bang_quy_doi_chi_tiet` | `dat_nguong` mặc định 1 |
| `cong_thuc[]` | `xt_cong_thuc` | `dang_dung` → `trang_thai`; `he_so_mon[]` → `xt_cong_thuc_he_so_mon`; `thanh_phan[]` → `xt_cong_thuc_thanh_phan` |
| `cong_thuc[].dieu_kien[]` | `xt_nhom_dieu_kien` (có `cong_thuc_id`) + `xt_dieu_kien` | |
| `dieu_kien_chung[]` | `xt_nhom_dieu_kien` (cả hai khóa NULL) | |
| `diem_cong[]` | `xt_diem_cong` | |
| `chuong_trinh[]` | `dats_chuong_trinh_dao_tao` | Khớp theo `(de_an_id, ma_xet_tuyen, ten_chuong_trinh)`, chưa có thì tạo; cập nhật `co_so_id`, `nganh_dao_tao_id`, `chi_tieu_tuyen_sinh` |
| `chuong_trinh[].hoc_phi` | `dats_hoc_phi` | |
| `chuong_trinh[].phuong_an[]` | `xt_phuong_an` | Công thức theo tổ hợp: mỗi tổ hợp một dòng. Kiểu khác: một dòng, `to_hop_id` NULL |
| `chuong_trinh[].dieu_kien_rieng[]` | `xt_nhom_dieu_kien` (có `de_an_chuong_trinh_id`, có thể kèm `cong_thuc_id`) | |
| `diem_chuan[]` | `xt_diem_chuan` | Xóa theo `(ma_truong, nam_tuyen_sinh)` rồi chèn |

Các bước:

1. Kiểm tra bằng `jsonschema` và gọi lại hàm `kiem_tra()` của `kiem_tra_de_an.py` với danh mục đọc từ CSDL. Có lỗi thì từ chối cả file.
2. Dựng bảng tra mã → id cho môn, tổ hợp, bài thi, chứng chỉ, tỉnh, ngành.
3. Xóa dữ liệu cũ của đề án theo đúng thứ tự ở mục 0 của file 04: `xt_phuong_an`, `xt_diem_cong`, `xt_nhom_dieu_kien`, `xt_cong_thuc`, `xt_bang_quy_doi`, `dats_hoc_phi`.
4. Chèn theo thứ tự: cơ sở → tổ hợp riêng → bảng quy đổi → công thức (kèm hệ số, thành phần) → chương trình → phương án → điều kiện → điểm cộng → học phí → điểm chuẩn.
5. Commit.

Xóa `xt_phuong_an` kéo theo xóa `xt_ket_qua_phuong_an` của các lần đánh giá cũ (khóa ngoại `ON DELETE CASCADE`), nên kết quả cũ của trường đó mất sau mỗi lần import lại. Đây là chủ ý: kết quả tính theo quy tắc cũ không còn đúng.

**Tiêu chí nghiệm thu importer**: nạp `mau_NTH_2026.json` và `mau_BKA_2026.json` vào CSDL trống phần `xt_*`, rồi so số dòng với kết quả của file 04: FTU 26 công thức, 770 phương án, 51 nhóm điều kiện, 10 điểm cộng; BKA 7 công thức, 501 phương án, 32 nhóm điều kiện.

## 5. Backend

### 5.1. API hồ sơ học sinh

Các bảng `hs_*` thay cho JSON trong `nguoi_dung_thong_tin.trinh_do_hoc_van`. Đề xuất một tài nguyên gộp, ghi đè toàn bộ hồ sơ mỗi lần lưu:

```
GET  /api/ho-so-xet-tuyen            danh sách hồ sơ của người dùng (hoặc theo ma_thiet_bi với khách)
POST /api/ho-so-xet-tuyen            tạo
GET  /api/ho-so-xet-tuyen/{id}
PUT  /api/ho-so-xet-tuyen/{id}       thay toàn bộ
```

Thân request, cũng là dạng frontend giữ trong state:

```json
{
  "ten_ho_so": "Hồ sơ chính",
  "nam_tot_nghiep": 2026, "da_tot_nghiep": true, "chuong_trinh_thpt": "GDPT_2018",
  "he_chuyen": true, "ma_mon_chuyen": "TOAN",
  "ma_tinh": "01", "ma_khu_vuc_uu_tien": "KV2-NT", "ma_doi_tuong_uu_tien": null,
  "ngan_sach_hoc_phi_nam": 60000000,
  "ket_qua_nam_hoc": [ { "lop": 10, "diem_tb_chung": 8.9, "hoc_luc": 4, "ren_luyen": 4 } ],
  "diem_mon": [
    { "ma_mon": "TOAN", "nguon_diem": "THI_THPT", "diem": 9.0, "nam": 2026, "la_du_kien": false },
    { "ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 10, "hoc_ky": 0, "diem": 9.2 }
  ],
  "diem_bai_thi": [ { "ma_bai_thi": "HSA", "nam_thi": 2026, "diem": 112, "phan_tu_chon": "KHOA_HOC" } ],
  "chung_chi": [ { "ma_chung_chi": "IELTS", "diem": 7.0, "cap_do": null, "ngay_het_han": "2027-12-01" } ],
  "thanh_tich": [ { "ma_thanh_tich": "HSG-TINH", "ma_mon": "TOAN", "muc_giai": 2, "nam_dat_giai": 2026, "lop": 12 } ],
  "mong_muon": [ { "loai": "TINH_THANH", "gia_tri": "01" }, { "loai": "NGANH", "gia_tri": "7480101" } ]
}
```

Kiểm tra phía server: điểm môn trong [0; 10]; `hoc_luc`, `ren_luyen` trong {1, 2, 3, 4}; `muc_giai` trong {1, 2, 3, 4, 9}; `hoc_ky = 0` nghĩa là cả năm; mã phải tồn tại trong danh mục. Khi lưu: xóa các dòng con rồi chèn lại trong một transaction. Không cần tự cập nhật `hs_chi_so`, thủ tục đánh giá làm việc đó.

Quy ước mã hóa, dùng chung cho backend và frontend:

| Trường | Giá trị |
|---|---|
| `hoc_luc`, `ren_luyen` | 4 Tốt/Giỏi · 3 Khá · 2 Đạt/Trung bình · 1 Chưa đạt/Yếu |
| `muc_giai` | 1 Nhất/Vàng · 2 Nhì/Bạc · 3 Ba/Đồng · 4 Khuyến khích/Tư · 9 chỉ tham gia |
| SAT, ACT, HSA, V-ACT, TSA | ghi vào `diem_bai_thi` |
| IELTS, TOEFL, JLPT, HSK, DELF, VSTEP, A-Level... | ghi vào `chung_chi`; VSTEP ghi số bậc vào `diem` |

### 5.2. Chuyển dữ liệu cũ

Viết một script chạy một lần, đọc `nguoi_dung_thong_tin.trinh_do_hoc_van`:

| Khóa JSON cũ | Đích |
|---|---|
| `diem_thi_thpt_quoc_gia.du_kien.{MA}` | `hs_diem_mon`, `nguon_diem = THI_THPT`, `la_du_kien = 1` |
| `diem_trung_binh_hoc_ba.{lop}.{MA}` | `hs_diem_mon`, `nguon_diem = HOC_BA`, `hoc_ky = 0` |
| `hoc_luc_trung_binh.{lop}` | `hs_ket_qua_nam_hoc.diem_tb_chung` |
| `hanh_kiem.{lop}` (chữ) | `hs_ket_qua_nam_hoc.ren_luyen` theo bảng mã trên |
| `chung_chi_ngoai_ngu[]` | `hs_chung_chi` (`ma` → `ma_chung_chi`, `thanh_tich` → `diem`) |
| `khu_vuc_uu_tien_id`, `doi_tuong_uu_tien_id`, `tinh_thanh_id` | chép sang `hs_ho_so` |

Hai chỗ phải quyết định trước khi chạy: JSON cũ dùng `NN1`, `NN2` thay cho ngôn ngữ cụ thể, còn bảng mới cần đúng môn (`ANH`, `PHAP`...); và JSON cũ không có xếp loại học lực (Tốt/Khá), chỉ có điểm trung bình. Các mã `CN`, `GDDP`, `GDQP`, `GDTC`, `HDTN`, `MYT`, `NHAC`, `TDTTS` không có trong `dm_mon_hoc` và không dùng để xét tuyển, có thể bỏ qua.

### 5.3. Service đánh giá

Có hai cách. **Tôi khuyên dùng cách A trước**, vì thủ tục đã được kiểm thử và chỉ có một nơi chứa logic.

**Cách A: gọi thủ tục.**

```python
from sqlalchemy import text

def chay_danh_gia(db, ho_so_id: int, nam: int, bo_tieu_chi_id: int | None = None,
                  lich_su_tim_truong_id: int | None = None) -> int:
    conn = db.connection()                      # mọi lệnh dưới đây phải chung MỘT kết nối
    conn.execute(text("CALL sp_xt_danh_gia(:hs, :nam, :bo, @xt_lan)"),
                 {"hs": ho_so_id, "nam": nam, "bo": bo_tieu_chi_id})
    lan = conn.execute(text("SELECT @xt_lan")).scalar_one()
    if lich_su_tim_truong_id:
        conn.execute(text("UPDATE xt_lan_danh_gia SET lich_su_tim_truong_id = :ls WHERE id = :lan"),
                     {"ls": lich_su_tim_truong_id, "lan": lan})
    db.commit()
    return lan
```

- Thủ tục dùng bảng tạm và biến phiên, cả hai gắn với kết nối, nên nhiều người chạy cùng lúc không lẫn nhau. Đừng tách lệnh `CALL` và `SELECT @xt_lan` sang hai kết nối của pool.
- Thủ tục báo lỗi `SQLSTATE 45000` khi không có hồ sơ hoặc chưa có bộ tiêu chí; bắt lỗi này và trả 404/409.
- Mỗi lần chạy ghi một dòng `xt_lan_danh_gia` và các dòng kết quả. Với hai trường hiện có là dưới 1.000 dòng; khi có vài trăm trường sẽ là hàng chục nghìn dòng mỗi lần. Cần một job định kỳ xóa các lần cũ (`DELETE FROM xt_lan_danh_gia WHERE tao_luc < ...`, kết quả tự xóa theo), và nên đo thời gian chạy lại khi dữ liệu lớn dần.

**Cách B: viết lại logic bằng Python.** Chọn khi đội không muốn giữ logic trong CSDL hoặc cần tính thử mà không ghi dữ liệu. Bản tham chiếu là khối `//<ENGINE>` trong `test_xet_tuyen.html`, đã cho kết quả trùng với thủ tục trên 986 phương án. Nếu đi cách này, giữ bộ kiểm thử ở mục 7 để hai bản không lệch nhau, và chú ý làm tròn giống thủ tục: điểm gốc 4 chữ số, điểm cộng và ưu tiên 2 chữ số, điểm xét 2 chữ số.

### 5.4. API đánh giá và tra cứu

```
POST /api/xet-tuyen/danh-gia                  { ho_so_id, nam_tuyen_sinh }  ->  { lan_danh_gia_id, thong_ke }
GET  /api/xet-tuyen/danh-gia/{lan}/chuong-trinh   danh sách đã xếp hạng, có lọc và phân trang
GET  /api/xet-tuyen/danh-gia/{lan}/truong         xếp hạng trường
GET  /api/xet-tuyen/danh-gia/{lan}/chuong-trinh/{id}/phuong-an   mọi phương án của một chương trình
GET  /api/xet-tuyen/danh-gia/{lan}/phuong-an      tất cả phương án (gồm không đạt), cho màn hình giải thích
```

Mọi endpoint `GET` phải kiểm tra lần đánh giá thuộc về người gọi (`xt_lan_danh_gia.ho_so_id` → `hs_ho_so.nguoi_dung_id` hoặc `ma_thiet_bi`).

Truy vấn danh sách chương trình, tham số lọc đều tùy chọn:

```sql
SELECT r.thu_hang, r.ma_truong, t.ten_truong, c.id AS chuong_trinh_id, c.ma_xet_tuyen, c.ten_chuong_trinh,
       ct.ma_cong_thuc, ct.ten_cong_thuc, ct.ma_phuong_thuc_cua_bo, th.ma_to_hop,
       r.diem_xet, r.thang_diem, k.diem_chuan_tham_chieu, k.nam_diem_chuan, r.chenh_lech_30,
       r.la_xet_thang, r.diem_kha_nang, r.diem_nganh, r.diem_hoc_phi, r.diem_vi_tri, r.diem_phu_hop, r.xep_loai,
       hp.hoc_phi_tu, hp.hoc_phi_den, COALESCE(t1.ten_tinh, t2.ten_tinh) AS ten_tinh
FROM xt_ket_qua_chuong_trinh r
JOIN xt_ket_qua_phuong_an k ON k.id = r.ket_qua_phuong_an_id
JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
JOIN dats_chuong_trinh_dao_tao c ON c.id = r.de_an_chuong_trinh_id
JOIN dm_truong t ON t.ma_truong = r.ma_truong
LEFT JOIN dm_to_hop_mon_hoc th ON th.id = k.to_hop_id
LEFT JOIN dats_tru_so ts ON ts.id = c.co_so_id
LEFT JOIN dm_tinh_thanh t1 ON t1.id = ts.tinh_thanh_id
LEFT JOIN dm_tinh_thanh t2 ON t2.ten_tinh = t.ten_tinh_thanh
LEFT JOIN (SELECT de_an_chuong_trinh_id, MIN(hoc_phi_tu) AS hoc_phi_tu, MAX(hoc_phi_den) AS hoc_phi_den
           FROM dats_hoc_phi GROUP BY de_an_chuong_trinh_id) hp ON hp.de_an_chuong_trinh_id = c.id
WHERE r.lan_danh_gia_id = :lan
  AND (:tu_khoa IS NULL OR c.ten_chuong_trinh LIKE CONCAT('%', :tu_khoa, '%') OR c.ma_xet_tuyen LIKE CONCAT(:tu_khoa, '%'))
  AND (:ma_truong IS NULL OR r.ma_truong = :ma_truong)
  AND (:ma_tinh IS NULL OR COALESCE(t1.ma_tinh, t2.ma_tinh) = :ma_tinh)
  AND (:xep_loai IS NULL OR r.xep_loai = :xep_loai)
  AND (:chenh_tu IS NULL OR r.chenh_lech_30 >= :chenh_tu)
  AND (:hoc_phi_den IS NULL OR hp.hoc_phi_tu <= :hoc_phi_den)
ORDER BY r.thu_hang
LIMIT :limit OFFSET :offset;
```

Lọc theo phương thức hoặc tổ hợp khác về bản chất: `xt_ket_qua_chuong_trinh` chỉ giữ phương án **tốt nhất** của mỗi chương trình, nên lọc trên bảng này sẽ bỏ sót chương trình mà phương án tốt nhất thuộc phương thức khác. Khi người dùng lọc theo phương thức/tổ hợp, truy vấn `xt_ket_qua_phuong_an` (điều kiện `du_dieu_kien = 1`) rồi lấy dòng tốt nhất mỗi chương trình trong Python, theo thứ tự: chênh lệch lớn hơn, rồi `diem_xet / thang_diem` lớn hơn. Trang thử HTML làm đúng như vậy.

Xếp hạng trường: `SELECT * FROM v_xt_ket_qua_truong WHERE lan_danh_gia_id = :lan ORDER BY diem_truong DESC`.

Dạng trả về của một dòng chương trình (frontend dựa vào đây):

```json
{
  "thu_hang": 3, "ma_truong": "NTH", "ten_truong": "Trường Đại học Ngoại thương",
  "chuong_trinh_id": 139, "ma_xet_tuyen": "NTHKE16", "ten_chuong_trinh": "CT TC Kế toán - Kiểm toán",
  "phuong_an": { "ma_cong_thuc": "FTU_HSA_30", "ten_cong_thuc": "ĐGNL HSA - thang 30", "ma_phuong_thuc": "402", "ma_to_hop": null },
  "diem_xet": 27.87, "thang_diem": 30,
  "diem_chuan": { "diem": 25.5, "nam": 2025 }, "chenh_lech_30": 2.37,
  "la_xet_thang": false,
  "tieu_chi": { "kha_nang": 100, "nganh": null, "hoc_phi": 100, "vi_tri": 100 },
  "diem_phu_hop": 100, "xep_loai": "Rất phù hợp",
  "hoc_phi": { "tu": 28000000, "den": 32000000 }, "ten_tinh": "Hà Nội"
}
```

### 5.5. Nối với chức năng tìm trường hiện có

`tn_lich_su_tim_truong_phu_hop` vẫn giữ vai trò ghi lượt, hạn mức và thanh toán. Khi một lượt tìm bắt đầu: tạo dòng lịch sử như cũ, gọi `chay_danh_gia(..., lich_su_tim_truong_id=...)`, rồi ghi `phien_ban_thuat_toan = 'xt-v1'`, `so_truong_tim_thay`, `so_truong_phu_hop_so_bo` từ `v_xt_ket_qua_truong`. Cột `du_lieu_ket_qua` (JSON) có thể để trống vì kết quả đã nằm trong các bảng `xt_ket_qua_*`. Lượt tìm cũ lọc theo `ma_nganh`; khi các chương trình đã có mã ngành, đưa ngành đó vào `hs_tieu_chi_mong_muon` (loại `NGANH`) trước khi chạy.

## 6. Frontend (Vue)

`test_xet_tuyen.html` là bản mẫu chạy được của toàn bộ luồng; dùng nó để xem bố cục, các cột và cách giải thích điểm. Trang thật gọi API thay vì tự tính.

**Màn hình và component đề xuất**

| Component | Nội dung |
|---|---|
| `HoSoXetTuyenForm` | Form hồ sơ, chia khối: thông tin chung, kết quả từng năm, bảng điểm môn (cột Thi THPT, HB 10, HB 11, HB 12), bài thi, chứng chỉ, thành tích, mong muốn |
| `KetQuaChuongTrinhTable` | Bảng xếp hạng; bấm một dòng mở `PhuongAnChiTiet` |
| `PhuongAnChiTiet` | Mọi phương án của chương trình: điểm gốc, cộng, ưu tiên, điểm xét, trạng thái, lý do |
| `KetQuaTruongTable` | Xếp hạng trường |
| `BoLocKetQua` | Từ khóa, trường, phương thức, tổ hợp, tỉnh, xếp loại, chênh lệch từ, học phí đến |

**Luồng**: lưu hồ sơ (`PUT`) → `POST danh-gia` → nhận `lan_danh_gia_id` → tải danh sách. Lọc và phân trang gọi lại `GET` với cùng `lan_danh_gia_id`, không chạy lại đánh giá. Chỉ chạy lại khi hồ sơ thay đổi.

**Quy tắc hiển thị**

- `diem_phu_hop = null`: hiện nhãn "Chưa có điểm chuẩn tham chiếu", không hiện số 0.
- Tiêu chí nào `null` thì hiện gạch ngang kèm chú thích "chưa có dữ liệu", đừng hiểu là 0 điểm.
- `la_xet_thang = true`: hiện "Đủ điều kiện xét tuyển thẳng" thay cho điểm xét.
- Luôn hiện `diem_xet` kèm `thang_diem` (30, 40 hoặc 100); không so sánh trực tiếp điểm khác thang, dùng `chenh_lech_30`.
- Phương án kiểu `THU_CONG` đủ điều kiện: hiện "Đủ điều kiện nộp hồ sơ, hệ thống chưa tính điểm cho phương thức này".
- Màu xếp loại: Rất phù hợp, Phù hợp (xanh); Có thể cân nhắc (vàng); Ít phù hợp (đỏ); chưa chấm (xám).
- Điểm chuẩn hiện kèm năm, vì đó là mốc của năm trước chứ không phải dự báo.

Danh mục cho các ô chọn (môn, khu vực, đối tượng, bài thi, chứng chỉ, thành tích, tỉnh) lấy từ API danh mục hiện có; danh sách chứng chỉ nên giới hạn ở những mã có trong `xt_bang_quy_doi_chi_tiet` hoặc `xt_dieu_kien` để form gọn.

## 7. Kiểm thử

Chạy `05_vi_du_truy_van.sql` trên CSDL thử để có hai hồ sơ mẫu và điểm chuẩn giả định, rồi kiểm tra các số sau (đã đối chiếu tay và đối chiếu giữa SQL với JavaScript):

| Hồ sơ | Phương án | Kết quả mong đợi |
|---|---|---|
| A | FTU `FTU_THPT_30`, A00 | gốc 26,25 · ưu tiên 0,25 · điểm xét 26,50 |
| A | FTU `FTU_HB_30`, A00 | gốc 27,50 · điểm xét 27,67 · trung bình môn 9,17 |
| A | FTU `FTU_HB_30`, D01 | không đạt: "Trung bình các môn xét 8.93 dưới ngưỡng 9.00" |
| A | FTU `FTU_HSA_30` | gốc 27,72 · điểm xét 27,87 |
| A | FTU `FTU_HB_IT40`, A01 | điểm xét 37,29 trên thang 40 |
| A | BKA `BKA_THPT_K01` | gốc 26,25 · điểm xét 26,50 |
| A | BKA `BKA_TSA` | điểm xét 74,17 trên thang 100 |
| B | FTU `FTU_THPT_30`, A00 | điểm xét 22,25 · không đạt ngưỡng 24 |
| A | tổng số | 890 phương án tính được, 119 chương trình có thể xét |
| B | tổng số | 96 phương án, 44 chương trình |

Nên có ba nhóm test tự động: (1) importer nạp hai file mẫu ra đúng số dòng ở mục 4.2; (2) service đánh giá ra đúng bảng trên; (3) API tra cứu kiểm tra quyền truy cập lần đánh giá của người khác.

Tôi chưa chạy lại file 04 trên MySQL sau khi sửa hệ số V-ACT (từ `3 / 350` thành `0.00857143`) và thay `4 / 3` bằng `1.33333333`. Thay đổi chỉ là hằng số, nhưng hãy chạy lại file 04 một lần và kiểm tra `SELECT he_so_noi_suy FROM xt_bang_quy_doi_chi_tiet WHERE he_so_noi_suy > 0` ra `0.06`, `0.00857143`, `0.1`.

## 8. Dữ liệu còn thiếu

1. **Điểm chuẩn các năm trước** cho từng mã xét tuyển, nhập qua khối `diem_chuan` của file chuẩn. Đây là điều kiện để có điểm phù hợp.
2. **Mã ngành** cho từng chương trình (`ma_nganh`).
3. **Học phí** của BKA và các trường khác.
4. **Đề án của XDA, KSA** và các trường còn lại, chuyển sang file chuẩn.
5. **Các quy định chưa mô hình hóa** của FTU và BKA, liệt kê trong `de_an.ghi_chu` của hai file mẫu và ở đầu file 04.
6. **Duyệt trọng số và các mốc chấm điểm** trong `xt_tieu_chi_phu_hop`, `xt_muc_phu_hop`: hiện là giá trị tôi đề xuất.
