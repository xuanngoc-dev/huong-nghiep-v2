# Import đầy đủ dữ liệu tuyển sinh một trường, một năm

File mẫu: [`mau_import_day_du.json`](mau_import_day_du.json). File này được test import thật mỗi lần chạy test
backend (`tests/test_import_day_du.py`), nên luôn đúng cấu trúc. Toàn bộ số liệu trong mẫu là **dữ liệu ví dụ**.

Một file gồm **mọi bảng của đề án, trừ danh mục `dm_*`**:

- 23 bảng `dats_*`: đề án, cơ sở, website, liên hệ, chương trình, kế hoạch, phương thức, tổ hợp của phương thức, nhân
  sự, cơ sở vật chất, quy mô, việc làm, trình độ ngành, đối tượng, điều kiện, tiêu chí, điểm cộng, phân bổ, hồ sơ,
  quy đổi ngưỡng / điểm trúng tuyển, chính sách xét tuyển thẳng / ưu tiên.
- Khối `quy_tac_xet_tuyen`: các bảng `xt_*` (bảng quy đổi, công thức, phương án, nhóm điều kiện, điểm cộng),
  `dats_hoc_phi`, `xt_diem_chuan`, tổ hợp riêng của trường.

## Cách gửi

**Giao diện:** Đề án tuyển sinh → Thêm → Dán JSON / Chọn file. Trường và năm lấy từ `thong_tin_import`.

**API:** `POST /api/v1/de-an-tuyen-sinh/import`

```json
{ "ma_truong": "BKA", "nam_tuyen_sinh": 2027, "du_lieu": { ...nội dung file mẫu... } }
```

- Cả file ghi trong **một transaction**: lỗi ở bất kỳ đâu (kể cả khối quy tắc) thì không ghi gì, trả 400 với `detail`
  nêu dòng lỗi.
- Mỗi trường một đề án mỗi năm: đã có đề án năm đó thì bị từ chối (xóa đề án cũ trước khi nhập lại).
- Có khối `quy_tac_xet_tuyen` thì **chỉ quản trị viên** được gửi (403 nếu không phải).
- Kết quả: `{de_an_id, counts: {bảng dats_: số dòng}, quy_tac: {lich_su_id, so_dong, canh_bao, quy_dinh_chua_mo_hinh_hoa} | null}`.

## Cấu trúc

```
{
  thong_tin_import: { ma_truong, nam_tuyen_sinh, xu_ly_khi_da_ton_tai: "tu_choi" }
  dats_tuyen_sinh: {                       ← object, các bảng con lồng bên trong
    ...cột đề án
    dats_tru_so[]          (id tự đặt trong file để chương trình / cơ sở vật chất tham chiếu: co_so_id)
    dats_website[], dats_lien_he_tuyen_sinh[]
    dats_chuong_trinh_dao_tao[] {
      ...cột chương trình
      dats_ke_hoach_tuyen_sinh[], dats_trinh_do_nganh[], dats_quy_mo_dao_tao[]
      dats_quy_doi_nguong_dau_vao[], dats_quy_doi_diem_trung_tuyen[]
      dats_phuong_thuc[] {
        ...cột phương thức
        dats_phuong_thuc_to_hop[]
        dats_dieu_kien_du_tuyen[], dats_tieu_chi_xet_tuyen[], dats_diem_cong[],
        dats_quy_tac_phan_bo[], dats_ho_so_du_tuyen[]
      }
    }
    dats_nhan_su[], dats_co_so_vat_chat[], dats_quy_mo_dao_tao[], dats_ty_le_viec_lam[],
    dats_doi_tuong_du_tuyen[], dats_chinh_sach_xet_tuyen_thang[], dats_chinh_sach_uu_tien_xet_tuyen[]
    (dieu_kien / tieu_chi / diem_cong / phan_bo / ho_so đặt ở đây nếu áp dụng chung cả đề án)
  }
  quy_tac_xet_tuyen: { ...file chuẩn quy tắc, xem de_an_xet_tuyen.schema.json }
}
```

- Bảng con lồng trong bản ghi cha tự nhận khóa ngoại (`de_an_id`, `de_an_chuong_trinh_id`, `de_an_phuong_thuc_id`).
  Đặt bảng ở cấp nào thì phạm vi áp dụng là cấp đó.
- Bảng nhiều dòng ghi một object thì được hiểu là mảng một phần tử. `dats_chinh_sach_uu_tien_xt` = tên viết tắt của
  `dats_chinh_sach_uu_tien_xet_tuyen`.
- **Id của mọi bản ghi do CSDL tự sinh**, không lấy theo file. `id` trong file không bị kiểm tra (trùng, thiếu, sai
  kiểu đều được), chỉ dùng khi một dòng khác tham chiếu tới nó bằng khóa ngoại ghi tay (`co_so_id`, hoặc
  `de_an_chuong_trinh_id` / `de_an_phuong_thuc_id` của bảng không lồng trong cha). Chỉ khi đó id được tham chiếu phải
  có và không trùng trong bảng của nó. Bảng lồng trong bản ghi cha không cần id. `de_an_id` luôn là đề án đang import.
- Không ghi `tao_luc`, `cap_nhat_luc`; `nam_tuyen_sinh` ở các bảng con luôn lấy theo năm import. Cột bỏ trống nhận
  `null` (hoặc giá trị mặc định của CSDL).
- `dats_tuyen_sinh.trang_thai_xet_tuyen`: 0 chưa chuẩn hóa, 1 thử nghiệm, 2 đang áp dụng. Nên import ở **1** rồi chạy
  thử trước khi chuyển 2 (xem `QUY_TRINH_DUA_TRUONG_VAO.md`).

### Tham chiếu danh mục bằng mã

Id danh mục khác nhau giữa các môi trường; dùng mã:

| Cột id | Khóa mã thay thế | Danh mục |
|---|---|---|
| `nganh_dao_tao_id` | `ma_nganh` | `dm_nganh_dao_tao.ma_nganh` |
| `tinh_thanh_id` (cơ sở) | `ma_tinh` | `dm_tinh_thanh.ma_tinh` |
| `phuong_thuc_nguon_id` / `phuong_thuc_dich_id` | `ma_phuong_thuc_nguon` / `ma_phuong_thuc_dich` | `dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc` |
| `to_hop_nguon_id` / `to_hop_dich_id` | `ma_to_hop_nguon` / `ma_to_hop_dich` | `dm_to_hop_mon_hoc.ma_to_hop` |
| `dats_phuong_thuc_to_hop.to_hop_id` | `ma_to_hop` | `dm_to_hop_mon_hoc.ma_to_hop` |
| `dats_phuong_thuc.to_hop_mon_hoc` | mảng mã, ví dụ `["A00", "A01"]`; `null` = mọi tổ hợp | |
| `dats_dieu_kien_du_tuyen.doi_tuong_du_tuyen_id` | `ma_doi_tuong_du_tuyen` | `dats_doi_tuong_du_tuyen.ma_doi_tuong` trong cùng file |

Ghi cả id và mã thì id được dùng. Mã không có trong danh mục → 400.

**Phương thức không có mã của Bộ** (`dats_phuong_thuc.ma_phuong_thuc_cua_bo`, `quy_tac_xet_tuyen.cong_thuc[].ma_phuong_thuc_cua_bo`
bỏ trống): dùng `ma_phuong_thuc_cua_truong` nếu mã đó có trong danh mục phương thức của Bộ, không thì là **`500`**
(Sử dụng phương thức khác). Ghi mã của Bộ nhưng mã không có trong danh mục vẫn báo lỗi.

## Khối `quy_tac_xet_tuyen`

Đúng cấu trúc file chuẩn (`de_an_xet_tuyen.schema.json`, mẫu `mau_BKA_2026.json`, `mau_NTH_2026.json`); kiểm tra
riêng được bằng `python kiem_tra_de_an.py <file>` sau khi tách khối này ra file. `ma_truong`, `nam_tuyen_sinh`,
`phien_ban`, `de_an` bỏ trống thì lấy từ file chính; nếu có thì phải khớp trường, năm import.

Khối này **khớp** với phần `dats_*` vừa nhập:

| Quy tắc | Khớp với | Theo |
|---|---|---|
| `co_so[]` | `dats_tru_so` | `ten_co_so` giống hệt |
| `chuong_trinh[]` | `dats_chuong_trinh_dao_tao` | `ma_xet_tuyen` + `ten_chuong_trinh` giống hệt (hoặc chỉ `ma_xet_tuyen` nếu mã là duy nhất) |

Không khớp thì hệ thống tạo thêm bản ghi tối thiểu và trả cảnh báo trong `quy_tac.canh_bao`. Hãy sửa tên cho khớp
rồi import lại. Từ khối quy tắc, chương trình nhận thêm `nganh_dao_tao_id` (theo `ma_nganh`), `co_so_id`,
`chi_tieu_tuyen_sinh`; cơ sở nhận tỉnh (theo `ma_tinh`).

| Phần trong khối | Ghi vào |
|---|---|
| `to_hop_rieng[]` | `dm_to_hop_mon_hoc` (mã gắn tiền tố trường: `K01` → `BKA-K01`) |
| `bang_quy_doi[]` | `xt_bang_quy_doi`, `xt_bang_quy_doi_chi_tiet` |
| `cong_thuc[]` (`he_so_mon`, `thanh_phan`, `dieu_kien`) | `xt_cong_thuc`, `xt_cong_thuc_he_so_mon`, `xt_cong_thuc_thanh_phan`, `xt_nhom_dieu_kien`, `xt_dieu_kien` |
| `dieu_kien_chung[]`, `chuong_trinh[].dieu_kien_rieng[]` | `xt_nhom_dieu_kien`, `xt_dieu_kien` |
| `diem_cong[]` | `xt_diem_cong` |
| `chuong_trinh[].phuong_an[]` | `xt_phuong_an` (một dòng cho mỗi công thức × tổ hợp) |
| `chuong_trinh[].hoc_phi` | `dats_hoc_phi` |
| `diem_chuan[]` | `xt_diem_chuan` (thay điểm chuẩn cùng trường, cùng năm) |

Kiểu tính công thức: `TO_HOP_MON` (tổng môn theo tổ hợp, cần `nguon_diem_mon` và `to_hop` ở phương án),
`THANH_PHAN` (bài thi / chứng chỉ quy đổi), `CHI_DIEU_KIEN` (xét thẳng, chỉ xét điều kiện), `THU_CONG` (hệ thống
không tính điểm; bắt buộc có ít nhất một nhóm `dieu_kien`).

Cập nhật riêng quy tắc của đề án đã có: tab "Quy tắc xét tuyển" → Import (cùng cấu trúc khối này, đủ `ma_truong`,
`nam_tuyen_sinh`, `phien_ban`, `de_an`).

### Chuẩn hóa tự động khối quy tắc

Trước khi kiểm tra, backend (`app/services/xet_tuyen_chuan_hoa.py`) tự sửa các cách ghi gần đúng hay gặp để file từ nhiều
nguồn vẫn nhập được. Mỗi chỗ đổi đều có trong `canh_bao` của kết quả import; phần hệ thống chưa tính được thì được ghi
vào `quy_dinh_chua_mo_hinh_hoa` thay vì chặn cả lần import.

| Trong file | Được hiểu là |
|---|---|
| `ma_chi_so: TOT_NGHIEP_HOP_LE` / `TOT_NGHIEP_THPT` | `DA_TOT_NGHIEP_THPT` |
| `ma_chi_so: IELTS` (khoa `IELTS_7`), `TOEFL_IBT`, `TOEFL_ITP` | `DIEM_CHUNG_CHI`, khoa `IELTS` / `TOEFL_IBT_120` / `TOEFL_ITP_L1` |
| `ma_chi_so: DIEM_THI_TOAN_2026`, `DIEM_HOC_BA_TOAN` | `DIEM_THI_THPT` / `DIEM_HOC_BA_TB`, khoa `TOAN` |
| `THANH_TICH`, khoa `HSGQG_NHAT` `= 1` (`_NHI`, `_BA`, `_KK`) | `THANH_TICH`, khoa `HSG-QG` `= 1` (2, 3, 4) |
| Mã danh mục khác dấu `-`/`_` (`VACT`) | Mã khớp duy nhất trong danh mục (`V-ACT`) |
| Thành phần `CHUNG_CHI` không có bảng quy đổi nhưng là bài thi trong danh mục (SAT, ACT) | `BAI_THI` |
| Thành phần không tính được (nguồn lạ, mã bài thi không có trong danh mục) | Công thức thành `THU_CONG` (hệ thống chưa tự tính điểm) |
| `kieu_tinh` lạ | `THU_CONG` |
| `nguon_diem_mon` gần đúng (`HOC_BA_THPT_VA_CHUNG_CHI`) | `HOC_BA` / `THI_THPT`, phần còn lại ghi chưa mô hình hóa |
| `thay_ngoai_ngu` khác `KHONG` nhưng thiếu bảng quy đổi | `KHONG` |
| `hoc_phi` có `hoc_phi_tu: null` | Dùng `hoc_phi_den`; cả hai trống thì bỏ khối học phí |
| Điều kiện / điểm cộng dùng chỉ số chưa có (ví dụ tổng điểm tổ hợp) | Bỏ qua, ghi chưa mô hình hóa; nhóm không còn điều kiện thì bỏ nhóm |
| `CHI_DIEU_KIEN` / `THU_CONG` chưa có nhóm `dieu_kien` | Chỉ cảnh báo; hệ thống không xét phương thức đó |

Không đoán khi có nhiều khả năng (ví dụ `SPT` ứng với nhiều bài thi `SPT_*`). Bỏ một điều kiện bắt buộc khiến hệ
thống xét rộng hơn đề án thật, nên cần đọc cảnh báo sau khi import.
