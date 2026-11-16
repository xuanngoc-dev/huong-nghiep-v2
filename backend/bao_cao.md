# Báo cáo kiểm tra dữ liệu trước khi tích hợp đề án tuyển sinh

Thời điểm: 16/11/2026 13:35. Script chỉ đọc (bước 0.2, `KE_HOACH_TRIEN_KHAI.md`).

| Mức độ | Số mục |
|---|---|
| CHẶN | 0 |
| CẦN BỔ SUNG | 3 |
| CẢNH BÁO | 3 |
| THÔNG TIN | 10 |

## Tóm tắt

| # | Mục | Mức độ | Bước | Tóm tắt |
|---|---|---|---|---|
| 1 | Đề án trùng trường + năm | THÔNG TIN | 1.1, 1.2 | Không có đề án trùng. |
| 2 | Số đề án theo năm | THÔNG TIN | 1.x | 4 đề án, 1 năm tuyển sinh. |
| 3 | Chương trình đào tạo thiếu mã ngành / cơ sở / mã xét tuyển | CẦN BỔ SUNG | 1.4, 3.8 | 245 chương trình: thiếu mã ngành 245, thiếu cơ sở 245, thiếu mã xét tuyển 0. Thiếu mã ngành thì tiêu chí Ngành không chấm được; thiếu mã xét tuyển thì không nối được điểm chuẩn. |
| 4 | Mã xét tuyển trùng trong cùng đề án | CẢNH BÁO | 2.3 | 16 mã xét tuyển xuất hiện nhiều lần trong cùng đề án. Bộ import khớp chương trình theo mã xét tuyển + tên, cần kiểm tra các dòng này. |
| 5 | Trường có đề án nhưng thiếu thông tin địa điểm | CẦN BỔ SUNG | 3.1 (tiêu chí Vị trí) | 4/4 trường có đề án thiếu hoặc sai thông tin tỉnh / vùng miền. |
| 6 | Cơ sở đào tạo chưa suy được tỉnh từ tên / địa chỉ | THÔNG TIN | 1.2, 1.4 (cột tinh_thanh_id mới) | 5/5 cơ sở có tên tỉnh trong tên hoặc địa chỉ (điền tự động được); 0 cơ sở phải chọn tỉnh tay. |
| 7 | Tổ hợp đang dùng chưa có chi tiết môn | CẦN BỔ SUNG | 2.1 (dữ liệu nền file 03) | 292/292 tổ hợp đang dùng chưa có dòng trong dm_to_hop_mon_hoc_chi_tiet; migration 2.1 sẽ dựng từ ds_mon_hoc. |
| 8 | Tổ hợp không dựng được chi tiết tự động | CẢNH BÁO | 2.1 | 4 tổ hợp có ds_mon_hoc rỗng, sai mã môn hoặc không đủ 3 môn. |
| 9 | Năm áp dụng của tổ hợp | THÔNG TIN | 5.1 | Bảng đã có cột nam_ap_dung_tu / nam_ap_dung_den; 0/292 tổ hợp có giá trị. Bước 5.1 chỉ cần dùng cột có sẵn, không phải thêm cột. |
| 10 | Nhóm môn 'Ngoại ngữ' | THÔNG TIN | 3.1 (thay điểm môn ngoại ngữ bằng chứng chỉ) | 8 môn thuộc nhóm 'Ngoại ngữ'. |
| 11 | Điểm cộng đối tượng ưu tiên so với Thông tư 06/2026 | CẢNH BÁO | 5.2 | 2/7 đối tượng lệch hoặc không có trong Thông tư (theo THIET_KE.md mục 7.5). |
| 12 | Điểm cộng khu vực ưu tiên | THÔNG TIN | 5.1 | 4 khu vực; bảng đã có cột nam_ap_dung. |
| 13 | Đề án của file mẫu đã có trong CSDL | THÔNG TIN | 2.3, 2.4 (nghiệm thu import) | Bộ import khớp đề án theo trường + năm của file mẫu. |
| 14 | Mã trong file mẫu chưa có trong danh mục CSDL | THÔNG TIN | 2.3 (import sẽ từ chối cả file) | Mọi mã trong file mẫu đều có trong danh mục. |
| 15 | Tổ hợp riêng của trường (quyết định gắn tiền tố mã trường) | THÔNG TIN | 2.3 | Mã dự kiến sau khi gắn tiền tố; mã gốc đã có trong danh mục chung thì sẽ đụng nếu không gắn. |
| 16 | Mã tổ hợp hiện có chứa dấu '-' | THÔNG TIN | 2.3 | Không có mã tổ hợp nào chứa '-', quy ước tiền tố không bị nhầm. |

## 1. Đề án trùng trường + năm

**THÔNG TIN** · bước 1.1, 1.2

Không có đề án trùng.

## 2. Số đề án theo năm

**THÔNG TIN** · bước 1.x

4 đề án, 1 năm tuyển sinh.

| Năm | Số đề án | Số trường | Đề án chưa có chương trình |
|---|---|---|---|
| 2026 | 4 | 4 | 0 |

## 3. Chương trình đào tạo thiếu mã ngành / cơ sở / mã xét tuyển

**CẦN BỔ SUNG** · bước 1.4, 3.8

245 chương trình: thiếu mã ngành 245, thiếu cơ sở 245, thiếu mã xét tuyển 0. Thiếu mã ngành thì tiêu chí Ngành không chấm được; thiếu mã xét tuyển thì không nối được điểm chuẩn.

| Mã trường | Năm | Số chương trình | Thiếu ngành | Thiếu cơ sở | Thiếu mã xét tuyển |
|---|---|---|---|---|---|
| KSA | 2026 | 82 | 82 | 82 | 0 |
| BKA | 2026 | 68 | 68 | 68 | 0 |
| NTH | 2026 | 51 | 51 | 51 | 0 |
| XDA | 2026 | 44 | 44 | 44 | 0 |

## 4. Mã xét tuyển trùng trong cùng đề án

**CẢNH BÁO** · bước 2.3

16 mã xét tuyển xuất hiện nhiều lần trong cùng đề án. Bộ import khớp chương trình theo mã xét tuyển + tên, cần kiểm tra các dòng này.

| Mã trường | Năm | Id đề án | Mã xét tuyển | Số lần |
|---|---|---|---|---|
| NTH | 2026 | 6 | NTHCN18 | 3 |
| NTH | 2026 | 6 | NTHKD06 | 2 |
| NTH | 2026 | 6 | NTHKD07 | 2 |
| NTH | 2026 | 6 | NTHKD08 | 2 |
| NTH | 2026 | 6 | NTHKE16 | 3 |
| NTH | 2026 | 6 | NTHKK23 | 2 |
| NTH | 2026 | 6 | NTHKT02 | 2 |
| NTH | 2026 | 6 | NTHKT04 | 3 |
| NTH | 2026 | 6 | NTHLS17 | 4 |
| NTH | 2026 | 6 | NTHQK12 | 2 |
| NTH | 2026 | 6 | NTHQT10 | 3 |
| NTH | 2026 | 6 | NTHTC15 | 3 |
| NTH | 2026 | 6 | NTHTM11 | 2 |
| NTH | 2026 | 6 | NTSKT01 | 2 |
| NTH | 2026 | 6 | NTSQT03 | 2 |
| NTH | 2026 | 6 | NTSTC05 | 2 |

## 5. Trường có đề án nhưng thiếu thông tin địa điểm

**CẦN BỔ SUNG** · bước 3.1 (tiêu chí Vị trí)

4/4 trường có đề án thiếu hoặc sai thông tin tỉnh / vùng miền.

| Mã trường | Thiếu / sai |
|---|---|
| BKA | mã tỉnh, vùng miền |
| KSA | mã tỉnh, vùng miền |
| NTH | mã tỉnh, vùng miền |
| XDA | mã tỉnh, vùng miền |

## 6. Cơ sở đào tạo chưa suy được tỉnh từ tên / địa chỉ

**THÔNG TIN** · bước 1.2, 1.4 (cột tinh_thanh_id mới)

5/5 cơ sở có tên tỉnh trong tên hoặc địa chỉ (điền tự động được); 0 cơ sở phải chọn tỉnh tay.

## 7. Tổ hợp đang dùng chưa có chi tiết môn

**CẦN BỔ SUNG** · bước 2.1 (dữ liệu nền file 03)

292/292 tổ hợp đang dùng chưa có dòng trong dm_to_hop_mon_hoc_chi_tiet; migration 2.1 sẽ dựng từ ds_mon_hoc.

## 8. Tổ hợp không dựng được chi tiết tự động

**CẢNH BÁO** · bước 2.1

4 tổ hợp có ds_mon_hoc rỗng, sai mã môn hoặc không đủ 3 môn.

| Mã tổ hợp | Vấn đề |
|---|---|
| 2 | mã môn không có trong dm_mon_hoc: CN, GDDP |
| K00 | ds_mon_hoc rỗng |
| K01 | có 6 môn (cần dựng tay vị trí tính điểm) |
| M00 | có 4 môn (cần dựng tay vị trí tính điểm) |

## 9. Năm áp dụng của tổ hợp

**THÔNG TIN** · bước 5.1

Bảng đã có cột nam_ap_dung_tu / nam_ap_dung_den; 0/292 tổ hợp có giá trị. Bước 5.1 chỉ cần dùng cột có sẵn, không phải thêm cột.

## 10. Nhóm môn 'Ngoại ngữ'

**THÔNG TIN** · bước 3.1 (thay điểm môn ngoại ngữ bằng chứng chỉ)

8 môn thuộc nhóm 'Ngoại ngữ'.

| Mã môn | Tên môn |
|---|---|
| ANH | Tiếng Anh |
| DUC | Tiếng Đức |
| HAN | Tiếng Hàn |
| NGA | Tiếng Nga |
| NGOAI_NGU | Ngoại ngữ (theo quy định của trường) |
| NHAT | Tiếng Nhật |
| PHAP | Tiếng Pháp |
| TRUNG | Tiếng Trung Quốc |

## 11. Điểm cộng đối tượng ưu tiên so với Thông tư 06/2026

**CẢNH BÁO** · bước 5.2

2/7 đối tượng lệch hoặc không có trong Thông tư (theo THIET_KE.md mục 7.5).

Chưa sửa gì; bước 5.2 cần chủ dự án duyệt bảng giá trị.

| Mã | Tên | Điểm cộng | Năm áp dụng | Trạng thái | Đối chiếu |
|---|---|---|---|---|---|
| 01 | Đối tượng 01 | 2 | — | 1 | khớp |
| 02 | Đối tượng 02 | 2 | — | 1 | khớp |
| 03 | Đối tượng 03 | 2 | — | 1 | khớp |
| 04 | Đối tượng 04 | 2 | — | 1 | lệch: Thông tư 1 |
| 05 | Đối tượng 05 | 1 | — | 1 | khớp |
| 06 | Đối tượng 06 | 1 | — | 1 | khớp |
| 07 | Đối tượng 07 | 1 | — | 1 | không có trong UT1/UT2 của Thông tư, cần rà |

## 12. Điểm cộng khu vực ưu tiên

**THÔNG TIN** · bước 5.1

4 khu vực; bảng đã có cột nam_ap_dung.

| Mã | Điểm cộng | Năm áp dụng | Trạng thái |
|---|---|---|---|
| KV1 | 0.75 | — | 1 |
| KV2 | 0.25 | — | 1 |
| KV2-NT | 0.5 | — | 1 |
| KV3 | 0 | — | 1 |

## 13. Đề án của file mẫu đã có trong CSDL

**THÔNG TIN** · bước 2.3, 2.4 (nghiệm thu import)

Bộ import khớp đề án theo trường + năm của file mẫu.

| File | Mã trường | Năm | Đề án trong CSDL |
|---|---|---|---|
| mau_NTH_2026.json | NTH | 2026 | có |
| mau_BKA_2026.json | BKA | 2026 | có |

## 14. Mã trong file mẫu chưa có trong danh mục CSDL

**THÔNG TIN** · bước 2.3 (import sẽ từ chối cả file)

Mọi mã trong file mẫu đều có trong danh mục.

## 15. Tổ hợp riêng của trường (quyết định gắn tiền tố mã trường)

**THÔNG TIN** · bước 2.3

Mã dự kiến sau khi gắn tiền tố; mã gốc đã có trong danh mục chung thì sẽ đụng nếu không gắn.

| File | Mã trong file | Mã sẽ lưu | Danh mục hiện tại |
|---|---|---|---|
| mau_BKA_2026.json | K01 | BKA-K01 | đã có trong dm_to_hop_mon_hoc (sẽ đụng nếu không gắn tiền tố) |

## 16. Mã tổ hợp hiện có chứa dấu '-'

**THÔNG TIN** · bước 2.3

Không có mã tổ hợp nào chứa '-', quy ước tiền tố không bị nhầm.
