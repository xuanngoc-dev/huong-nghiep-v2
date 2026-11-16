# Thiết kế dữ liệu xét tuyển: từ điểm của học sinh đến danh sách trường phù hợp có chấm điểm

Áp dụng cho CSDL `huongnghiep` (MySQL 5.7.44). Căn cứ: Thông tư 06/2026/TT-BGDĐT, thông tin tuyển sinh 2026 của ĐH Bách khoa Hà Nội (BKA) và Trường ĐH Ngoại thương (NTH).

## 1. Vì sao cần thêm bảng

Schema hiện có đã đủ **danh mục** (`dm_*`) và **nội dung đề án** (`dats_*`), nhưng phần quyết định việc "học sinh này vào được đâu" đang nằm ở dạng không truy vấn được:

| Thông tin | Đang lưu ở | Vấn đề |
|---|---|---|
| Công thức điểm xét | `dats_phuong_thuc.cong_thuc_tinh_diem` (text), `dats_tieu_chi_xet_tuyen.gia_tri_tieu_chi` (JSON, ví dụ `"(3*Toan+1*Ngu_van+2*mon_chon)/2"`) | Chuỗi tự do, mỗi trường một kiểu khóa JSON |
| Điều kiện dự tuyển | `dats_dieu_kien_du_tuyen.gia_tri_dieu_kien` (JSON) | Không có cấu trúc chung để so với hồ sơ |
| Bảng quy đổi chứng chỉ, ĐGNL | JSON trong `dats_tieu_chi_xet_tuyen` | Không nối được với điểm của học sinh |
| Tổ hợp theo phương thức | `dats_phuong_thuc.to_hop_mon_hoc` (JSON); `dats_phuong_thuc_to_hop` và `dm_to_hop_mon_hoc_chi_tiet` rỗng | Không nối được tổ hợp → môn |
| Điểm của học sinh | `nguoi_dung_thong_tin.trinh_do_hoc_van` (JSON) | Không nối được với môn, bài thi, chứng chỉ |
| Điểm chuẩn các năm | Chưa có | Không có mốc để đánh giá khả năng trúng tuyển |

Giải pháp: giữ nguyên các bảng cũ làm nguồn mô tả, thêm một lớp **tính toán được** gồm 26 bảng. Bảng cũ chỉ bị đụng ở một chỗ: thêm cột `dats_tru_so.tinh_thanh_id`.

## 2. Mô hình

```
HỒ SƠ HỌC SINH (hs_*)                    QUY TẮC XÉT TUYỂN (xt_*)
hs_ho_so ─┬─ hs_ket_qua_nam_hoc          dats_tuyen_sinh (đề án)
          ├─ hs_diem_mon                    ├─ xt_bang_quy_doi ── xt_bang_quy_doi_chi_tiet
          ├─ hs_diem_bai_thi                ├─ xt_cong_thuc ─┬─ xt_cong_thuc_he_so_mon
          ├─ hs_chung_chi                   │                └─ xt_cong_thuc_thanh_phan
          ├─ hs_thanh_tich                  ├─ xt_nhom_dieu_kien ── xt_dieu_kien
          ├─ hs_tieu_chi_mong_muon          ├─ xt_diem_cong
          └─ hs_chi_so (dẫn xuất)           └─ dats_chuong_trinh_dao_tao ─┬─ xt_phuong_an
                    │                                                     └─ dats_hoc_phi
                    │                    xt_diem_chuan (theo ma_truong + ma_xet_tuyen + năm)
                    ▼
KẾT QUẢ   xt_lan_danh_gia ─┬─ xt_ket_qua_phuong_an      (mỗi cách vào một chương trình)
                           └─ xt_ket_qua_chuong_trinh   (mỗi chương trình một dòng, có điểm phù hợp)
                              v_xt_ket_qua_truong       (gộp theo trường)
CẤU HÌNH  xt_bo_tieu_chi ─┬─ xt_tieu_chi_phu_hop (trọng số)
                          └─ xt_muc_phu_hop (các mốc quy điểm, nhãn)
```

### 2.1. Ba khái niệm trung tâm

**Công thức (`xt_cong_thuc`)** là một "họ" cách tính điểm của đề án. Có 4 kiểu:

| `kieu_tinh` | Ý nghĩa | Ví dụ |
|---|---|---|
| `TO_HOP_MON` | Tổng có hệ số các môn của tổ hợp, nguồn là điểm thi THPT hoặc học bạ; môn ngoại ngữ có thể thay bằng chứng chỉ quy đổi | FTU: `Toán*2 + M2 + M3` (thang 40); BKA K01 |
| `THANH_PHAN` | Tổng các thành phần bài thi/chứng chỉ đã quy đổi | FTU: `27 + (HSA-100)*3/50`; `SAT quy đổi + CCNN quy đổi` |
| `CHI_DIEU_KIEN` | Không tính điểm, chỉ xét điều kiện | Xét tuyển thẳng |
| `THU_CONG` | Có điểm nhưng hệ thống chưa tự tính; chỉ báo "đủ điều kiện nộp hồ sơ" | BKA hồ sơ năng lực + phỏng vấn |

Trên công thức còn có: thang điểm, hệ số nhân tổng (0,5; 4/3...), ngưỡng (`nguong_tb_mon`, `nguong_thpt_to_hop`, `diem_san`), có/không áp dụng điểm cộng và điểm ưu tiên.

**Phương án (`xt_phuong_an`)** = chương trình × công thức × tổ hợp. Đây là bảng nối trung tâm: mỗi dòng là một cách cụ thể để học sinh vào một chương trình. Học sinh có thể có nhiều phương án cho cùng chương trình; hệ thống giữ phương án tốt nhất.

**Chỉ số (`hs_chi_so`)** là bảng phẳng `(hồ sơ, mã chỉ số, khóa, giá trị)` sinh tự động từ các bảng `hs_*`. Điều kiện và điểm cộng của đề án viết theo đúng dạng đó `(mã chỉ số, khóa, toán tử, giá trị)`, nên kiểm tra điều kiện là một phép JOIN, thêm loại điều kiện mới không phải sửa code. Danh sách chỉ số ở `dm_chi_so_xet_tuyen`.

### 2.2. Điều kiện: AND giữa các nhóm, OR trong nhóm

`xt_nhom_dieu_kien` gắn với đề án, có thể thu hẹp theo công thức và/hoặc chương trình. Mọi nhóm áp dụng cho phương án phải đạt; trong một nhóm chỉ cần một `xt_dieu_kien` đạt. Ví dụ FTU xét học bạ:

```
[TN_2026]               NAM_TOT_NGHIEP = 2026
[HOC_LUC_TOT]           HOC_LUC_MIN_3_NAM >= 4
[REN_LUYEN_KHA]         REN_LUYEN_MIN_3_NAM >= 3
[CHUYEN_HOAC_HSG_TINH]  HE_CHUYEN = 1   HOẶC   THANH_TICH[HSG-TINH] <= 3
```

`ten_nhom` được dùng làm lý do hiển thị khi không đạt.

### 2.3. Tổ hợp môn

`dm_to_hop_mon_hoc_chi_tiet` (đang rỗng) được dựng từ `dm_to_hop_mon_hoc.ds_mon_hoc`. `thu_tu_mon` là **vị trí tính điểm**: nhiều môn cùng một vị trí nghĩa là "chọn một trong các môn", lấy môn điểm cao nhất. Nhờ vậy K01 (Toán, Văn, một trong Lý/Hóa/Sinh/Tin) không cần bảng riêng.

## 3. Cách tính (thủ tục `sp_xt_danh_gia`)

1. Dựng lại `hs_chi_so` cho hồ sơ.
2. Với mọi phương án của các đề án trong năm:
   - `TO_HOP_MON`: mỗi vị trí lấy `hệ số × điểm` cao nhất, cộng lại, nhân `he_so_nhan`. Chỉ ghi kết quả khi học sinh đủ môn.
   - `THANH_PHAN`: quy đổi bài thi/chứng chỉ theo `xt_bang_quy_doi_chi_tiet` (bậc thang hoặc nội suy tuyến tính), cộng theo hệ số.
3. Điểm cộng (`xt_diem_cong`): mỗi `nhom_cong` lấy mức cao nhất, cộng các nhóm, chặn trần 10% thang (khoản 2c Điều 6), quy từ thang 30 sang thang của công thức.
4. Điểm ưu tiên (Điều 7): mức khu vực + đối tượng; quy tổng điểm về thang 30, từ 22,5 trở lên thì nhân `(30 - tổng)/7,5`; ưu tiên khu vực chỉ tính trong năm tốt nghiệp và năm kế tiếp.
5. Điểm xét = min(thang, gốc + cộng + ưu tiên), làm tròn 2 chữ số.
6. Xét ngưỡng của công thức và các nhóm điều kiện → `du_dieu_kien`, `ly_do_khong_dat`.
7. Lấy điểm chuẩn tham chiếu: cùng `ma_truong` + `ma_xet_tuyen`, năm gần nhất, ưu tiên dòng khớp tổ hợp rồi khớp phương thức. `chenh_lech_30` = điểm xét − điểm chuẩn sau khi cùng quy về thang 30.
8. Mỗi chương trình giữ phương án tốt nhất, rồi chấm 4 tiêu chí (0–100):

| Tiêu chí | Trọng số mặc định | Cách chấm |
|---|---|---|
| Khả năng trúng tuyển | 50 | Theo `chenh_lech_30`: ≥2 → 100; [1;2) → 90; [0;1) → 75; [−1;0) → 50; [−2;−1) → 25; < −2 → 5. Đủ điều kiện xét thẳng → 100 |
| Ngành | 25 | Đúng ngành/nhóm ngành/lĩnh vực đã chọn → 100; cùng nhóm với ngành đã chọn → 60; khác → 0 |
| Học phí | 15 | Trong ngân sách → 100; vượt thì giảm tuyến tính, vượt 50% → 0 |
| Vị trí | 10 | Đúng tỉnh mong muốn → 100; đúng vùng → 70; khác → 20 |

   **Điểm phù hợp** = trung bình có trọng số của các tiêu chí có dữ liệu. Ngành, học phí, vị trí thiếu dữ liệu thì bỏ khỏi mẫu số. Riêng khả năng trúng tuyển là tiêu chí nền: **chưa có điểm chuẩn thì không chấm**, chương trình được gắn nhãn "Chưa có điểm chuẩn tham chiếu" và xếp sau. Trọng số và các mốc là dữ liệu trong `xt_tieu_chi_phu_hop`, `xt_muc_phu_hop`; đây là tham số nghiệp vụ do tôi đề xuất, cần anh/chị duyệt.

9. Điểm của **trường** (`v_xt_ket_qua_truong.diem_truong`) = trung bình điểm phù hợp của tối đa 3 chương trình tốt nhất của trường đó.

## 4. Cách dùng

```sql
CALL sp_xt_danh_gia(@ho_so_id, 2026, NULL, @lan);

-- Chương trình phù hợp nhất
SELECT * FROM xt_ket_qua_chuong_trinh WHERE lan_danh_gia_id = @lan ORDER BY thu_hang;
-- Xếp hạng trường
SELECT * FROM v_xt_ket_qua_truong WHERE lan_danh_gia_id = @lan ORDER BY diem_truong DESC;
-- Giải thích từng cách tính, lý do không đạt
SELECT * FROM xt_ket_qua_phuong_an WHERE lan_danh_gia_id = @lan;
```

Các truy vấn lọc theo địa điểm, học phí, chênh lệch điểm có sẵn trong `05_vi_du_truy_van.sql`. `xt_lan_danh_gia.lich_su_tim_truong_id` nối được với `tn_lich_su_tim_truong_phu_hop` hiện có.

Ứng dụng ghi điểm của học sinh vào các bảng `hs_*` (thay cho JSON trong `nguoi_dung_thong_tin`). SAT, ACT, HSA, TSA, V-ACT ghi vào `hs_diem_bai_thi`; IELTS, JLPT, HSK... ghi vào `hs_chung_chi`.

## 5. Nhập một đề án mới

Thứ tự, lấy `04_du_lieu_ftu_bka_2026.sql` làm mẫu:

1. `xt_bang_quy_doi` + chi tiết: mỗi bảng quy đổi trong phụ lục đề án. Mức dưới ngưỡng bảo đảm chất lượng đặt `dat_nguong = 0`.
2. `xt_cong_thuc`: mỗi tổ hợp (phương thức × thang điểm × cách nhân hệ số) một dòng; hệ số môn vào `xt_cong_thuc_he_so_mon`, thành phần bài thi vào `xt_cong_thuc_thanh_phan`.
3. `xt_phuong_an`: sinh bằng `INSERT ... SELECT` từ `dats_phuong_thuc` (đã có mã phương thức và danh sách tổ hợp).
4. `xt_nhom_dieu_kien` + `xt_dieu_kien`, `xt_diem_cong`.
5. `dats_hoc_phi`, `xt_diem_chuan`.

## 6. Kết quả kiểm thử

Đã chạy toàn bộ trên MySQL 5.7 với dump hiện có trong thư mục `database`:

- Nạp được 26 công thức FTU, 7 công thức BKA; 1.271 phương án cho 119 chương trình; mọi dòng `dats_phuong_thuc` của hai trường đều có phương án tương ứng.
- Đối chiếu tay với hồ sơ thử: FTU điểm thi A00 = 9,0 + 8,5 + 8,75 = 26,25, ưu tiên KV2-NT 0,5 × (30 − 26,25)/7,5 = 0,25 → 26,50; FTU HSA 112 → 27,72 + 0,15 = 27,87; FTU SAT 1450 + IELTS 7.0 = 18,5 + 9,0 = 27,50; BKA K01 = (27 + 8 + 17,5)/2 = 26,25 → 26,50; BKA TSA 72,5 + 1,67 = 74,17. Thủ tục cho đúng các số này.
- Điều kiện loại đúng: học bạ D01 trung bình 8,93 < 9,00; tổng thi THPT 22,25 < 24; chương trình FL1 thiếu ngoại ngữ.

Điểm chuẩn dùng trong kiểm thử là **số giả định**, chỉ để chạy thử.

## 7. Việc còn phải làm trước khi dùng thật

**Dữ liệu còn thiếu**

1. `xt_diem_chuan` chưa có số liệu thật. Không có thì không chấm được điểm phù hợp.
2. `dats_chuong_trinh_dao_tao.nganh_dao_tao_id` đang NULL ở cả 245 chương trình, nên tiêu chí Ngành chưa hoạt động.
3. Học phí mới có của FTU. BKA không công bố trong QĐ 2466.
4. Hai đề án còn lại (XDA, KSA) chưa chuẩn hóa sang `xt_*`.

**Điểm lệch trong dữ liệu hiện có**

5. `dm_doi_tuong_uu_tien` đang có 7 đối tượng với 01–04 cộng 2,0 và 05–07 cộng 1,0. Thông tư 06/2026 (Điều 7 khoản 2a) quy định UT1 gồm đối tượng 01–03 (2,0) và UT2 gồm 04–06 (1,0). Tôi chưa sửa bảng này; thủ tục đang lấy `diem_cong` từ bảng nên cần rà lại theo Phụ lục II.
6. `dm_truong.ma_tinh_thanh` và `vung_mien` gần như trống; thủ tục tạm nối theo `ten_tinh_thanh`.
7. Tổ hợp M00 (4 môn) và K00 (rỗng) chưa dựng được chi tiết.

**Quy định chưa mô hình hóa** (liệt kê đầy đủ ở đầu `04_du_lieu_ftu_bka_2026.sql`)

8. BKA: tổ hợp "in đậm" tính Toán hệ số 2 không xác định được từ bản text, hiện tính hệ số 1. Công thức `BKA_THPT_TOAN_X2` để sẵn nhưng tắt.
9. FTU: A-Level chưa tự tính; xét thẳng mới có diện HSG quốc gia và Olympic quốc tế; chưa kiểm tra môn đạt giải khớp tổ hợp khi cộng điểm thưởng; chưa kiểm tra HSKK đi kèm HSK.
10. Phụ lục 2 của FTU ghi công thức giảm điểm ưu tiên cho mọi tổng điểm dưới 30, trong khi Quy chế chỉ giảm từ 22,5. Tôi áp dụng theo Quy chế.
11. Ngưỡng đầu vào riêng của ngành sư phạm, sức khỏe, pháp luật (Điều 9) và mức sàn 15 điểm của Điều 6 khoản 3 chưa đưa vào; có thể nhập qua `nguong_thpt_to_hop` hoặc nhóm điều kiện theo chương trình.

**Triển khai**

12. Dự án dùng Alembic (`alembic_version = 20261113_0051`): chuyển `01_schema.sql` thành migration và khai báo model tương ứng.
13. Mỗi lần chạy ghi vài trăm đến vài nghìn dòng vào `xt_ket_qua_phuong_an`; nên có job xóa các lần đánh giá cũ (xóa `xt_lan_danh_gia` sẽ kéo theo kết quả).
14. Việc nhận biết môn ngoại ngữ dựa vào `dm_mon_hoc.nhom_mon = 'Ngoại ngữ'`; đổi tên nhóm này sẽ làm sai phần thay điểm bằng chứng chỉ.

## 8. Danh sách file

| File | Nội dung |
|---|---|
| `01_schema.sql` | 26 bảng mới + cột `dats_tru_so.tinh_thanh_id` |
| `02_thu_tuc.sql` | `fn_xt_so_sanh`, `sp_hs_cap_nhat_chi_so`, `sp_xt_tinh_diem`, `sp_xt_danh_gia`, view `v_xt_ket_qua_truong` |
| `03_du_lieu_danh_muc.sql` | Danh mục chỉ số, dựng chi tiết tổ hợp môn, bộ tiêu chí mặc định |
| `04_du_lieu_ftu_bka_2026.sql` | Quy tắc xét tuyển 2026 của FTU và BKA; có cập nhật `co_so_id` của chương trình FTU đang NULL |
| `05_vi_du_truy_van.sql` | Hồ sơ thử, điểm chuẩn giả định, 7 truy vấn mẫu. Chỉ chạy trên môi trường thử |
| `IMPLEMENT.md` | Hướng dẫn triển khai cho backend Python và frontend Vue |
| `chuan_du_lieu/` | Cấu trúc JSON chuẩn cho đề án của mỗi trường, danh mục mã, hai file mẫu, script kiểm tra |
| `chay_sql.py` | Tách file `.sql` thành câu lệnh để chạy trong Alembic |
| `test_xet_tuyen.html` | Trang thử logic tính điểm và tìm kiếm, chạy độc lập |
