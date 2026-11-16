-- =====================================================================
-- 04_du_lieu_ftu_bka_2026.sql
-- Chuẩn hóa quy tắc xét tuyển 2026 của:
--   NTH - Trường ĐH Ngoại thương  (QĐ 1566/QĐ-ĐHNT ngày 08/04/2026)
--   BKA - ĐH Bách khoa Hà Nội     (QĐ 2466/QĐ-ĐHBK ngày 03/03/2026)
-- vào các bảng xt_*. Chương trình và phương thức lấy từ dats_chuong_trinh_dao_tao,
-- dats_phuong_thuc đã có (nối theo mã, không ghi cứng id).
-- Chạy lại nhiều lần được: phần đầu xóa dữ liệu xt_* cũ của hai đề án này.
--
-- NHỮNG ĐIỂM CHƯA MÔ HÌNH HÓA (đọc trước khi dùng kết quả):
--  FTU
--   - A-Level + CCNN: chỉ nhận diện "có chứng chỉ A-Level", chưa tự tính điểm (kieu_tinh = THU_CONG).
--   - Xét tuyển thẳng: chỉ mô hình hóa diện b, c (Olympic quốc tế, HSG quốc gia giải Nhất/Nhì/Ba);
--     các diện a, d, e, f, g và ràng buộc "môn đạt giải phù hợp chương trình" chưa có.
--   - Điểm thưởng: chưa kiểm tra môn đạt giải thuộc tổ hợp xét; chưa có mức 0,5 "tham gia đội tuyển HSG quốc gia".
--   - HSK phải kèm HSKK cùng kỳ thi; HSA phần 3 Khoa học phải chọn Lý + Hóa: chưa kiểm tra.
--   - SAT/ACT + CCNN: mới nhận chứng chỉ tiếng Anh (chưa nhận tiếng Pháp/Nhật/Trung cho
--     các chương trình Ngôn ngữ thương mại tương ứng).
--   - Ngưỡng riêng của các chương trình lĩnh vực pháp luật (khoản 2 Điều 9 Quy chế) chưa có.
--   - Bảng quy đổi tiếng Nhật: các mức N3 95-129 trong đề án ghi khoảng điểm (6.0-7.0, 7.5-8.5)
--     và đều dưới ngưỡng bảo đảm chất lượng nên không nhập.
--  BKA
--   - Đề án ghi "tổ hợp in đậm tính Toán hệ số 2" nhưng bản text không còn định dạng in đậm,
--     nên mọi tổ hợp ngoài K01 đang tính hệ số 1. Công thức BKA_THPT_TOAN_X2 để sẵn ở
--     trang_thai = 0; cách quy về thang 30 của nó KHÔNG có trong QĐ 2466, phải đối chiếu trước khi bật.
--   - Quy đổi chứng chỉ ngoại ngữ thành điểm môn tiếng Anh: bảng tham chiếu không có trong QĐ 2466.
--   - Xét tuyển tài năng diện 1.2, 1.3: chỉ xét điều kiện nộp hồ sơ, chưa tính điểm (THU_CONG).
--   - Ngưỡng điểm sàn THPT và ngưỡng TSA: đề án ghi "thông báo sau".
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

SET @da_ftu := (SELECT id FROM dats_tuyen_sinh WHERE ma_truong = 'NTH' AND nam_tuyen_sinh = 2026 ORDER BY id LIMIT 1);
SET @da_bka := (SELECT id FROM dats_tuyen_sinh WHERE ma_truong = 'BKA' AND nam_tuyen_sinh = 2026 ORDER BY id LIMIT 1);

-- ---------------------------------------------------------------------
-- 0. Dọn dữ liệu cũ của hai đề án
-- ---------------------------------------------------------------------
DELETE FROM xt_phuong_an      WHERE de_an_id IN (@da_ftu, @da_bka);
DELETE FROM xt_diem_cong      WHERE de_an_id IN (@da_ftu, @da_bka);
DELETE FROM xt_nhom_dieu_kien WHERE de_an_id IN (@da_ftu, @da_bka);
DELETE FROM xt_cong_thuc      WHERE de_an_id IN (@da_ftu, @da_bka);
DELETE FROM xt_bang_quy_doi   WHERE de_an_id IN (@da_ftu, @da_bka);
DELETE FROM dats_hoc_phi      WHERE de_an_id IN (@da_ftu, @da_bka);

-- =====================================================================
-- PHẦN 1. TRƯỜNG ĐẠI HỌC NGOẠI THƯƠNG
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1.1 Bảng quy đổi (Phụ lục 3 và mục 6.4.2.1)
-- ---------------------------------------------------------------------
INSERT INTO xt_bang_quy_doi (de_an_id, ma_bang, ten_bang, thang_diem_dich, ghi_chu) VALUES
(@da_ftu, 'QD_NGOAI_NGU', 'Quy đổi chứng chỉ ngoại ngữ quốc tế sang điểm môn ngoại ngữ', 10,
 'Phụ lục 3 mục 1, 2. Ngưỡng bảo đảm chất lượng: IELTS 6.5 hoặc tương đương; JLPT N3 từ 130; EJU từ 220; HSK4 từ 280 và HSKK trung cấp từ 60; DELF B2. Mức dưới ngưỡng có dat_nguong = 0.'),
(@da_ftu, 'QD_SAT_ACT', 'Quy đổi SAT/ACT sang thang 20', 20, 'Phụ lục 3 mục 3.'),
(@da_ftu, 'QD_DGNL_30', 'Quy đổi HSA, V-ACT, TSA về thang 30', 30,
 'Mục 6.4.2.1: HSA = 27 + (x-100)*3/50; V-ACT = 27 + (x-850)*3/350; TSA = 27 + (x-70)*3/30. Dưới 100/850/70 không đủ điều kiện.');
SET @b_nn   := (SELECT id FROM xt_bang_quy_doi WHERE de_an_id = @da_ftu AND ma_bang = 'QD_NGOAI_NGU');
SET @b_sat  := (SELECT id FROM xt_bang_quy_doi WHERE de_an_id = @da_ftu AND ma_bang = 'QD_SAT_ACT');
SET @b_dgnl := (SELECT id FROM xt_bang_quy_doi WHERE de_an_id = @da_ftu AND ma_bang = 'QD_DGNL_30');

-- IELTS Academic, TOEFL iBT, JLPT, EJU, HSK, DELF/DALF
INSERT INTO xt_bang_quy_doi_chi_tiet (bang_quy_doi_id, chung_chi_id, mon_hoc_id, cap_do, diem_tu, diem_den, diem_quy_doi, dat_nguong)
SELECT @b_nn, cc.id, mh.id, v.cap_do, v.diem_tu, v.diem_den, v.qd, v.dat
FROM (
            SELECT 'IELTS' AS ma_cc, 'ANH' AS ma_mon, CAST(NULL AS CHAR(30)) AS cap_do, 4.0 AS diem_tu, 4.5 AS diem_den, 5.0 AS qd, 0 AS dat
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 5.0, 5.5,  6.5, 0
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 6.0, 6.0,  7.5, 0
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 6.5, 6.5,  8.5, 1
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 7.0, 7.0,  9.0, 1
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 7.5, 7.5,  9.5, 1
  UNION ALL SELECT 'IELTS', 'ANH', NULL, 8.0, 9.0, 10.0, 1
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL,  45,  50,  5.0, 0
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL,  51,  59,  6.5, 0
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL,  60,  78,  7.5, 0
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL,  79,  92,  8.5, 1
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL,  93, 101,  9.0, 1
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL, 102, 109,  9.5, 1
  UNION ALL SELECT 'TOEFL_IBT_120', 'ANH', NULL, 110, 120, 10.0, 1
  UNION ALL SELECT 'JLPT', 'NHAT', 'N3', 130,  180,  9.0, 1
  UNION ALL SELECT 'JLPT', 'NHAT', 'N2', NULL, NULL, 9.5, 1
  UNION ALL SELECT 'JLPT', 'NHAT', 'N1', NULL, NULL, 10.0, 1
  UNION ALL SELECT 'EJU',  'NHAT', NULL, 220, 269,  9.0, 1
  UNION ALL SELECT 'EJU',  'NHAT', NULL, 270, 319,  9.5, 1
  UNION ALL SELECT 'EJU',  'NHAT', NULL, 320, 340, 10.0, 1
  UNION ALL SELECT 'HSK_2_0', 'TRUNG', 'HSK4', 280, 300,   9.0, 1
  UNION ALL SELECT 'HSK_2_0', 'TRUNG', 'HSK5', NULL, NULL, 9.5, 1
  UNION ALL SELECT 'HSK_2_0', 'TRUNG', 'HSK6', NULL, NULL, 10.0, 1
  UNION ALL SELECT 'DELF', 'PHAP', 'B2', NULL, NULL,  9.0, 1
  UNION ALL SELECT 'DALF', 'PHAP', 'C1', NULL, NULL,  9.5, 1
  UNION ALL SELECT 'DALF', 'PHAP', 'C2', NULL, NULL, 10.0, 1
) v
JOIN dm_bang_cap_chung_chi cc ON cc.ma_chung_chi = v.ma_cc
JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = v.ma_mon;

-- Cambridge English Scale: cùng một thang cho các bài thi Cambridge
INSERT INTO xt_bang_quy_doi_chi_tiet (bang_quy_doi_id, chung_chi_id, mon_hoc_id, diem_tu, diem_den, diem_quy_doi, dat_nguong)
SELECT @b_nn, cc.id, mh.id, v.diem_tu, v.diem_den, v.qd, v.dat
FROM (
            SELECT 140 AS diem_tu, 153 AS diem_den, 5.0 AS qd, 0 AS dat
  UNION ALL SELECT 154, 168,  6.5, 0
  UNION ALL SELECT 169, 179,  7.5, 0
  UNION ALL SELECT 180, 183,  8.5, 1
  UNION ALL SELECT 184, 191,  9.0, 1
  UNION ALL SELECT 192, 199,  9.5, 1
  UNION ALL SELECT 200, 230, 10.0, 1
) v
JOIN dm_bang_cap_chung_chi cc
  ON cc.ma_chung_chi IN ('CAMBRIDGE_B1_PRELIMINARY', 'CAMBRIDGE_B2_FIRST', 'CAMBRIDGE_C1_ADVANCED', 'CAMBRIDGE_C2_PROFICIENCY')
JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'ANH';

-- SAT / ACT -> thang 20
INSERT INTO xt_bang_quy_doi_chi_tiet (bang_quy_doi_id, bai_thi_id, diem_tu, diem_den, diem_quy_doi)
SELECT @b_sat, bt.id, v.diem_tu, v.diem_den, v.qd
FROM (
            SELECT 'SAT' AS ma_bt, 1380 AS diem_tu, 1390 AS diem_den, 17.50 AS qd
  UNION ALL SELECT 'SAT', 1400, 1420, 18.00
  UNION ALL SELECT 'SAT', 1430, 1470, 18.50
  UNION ALL SELECT 'SAT', 1480, 1490, 19.00
  UNION ALL SELECT 'SAT', 1500, 1520, 19.50
  UNION ALL SELECT 'SAT', 1530, 1540, 19.75
  UNION ALL SELECT 'SAT', 1550, 1600, 20.00
  UNION ALL SELECT 'ACT', 30, 30, 17.50
  UNION ALL SELECT 'ACT', 31, 31, 18.00
  UNION ALL SELECT 'ACT', 32, 32, 18.50
  UNION ALL SELECT 'ACT', 33, 33, 19.00
  UNION ALL SELECT 'ACT', 34, 34, 19.50
  UNION ALL SELECT 'ACT', 35, 35, 19.75
  UNION ALL SELECT 'ACT', 36, 36, 20.00
) v
JOIN dm_bai_thi_danh_gia bt ON bt.ma_bai_thi = v.ma_bt;

-- HSA / V-ACT / TSA -> thang 30 (nội suy tuyến tính từ mức sàn)
INSERT INTO xt_bang_quy_doi_chi_tiet (bang_quy_doi_id, bai_thi_id, diem_tu, diem_den, diem_quy_doi, he_so_noi_suy)
SELECT @b_dgnl, bt.id, v.diem_tu, v.diem_den, 27, v.he_so
FROM (
            -- Ghi hệ số bằng số thập phân đủ 8 chữ số: viết 3 / 350 thì MySQL chỉ giữ 4 chữ số (0,0086) và làm lệch kết quả
            SELECT 'HSA'   AS ma_bt, 100 AS diem_tu,  150 AS diem_den, 0.06000000 AS he_so   -- 3/50
  UNION ALL SELECT 'V-ACT',          850,            1200,             0.00857143            -- 3/350
  UNION ALL SELECT 'TSA',             70,             100,             0.10000000            -- 3/30
) v
JOIN dm_bai_thi_danh_gia bt ON bt.ma_bai_thi = v.ma_bt;

-- ---------------------------------------------------------------------
-- 1.2 Công thức.
--   Hậu tố: _30   = CT tiêu chuẩn, CLC, tiên tiến, ĐHNN&PTQT, tích hợp Luật (thang 30)
--           _IT40 = CT tích hợp Khoa học máy tính / Trí tuệ nhân tạo / Khoa học dữ liệu (Toán x2, thang 40)
--           _NN40 = CT tích hợp Ngôn ngữ thương mại (Văn x1,5; Ngoại ngữ x1,5; thang 40)
-- ---------------------------------------------------------------------
INSERT INTO xt_cong_thuc
  (de_an_id, ma_cong_thuc, ten_cong_thuc, ma_phuong_thuc_cua_bo, kieu_tinh, nguon_diem_mon, thay_ngoai_ngu,
   bang_quy_doi_ngoai_ngu_id, thang_diem, he_so_nhan, nguong_tb_mon, nguong_thpt_to_hop, mo_ta_cong_thuc)
VALUES
-- 6.3.2.1 Điểm thi THPT 3 môn
(@da_ftu, 'FTU_THPT_30',   'Điểm thi THPT - thang 30', '100', 'TO_HOP_MON', 'THI_THPT', 'KHONG', NULL, 30, 1, NULL, 24,
 'M1 + M2 + M3 + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_THPT_IT40', 'Điểm thi THPT - Toán hệ số 2, thang 40', '100', 'TO_HOP_MON', 'THI_THPT', 'KHONG', NULL, 40, 1, NULL, 24,
 'Toán*2 + M2 + M3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_THPT_NN40', 'Điểm thi THPT - Ngôn ngữ thương mại, thang 40', '100', 'TO_HOP_MON', 'THI_THPT', 'KHONG', NULL, 40, 1, NULL, 24,
 'Toán + Ngữ văn*1,5 + Ngoại ngữ*1,5 + điểm ưu tiên, điểm thưởng quy đổi'),
-- 6.2.3.1 Học bạ 3 môn (TB 3 môn >= 9,00)
(@da_ftu, 'FTU_HB_30',   'Học bạ THPT - thang 30', '200', 'TO_HOP_MON', 'HOC_BA', 'KHONG', NULL, 30, 1, 9.00, 24,
 'M1 + M2 + M3 (TB cả năm lớp 10, 11, 12 từng môn) + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_HB_IT40', 'Học bạ THPT - Toán hệ số 2, thang 40', '200', 'TO_HOP_MON', 'HOC_BA', 'KHONG', NULL, 40, 1, 9.00, 24,
 'Toán*2 + M2 + M3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_HB_NN40', 'Học bạ THPT - Ngôn ngữ thương mại, thang 40', '200', 'TO_HOP_MON', 'HOC_BA', 'KHONG', NULL, 40, 1, 9.00, 24,
 'Toán + Ngữ văn*1,5 + Ngoại ngữ*1,5 + điểm ưu tiên, điểm thưởng quy đổi'),
-- 6.3.2.2 Điểm thi THPT 2 môn + chứng chỉ ngoại ngữ
(@da_ftu, 'FTU_THPT_CCNN_30',   'Điểm thi THPT kết hợp CCNN - thang 30', '409', 'TO_HOP_MON', 'THI_THPT', 'BAT_BUOC', @b_nn, 30, 1, NULL, 24,
 'Toán + (Lý/Hóa/Văn) + điểm quy đổi CCNN + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_THPT_CCNN_IT40', 'Điểm thi THPT kết hợp CCNN - Toán hệ số 2, thang 40', '409', 'TO_HOP_MON', 'THI_THPT', 'BAT_BUOC', @b_nn, 40, 1, NULL, 24,
 'Toán*2 + (Lý/Hóa/Văn) + điểm quy đổi CCNN + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_THPT_CCNN_NN40', 'Điểm thi THPT kết hợp CCNN - Ngôn ngữ thương mại, thang 40', '409', 'TO_HOP_MON', 'THI_THPT', 'BAT_BUOC', @b_nn, 40, 1, NULL, 24,
 'Toán + Ngữ văn*1,5 + điểm quy đổi CCNN*1,5 + điểm ưu tiên, điểm thưởng quy đổi'),
-- 6.2.3.2 Học bạ 2 môn + chứng chỉ ngoại ngữ (TB 2 môn >= 8,50; Ngôn ngữ thương mại >= 8,00)
(@da_ftu, 'FTU_HB_CCNN_30',   'Học bạ kết hợp CCNN - thang 30', '410', 'TO_HOP_MON', 'HOC_BA', 'BAT_BUOC', @b_nn, 30, 1, 8.50, 24,
 'Toán + (Lý/Hóa/Văn) + điểm quy đổi CCNN + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_HB_CCNN_IT40', 'Học bạ kết hợp CCNN - Toán hệ số 2, thang 40', '410', 'TO_HOP_MON', 'HOC_BA', 'BAT_BUOC', @b_nn, 40, 1, 8.50, 24,
 'Toán*2 + (Lý/Hóa/Văn) + điểm quy đổi CCNN + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_HB_CCNN_NN40', 'Học bạ kết hợp CCNN - Ngôn ngữ thương mại, thang 40', '410', 'TO_HOP_MON', 'HOC_BA', 'BAT_BUOC', @b_nn, 40, 1, 8.00, 24,
 'Toán + Ngữ văn*1,5 + điểm quy đổi CCNN*1,5 + điểm ưu tiên, điểm thưởng quy đổi'),
-- 6.4.2.1 ĐGNL / ĐGTD trong nước
(@da_ftu, 'FTU_HSA_30',   'ĐGNL HSA - thang 30', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 '27 + (HSA - 100)*3/50 + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_HSA_40',   'ĐGNL HSA - thang 40 (KHMT, TTNT, KHDL)', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '[27 + (HSA - 100)*3/50]*4/3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_HSA_NN40', 'ĐGNL HSA phần 3 Tiếng Anh - thang 40 (Ngôn ngữ thương mại)', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '[27 + (HSA - 100)*3/50]*4/3 + điểm ưu tiên, điểm thưởng quy đổi; bắt buộc chọn phần 3 - Tiếng Anh'),
(@da_ftu, 'FTU_VACT_30',  'ĐGNL V-ACT - thang 30', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 '27 + (V-ACT - 850)*3/350 + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_VACT_40',  'ĐGNL V-ACT - thang 40 (KHMT, TTNT, KHDL)', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '[27 + (V-ACT - 850)*3/350]*4/3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_TSA_40',   'ĐGTD TSA - thang 40 (KHMT, TTNT, KHDL)', '402', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '[27 + (TSA - 70)*3/30]*4/3 + điểm ưu tiên, điểm thưởng quy đổi'),
-- 6.4.2.2 SAT/ACT + CCNN
(@da_ftu, 'FTU_SAT_30',   'SAT kết hợp CCNN - thang 30', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 'M1 (SAT quy đổi thang 20) + M2 (CCNN quy đổi) + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_SAT_IT40', 'SAT kết hợp CCNN - thang 40 (KHMT, TTNT, KHDL)', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '(M1 + M2)*4/3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_SAT_NN40', 'SAT kết hợp CCNN - thang 40 (Ngôn ngữ thương mại)', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1, NULL, NULL,
 'M1 + M2*2 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_ACT_30',   'ACT kết hợp CCNN - thang 30', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 'M1 (ACT quy đổi thang 20) + M2 (CCNN quy đổi) + điểm ưu tiên, điểm thưởng'),
(@da_ftu, 'FTU_ACT_IT40', 'ACT kết hợp CCNN - thang 40 (KHMT, TTNT, KHDL)', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1.33333333, NULL, NULL,
 '(M1 + M2)*4/3 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_ACT_NN40', 'ACT kết hợp CCNN - thang 40 (Ngôn ngữ thương mại)', '415', 'THANH_PHAN', NULL, 'KHONG', NULL, 40, 1, NULL, NULL,
 'M1 + M2*2 + điểm ưu tiên, điểm thưởng quy đổi'),
(@da_ftu, 'FTU_ALEVEL',   'A-Level kết hợp CCNN (chưa tự tính điểm)', '415', 'THU_CONG', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 'M1 (Toán A-Level quy đổi) + M2 (môn A-Level khác) + M3 (CCNN quy đổi); có biến thể thang 40'),
(@da_ftu, 'FTU_XET_THANG', 'Xét tuyển thẳng theo Quy chế', '301', 'CHI_DIEU_KIEN', NULL, 'KHONG', NULL, 30, 1, NULL, NULL,
 'Không tính điểm; xét theo chỉ tiêu tuyển thẳng, thứ tự nguyện vọng, hạng giải');

UPDATE xt_cong_thuc SET ap_dung_diem_cong = 0, ap_dung_uu_tien = 0
WHERE de_an_id = @da_ftu AND ma_cong_thuc IN ('FTU_XET_THANG', 'FTU_ALEVEL');

-- Hệ số môn
INSERT INTO xt_cong_thuc_he_so_mon (cong_thuc_id, mon_hoc_id, nhom_mon, he_so)
SELECT ct.id, mh.id, NULL, 2
FROM xt_cong_thuc ct JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'TOAN'
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'TO_HOP_MON' AND ct.ma_cong_thuc LIKE '%\_IT40';

INSERT INTO xt_cong_thuc_he_so_mon (cong_thuc_id, mon_hoc_id, nhom_mon, he_so)
SELECT ct.id, mh.id, NULL, 1.5
FROM xt_cong_thuc ct JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'VAN'
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'TO_HOP_MON' AND ct.ma_cong_thuc LIKE '%\_NN40';

INSERT INTO xt_cong_thuc_he_so_mon (cong_thuc_id, mon_hoc_id, nhom_mon, he_so)
SELECT ct.id, NULL, 'Ngoại ngữ', 1.5
FROM xt_cong_thuc ct
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'TO_HOP_MON' AND ct.ma_cong_thuc LIKE '%\_NN40';

-- Thành phần của các công thức bài thi (kết quả năm 2026)
INSERT INTO xt_cong_thuc_thanh_phan
  (cong_thuc_id, vi_tri, ten_thanh_phan, loai_nguon, bai_thi_id, bang_quy_doi_id, he_so, nam_thi_tu, nam_thi_den, yeu_cau_phan_tu_chon)
SELECT ct.id, 1, CONCAT('Điểm ', bt.ten_viet_tat, ' quy đổi thang 30'), 'BAI_THI', bt.id, @b_dgnl, 1, 2026, 2026,
       IF(ct.ma_cong_thuc = 'FTU_HSA_NN40', 'TIENG_ANH', NULL)
FROM xt_cong_thuc ct
JOIN dm_bai_thi_danh_gia bt
  ON bt.ma_bai_thi = CASE WHEN ct.ma_cong_thuc LIKE 'FTU\_HSA\_%' THEN 'HSA'
                          WHEN ct.ma_cong_thuc LIKE 'FTU\_VACT\_%' THEN 'V-ACT'
                          WHEN ct.ma_cong_thuc LIKE 'FTU\_TSA\_%' THEN 'TSA' END
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'THANH_PHAN';

-- SAT/ACT: M1 = bài thi quy đổi thang 20 (hiệu lực 3 năm), M2 = chứng chỉ tiếng Anh quy đổi thang 10
INSERT INTO xt_cong_thuc_thanh_phan
  (cong_thuc_id, vi_tri, ten_thanh_phan, loai_nguon, bai_thi_id, bang_quy_doi_id, he_so, nam_thi_tu)
SELECT ct.id, 1, CONCAT('M1: ', bt.ma_bai_thi, ' quy đổi thang 20'), 'BAI_THI', bt.id, @b_sat, 1, 2023
FROM xt_cong_thuc ct
JOIN dm_bai_thi_danh_gia bt
  ON bt.ma_bai_thi = CASE WHEN ct.ma_cong_thuc LIKE 'FTU\_SAT\_%' THEN 'SAT'
                          WHEN ct.ma_cong_thuc LIKE 'FTU\_ACT\_%' THEN 'ACT' END
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'THANH_PHAN';

INSERT INTO xt_cong_thuc_thanh_phan
  (cong_thuc_id, vi_tri, ten_thanh_phan, loai_nguon, bang_quy_doi_id, mon_hoc_id, he_so)
SELECT ct.id, 2, 'M2: chứng chỉ ngoại ngữ quốc tế quy đổi', 'CHUNG_CHI', @b_nn, mh.id,
       IF(ct.ma_cong_thuc LIKE '%\_NN40', 2, 1)
FROM xt_cong_thuc ct JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'ANH'
WHERE ct.de_an_id = @da_ftu AND ct.kieu_tinh = 'THANH_PHAN'
  AND (ct.ma_cong_thuc LIKE 'FTU\_SAT\_%' OR ct.ma_cong_thuc LIKE 'FTU\_ACT\_%');

-- ---------------------------------------------------------------------
-- 1.3 Phương án xét tuyển = chương trình x công thức x tổ hợp
--     Lấy từ dats_phuong_thuc (ma_phuong_thuc_cua_truong, to_hop_mon_hoc) đã nhập.
-- ---------------------------------------------------------------------
-- Các phương thức theo tổ hợp môn
INSERT INTO xt_phuong_an (de_an_id, de_an_chuong_trinh_id, de_an_phuong_thuc_id, cong_thuc_id, to_hop_id)
SELECT s.de_an_id, s.chuong_trinh_id, s.phuong_thuc_id, ct.id, th.id
FROM (
  SELECT c.de_an_id, c.id AS chuong_trinh_id, pt.id AS phuong_thuc_id, pt.ma_phuong_thuc_cua_truong AS ma_pt, pt.to_hop_mon_hoc,
         CASE WHEN c.ten_chuong_trinh LIKE 'CT TH Khoa học máy tính%' OR c.ten_chuong_trinh LIKE 'CT TH Trí tuệ nhân tạo%'
                   OR c.ten_chuong_trinh LIKE 'CT TH Khoa học dữ liệu%' THEN 'IT40'
              WHEN c.ten_chuong_trinh LIKE 'CT TH Tiếng % thương mại' THEN 'NN40'
              ELSE '30' END AS bien_the
  FROM dats_phuong_thuc pt
  JOIN dats_chuong_trinh_dao_tao c ON c.id = pt.de_an_chuong_trinh_id
  WHERE c.de_an_id = @da_ftu AND pt.ma_phuong_thuc_cua_truong IN ('FTU_100', 'FTU_200', 'FTU_409', 'FTU_410')
) s
JOIN xt_cong_thuc ct
  ON ct.de_an_id = s.de_an_id
 AND ct.ma_cong_thuc = CONCAT(CASE s.ma_pt WHEN 'FTU_100' THEN 'FTU_THPT_' WHEN 'FTU_200' THEN 'FTU_HB_'
                                           WHEN 'FTU_409' THEN 'FTU_THPT_CCNN_' ELSE 'FTU_HB_CCNN_' END, s.bien_the)
JOIN dm_to_hop_mon_hoc th ON JSON_CONTAINS(s.to_hop_mon_hoc, JSON_QUOTE(th.ma_to_hop))
WHERE EXISTS (SELECT 1 FROM dm_to_hop_mon_hoc_chi_tiet x WHERE x.to_hop_id = th.id)
  -- phương thức kết hợp chứng chỉ chỉ dùng tổ hợp có môn ngoại ngữ (chứng chỉ thay cho môn đó)
  AND (ct.thay_ngoai_ngu <> 'BAT_BUOC'
       OR EXISTS (SELECT 1 FROM dm_to_hop_mon_hoc_chi_tiet x JOIN dm_mon_hoc m ON m.id = x.mon_hoc_id
                  WHERE x.to_hop_id = th.id AND m.nhom_mon = 'Ngoại ngữ'));

-- Các phương thức không theo tổ hợp
INSERT INTO xt_phuong_an (de_an_id, de_an_chuong_trinh_id, de_an_phuong_thuc_id, cong_thuc_id, to_hop_id)
SELECT s.de_an_id, s.chuong_trinh_id, s.phuong_thuc_id, ct.id, NULL
FROM (
  SELECT c.de_an_id, c.id AS chuong_trinh_id, pt.id AS phuong_thuc_id, pt.ma_phuong_thuc_cua_truong AS ma_pt,
         CASE WHEN c.ten_chuong_trinh LIKE 'CT TH Khoa học máy tính%' OR c.ten_chuong_trinh LIKE 'CT TH Trí tuệ nhân tạo%'
                   OR c.ten_chuong_trinh LIKE 'CT TH Khoa học dữ liệu%' THEN 'IT40'
              WHEN c.ten_chuong_trinh LIKE 'CT TH Tiếng % thương mại' THEN 'NN40'
              ELSE '30' END AS bien_the
  FROM dats_phuong_thuc pt
  JOIN dats_chuong_trinh_dao_tao c ON c.id = pt.de_an_chuong_trinh_id
  WHERE c.de_an_id = @da_ftu
) s
JOIN xt_cong_thuc ct
  ON ct.de_an_id = s.de_an_id
 AND ct.ma_cong_thuc = CASE s.ma_pt
       WHEN 'FTU_402_HSA'    THEN CASE s.bien_the WHEN '30' THEN 'FTU_HSA_30' WHEN 'IT40' THEN 'FTU_HSA_40' ELSE 'FTU_HSA_NN40' END
       WHEN 'FTU_402_VACT'   THEN IF(s.bien_the = '30', 'FTU_VACT_30', 'FTU_VACT_40')
       WHEN 'FTU_402_TSA'    THEN 'FTU_TSA_40'
       WHEN 'FTU_415_SAT'    THEN CONCAT('FTU_SAT_', s.bien_the)
       WHEN 'FTU_415_ACT'    THEN CONCAT('FTU_ACT_', s.bien_the)
       WHEN 'FTU_415_ALEVEL' THEN 'FTU_ALEVEL'
       WHEN 'FTU_301'        THEN 'FTU_XET_THANG' END;

-- ---------------------------------------------------------------------
-- 1.4 Điều kiện dự tuyển (mục II.1, 6.1 - 6.4)
-- ---------------------------------------------------------------------
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta) VALUES
(@da_ftu, NULL, 'TN_THPT', 'Chưa tốt nghiệp THPT hoặc tương đương',
 'Đã được công nhận tốt nghiệp THPT (hoặc tương đương) tính tới thời điểm xét tuyển.');

-- Thi THPT (100, 409) và ĐGNL/ĐGTD (402): học tập và rèn luyện từng năm đạt Khá trở lên
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, 'HOC_LUC_KHA', 'Kết quả học tập từng năm lớp 10, 11, 12 chưa đạt Khá',
       'CT 2018: kết quả học tập từng năm đạt mức Khá trở lên; CT trước 2018: điểm TBC từng năm từ 7,0.'
FROM xt_cong_thuc ct
WHERE ct.de_an_id = @da_ftu AND ct.ma_phuong_thuc_cua_bo IN ('100', '409', '402');

-- Rèn luyện Khá: thêm cả học bạ (200, 410)
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, 'REN_LUYEN_KHA', 'Kết quả rèn luyện từng năm lớp 10, 11, 12 chưa đạt Khá',
       'Kết quả rèn luyện (hạnh kiểm) từng năm lớp 10, 11, 12 đạt mức Khá trở lên.'
FROM xt_cong_thuc ct
WHERE ct.de_an_id = @da_ftu AND ct.ma_phuong_thuc_cua_bo IN ('100', '409', '402', '200', '410');

-- Học bạ (200, 410): tốt nghiệp 2026, học tập Tốt cả 3 năm, hệ chuyên hoặc giải HSG cấp tỉnh
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, v.ma_nhom, v.ten_nhom, v.mo_ta
FROM xt_cong_thuc ct
JOIN (
            SELECT 'TN_2026' AS ma_nhom, 'Không tốt nghiệp THPT năm 2026' AS ten_nhom, 'Tốt nghiệp THPT năm 2026.' AS mo_ta
  UNION ALL SELECT 'HOC_LUC_TOT', 'Kết quả học tập từng năm lớp 10, 11, 12 chưa đạt Tốt',
                   'Kết quả học tập bậc THPT từng năm lớp 10, 11, 12 đạt mức Tốt.'
  UNION ALL SELECT 'CHUYEN_HOAC_HSG_TINH', 'Không thuộc hệ chuyên và không có giải Nhất/Nhì/Ba HSG cấp tỉnh',
                   'Học sinh hệ chuyên của trường THPT trọng điểm quốc gia/THPT chuyên, hoặc học sinh không chuyên đạt giải Nhất, Nhì, Ba kỳ thi HSG cấp tỉnh/thành phố lớp 11 hoặc 12.'
) v
WHERE ct.de_an_id = @da_ftu AND ct.ma_phuong_thuc_cua_bo IN ('200', '410');

INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, 'DIEN_XET_THANG', 'Không thuộc diện xét tuyển thẳng đã mô hình hóa',
       'Mục 6.1.1 điểm b, c: tham gia/đạt giải Olympic quốc tế; giải Nhất, Nhì, Ba HSG quốc gia.'
FROM xt_cong_thuc ct WHERE ct.de_an_id = @da_ftu AND ct.ma_cong_thuc = 'FTU_XET_THANG';

INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, 'CO_A_LEVEL', 'Không có chứng chỉ A-Level',
       'Chứng chỉ A-Level với môn Toán đạt từ A trở lên (mức điểm môn chưa kiểm tra tự động).'
FROM xt_cong_thuc ct WHERE ct.de_an_id = @da_ftu AND ct.ma_cong_thuc = 'FTU_ALEVEL';

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, v.ma_chi_so, v.khoa, v.toan_tu, v.gia_tri, v.mo_ta
FROM xt_nhom_dieu_kien n
JOIN (
            SELECT 'TN_THPT' AS ma_nhom, 'DA_TOT_NGHIEP_THPT' AS ma_chi_so, '' AS khoa, '=' AS toan_tu, 1 AS gia_tri, 'Đã tốt nghiệp THPT' AS mo_ta
  UNION ALL SELECT 'HOC_LUC_KHA', 'HOC_LUC_MIN_3_NAM', '', '>=', 3, 'Học tập từng năm từ Khá'
  UNION ALL SELECT 'HOC_LUC_KHA', 'TBC_MIN_3_NAM', '', '>=', 7, 'CT trước 2018: TBC từng năm từ 7,0'
  UNION ALL SELECT 'REN_LUYEN_KHA', 'REN_LUYEN_MIN_3_NAM', '', '>=', 3, 'Rèn luyện từng năm từ Khá'
  UNION ALL SELECT 'TN_2026', 'NAM_TOT_NGHIEP', '', '=', 2026, 'Tốt nghiệp năm 2026'
  UNION ALL SELECT 'HOC_LUC_TOT', 'HOC_LUC_MIN_3_NAM', '', '>=', 4, 'Học tập từng năm đạt Tốt'
  UNION ALL SELECT 'CHUYEN_HOAC_HSG_TINH', 'HE_CHUYEN', '', '=', 1, 'Học sinh hệ chuyên'
  UNION ALL SELECT 'CHUYEN_HOAC_HSG_TINH', 'THANH_TICH', 'HSG-TINH', '<=', 3, 'Giải Nhất/Nhì/Ba HSG cấp tỉnh'
  UNION ALL SELECT 'DIEN_XET_THANG', 'THANH_TICH', 'HSG-QG', '<=', 3, 'Giải Nhất/Nhì/Ba HSG quốc gia'
  UNION ALL SELECT 'DIEN_XET_THANG', 'THANH_TICH', 'HSG-QT', '<=', 9, 'Tham gia hoặc đạt giải Olympic quốc tế'
  UNION ALL SELECT 'CO_A_LEVEL', 'CO_CHUNG_CHI', 'GCE_A_LEVEL', '=', 1, 'Có chứng chỉ A-Level còn hạn'
) v ON v.ma_nhom = n.ma_nhom
WHERE n.de_an_id = @da_ftu;

-- ---------------------------------------------------------------------
-- 1.5 Điểm thưởng (Phụ lục 2 mục 1.2) - thang 30, chỉ lấy một mức cao nhất
-- ---------------------------------------------------------------------
INSERT INTO xt_diem_cong (de_an_id, cong_thuc_id, loai_diem_cong, nhom_cong, ma_chi_so, khoa, toan_tu, gia_tri_so, diem_cong, mo_ta) VALUES
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'HSG-QT',  '<=', 9, 3.0, 'Tham gia/đạt giải Olympic quốc tế'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'HSG-QG',  '<=', 1, 3.0, 'Giải Nhất HSG quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'HSG-QG',  '<=', 2, 2.0, 'Giải Nhì HSG quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'HSG-QG',  '<=', 3, 1.5, 'Giải Ba HSG quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'HSG-QG',  '<=', 4, 1.0, 'Giải Khuyến khích HSG quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'NCKH-QT', '<=', 9, 3.0, 'Tham gia/đạt giải KHKT quốc tế'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'NCKH-QG', '<=', 1, 2.0, 'Giải Nhất KHKT quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'NCKH-QG', '<=', 2, 1.5, 'Giải Nhì KHKT quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'NCKH-QG', '<=', 3, 1.0, 'Giải Ba KHKT quốc gia'),
(@da_ftu, NULL, 'DIEM_THUONG', 'GIAI_THUONG', 'THANH_TICH', 'NCKH-QG', '<=', 4, 0.5, 'Giải Tư KHKT quốc gia');

-- ---------------------------------------------------------------------
-- 1.6 Học phí dự kiến 2026-2027 (mục II.11)
-- ---------------------------------------------------------------------
INSERT INTO dats_hoc_phi (de_an_id, de_an_chuong_trinh_id, nam_hoc, hoc_phi_tu, hoc_phi_den, ghi_chu)
SELECT c.de_an_id, c.id, '2026-2027',
       CASE WHEN c.ten_chuong_trinh LIKE 'CT TT i-Hons%' THEN 88000000
            WHEN c.ten_chuong_trinh LIKE 'CT TT %'  THEN 77000000
            WHEN c.ten_chuong_trinh LIKE 'CT CLC %' THEN 50000000
            WHEN c.ten_chuong_trinh LIKE 'CT TH %'  THEN 34000000
            WHEN c.ten_chuong_trinh LIKE 'CT TC %'  THEN 28000000
            WHEN c.ten_chuong_trinh IN ('CT ĐHNNQT Quản trị khách sạn', 'CT ĐHNNQT Marketing số',
                                        'CT ĐHNNQT Truyền thông Marketing tích hợp', 'CT ĐHNNQT Kinh doanh số toàn cầu') THEN 65000000
            ELSE 50000000 END,
       CASE WHEN c.ten_chuong_trinh LIKE 'CT TT i-Hons%' THEN 88000000
            WHEN c.ten_chuong_trinh LIKE 'CT TT %'  THEN 80000000
            WHEN c.ten_chuong_trinh LIKE 'CT CLC %' THEN 54000000
            WHEN c.ten_chuong_trinh LIKE 'CT TH %'  THEN 39000000
            WHEN c.ten_chuong_trinh LIKE 'CT TC %'  THEN 32000000
            WHEN c.ten_chuong_trinh IN ('CT ĐHNNQT Quản trị khách sạn', 'CT ĐHNNQT Marketing số',
                                        'CT ĐHNNQT Truyền thông Marketing tích hợp', 'CT ĐHNNQT Kinh doanh số toàn cầu') THEN 70000000
            ELSE 54000000 END,
       IF(c.ten_chuong_trinh LIKE 'CT TT i-Hons%', 'Học phí gốc khoảng 125 triệu/năm; trường cấp học bổng khoảng 30% cho khóa 2026.', NULL)
FROM dats_chuong_trinh_dao_tao c
WHERE c.de_an_id = @da_ftu
  AND (c.ten_chuong_trinh LIKE 'CT TT %' OR c.ten_chuong_trinh LIKE 'CT CLC %' OR c.ten_chuong_trinh LIKE 'CT TH %'
       OR c.ten_chuong_trinh LIKE 'CT TC %' OR c.ten_chuong_trinh LIKE 'CT ĐHNNQT %' OR c.ten_chuong_trinh LIKE 'CT ĐHPTQT %');

-- ---------------------------------------------------------------------
-- 1.7 Địa điểm đào tạo: gắn tỉnh cho cơ sở và gắn cơ sở cho chương trình (đang NULL)
--     Mã xét tuyển NTS* = TP.HCM; NTHKK23 = Quảng Ninh; còn lại = Hà Nội (Phụ lục 1).
-- ---------------------------------------------------------------------
UPDATE dats_tru_so ts
JOIN dm_tinh_thanh t ON t.ma_tinh = CASE WHEN ts.ten_co_so LIKE '%Hồ Chí Minh%' THEN '79'
                                         WHEN ts.ten_co_so LIKE '%Quảng Ninh%' THEN '22' ELSE '01' END
SET ts.tinh_thanh_id = t.id
WHERE ts.de_an_id = @da_ftu;

UPDATE dats_chuong_trinh_dao_tao c
JOIN dats_tru_so ts
  ON ts.de_an_id = c.de_an_id
 AND ts.ten_co_so = CASE WHEN c.ma_xet_tuyen LIKE 'NTS%' THEN 'Cơ sở TP. Hồ Chí Minh'
                         WHEN c.ma_xet_tuyen = 'NTHKK23' THEN 'Cơ sở Quảng Ninh' ELSE 'Trụ sở chính' END
SET c.co_so_id = ts.id
WHERE c.de_an_id = @da_ftu AND c.co_so_id IS NULL;

-- =====================================================================
-- PHẦN 2. ĐẠI HỌC BÁCH KHOA HÀ NỘI
-- =====================================================================
INSERT INTO xt_cong_thuc
  (de_an_id, ma_cong_thuc, ten_cong_thuc, ma_phuong_thuc_cua_bo, kieu_tinh, nguon_diem_mon, thang_diem, he_so_nhan,
   ap_dung_diem_cong, ap_dung_uu_tien, trang_thai, mo_ta_cong_thuc, ghi_chu)
VALUES
(@da_bka, 'BKA_THPT_30', 'Điểm thi THPT theo tổ hợp - thang 30', '100', 'TO_HOP_MON', 'THI_THPT', 30, 1, 1, 1, 1,
 'M1 + M2 + M3 + điểm ưu tiên', 'Đang dùng cho mọi tổ hợp ngoài K01, kể cả tổ hợp in đậm (xem ghi chú đầu file).'),
(@da_bka, 'BKA_THPT_K01', 'Điểm thi THPT tổ hợp K01', '100', 'TO_HOP_MON', 'THI_THPT', 30, 0.5, 1, 1, 1,
 '[Toán x 3 + Ngữ văn x 1 + (Lý/Hóa/Sinh/Tin) x 2] x 1/2', 'Mục II.3.'),
(@da_bka, 'BKA_THPT_TOAN_X2', 'Điểm thi THPT - tổ hợp in đậm, Toán hệ số 2', '100', 'TO_HOP_MON', 'THI_THPT', 30, 0.75, 1, 1, 0,
 '(Toán x 2 + M2 + M3) x 3/4',
 'CHƯA DÙNG. QĐ 2466 chỉ ghi "tính môn Toán nhân hệ số 2", không ghi cách quy về thang 30; he_so_nhan 3/4 là giả định cần đối chiếu. Khi xác định được tổ hợp in đậm thì đổi cong_thuc_id của các xt_phuong_an tương ứng và bật trang_thai.'),
(@da_bka, 'BKA_TSA', 'Điểm thi Đánh giá tư duy (TSA)', '401', 'THANH_PHAN', NULL, 100, 1, 1, 1, 1,
 'Điểm TSA năm 2025 hoặc 2026', 'Ngưỡng điểm TSA: thông báo sau.'),
(@da_bka, 'BKA_XTTN_11', 'Xét tuyển tài năng 1.1 - xét tuyển thẳng', '301', 'CHI_DIEU_KIEN', NULL, 30, 1, 0, 0, 1,
 'Không tính điểm', 'Mục II.1.1.'),
(@da_bka, 'BKA_XTTN_12', 'Xét tuyển tài năng 1.2 - chứng chỉ quốc tế (chưa tự tính điểm)', '415', 'THU_CONG', NULL, 100, 1, 0, 0, 1,
 'Theo quy định xét tuyển tài năng của ĐHBK Hà Nội', 'Mục II.1.2.'),
(@da_bka, 'BKA_XTTN_13', 'Xét tuyển tài năng 1.3 - hồ sơ năng lực và phỏng vấn (chưa tự tính điểm)', '500', 'THU_CONG', NULL, 100, 1, 0, 0, 1,
 'Điểm HSNL = điểm tư duy (TSA x 40/60, tối đa 40) + điểm thành tích (tối đa 50) + điểm thưởng (tối đa 10)', 'Mục II.1.3.');

INSERT INTO xt_cong_thuc_he_so_mon (cong_thuc_id, mon_hoc_id, nhom_mon, he_so)
SELECT ct.id, mh.id, NULL, CASE mh.ma_mon_hoc WHEN 'TOAN' THEN 3 WHEN 'VAN' THEN 1 ELSE 2 END
FROM xt_cong_thuc ct JOIN dm_mon_hoc mh ON mh.ma_mon_hoc IN ('TOAN', 'VAN', 'LY', 'HOA', 'SINH', 'TIN')
WHERE ct.de_an_id = @da_bka AND ct.ma_cong_thuc = 'BKA_THPT_K01';

INSERT INTO xt_cong_thuc_he_so_mon (cong_thuc_id, mon_hoc_id, nhom_mon, he_so)
SELECT ct.id, mh.id, NULL, 2
FROM xt_cong_thuc ct JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'TOAN'
WHERE ct.de_an_id = @da_bka AND ct.ma_cong_thuc = 'BKA_THPT_TOAN_X2';

INSERT INTO xt_cong_thuc_thanh_phan (cong_thuc_id, vi_tri, ten_thanh_phan, loai_nguon, bai_thi_id, he_so, nam_thi_tu, nam_thi_den)
SELECT ct.id, 1, 'Điểm TSA', 'BAI_THI', bt.id, 1, 2025, 2026
FROM xt_cong_thuc ct JOIN dm_bai_thi_danh_gia bt ON bt.ma_bai_thi = 'TSA'
WHERE ct.de_an_id = @da_bka AND ct.ma_cong_thuc = 'BKA_TSA';

-- Phương án: điểm thi THPT theo từng tổ hợp (K01 dùng công thức riêng)
INSERT INTO xt_phuong_an (de_an_id, de_an_chuong_trinh_id, de_an_phuong_thuc_id, cong_thuc_id, to_hop_id)
SELECT c.de_an_id, c.id, pt.id, ct.id, th.id
FROM dats_phuong_thuc pt
JOIN dats_chuong_trinh_dao_tao c ON c.id = pt.de_an_chuong_trinh_id
JOIN dm_to_hop_mon_hoc th ON JSON_CONTAINS(pt.to_hop_mon_hoc, JSON_QUOTE(th.ma_to_hop))
JOIN xt_cong_thuc ct ON ct.de_an_id = c.de_an_id
                    AND ct.ma_cong_thuc = IF(th.ma_to_hop = 'K01', 'BKA_THPT_K01', 'BKA_THPT_30')
WHERE c.de_an_id = @da_bka AND pt.ma_phuong_thuc_cua_bo = '100'
  AND EXISTS (SELECT 1 FROM dm_to_hop_mon_hoc_chi_tiet x WHERE x.to_hop_id = th.id);

-- Phương án: TSA và xét tuyển tài năng
INSERT INTO xt_phuong_an (de_an_id, de_an_chuong_trinh_id, de_an_phuong_thuc_id, cong_thuc_id, to_hop_id)
SELECT c.de_an_id, c.id, pt.id, ct.id, NULL
FROM dats_phuong_thuc pt
JOIN dats_chuong_trinh_dao_tao c ON c.id = pt.de_an_chuong_trinh_id
JOIN xt_cong_thuc ct ON ct.de_an_id = c.de_an_id
                    AND ct.ma_cong_thuc = CASE pt.ma_phuong_thuc_cua_bo WHEN '401' THEN 'BKA_TSA' WHEN '301' THEN 'BKA_XTTN_11'
                                                                        WHEN '415' THEN 'BKA_XTTN_12' WHEN '500' THEN 'BKA_XTTN_13' END
WHERE c.de_an_id = @da_bka;

-- Điều kiện theo phương thức
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta) VALUES
(@da_bka, NULL, 'TN_THPT', 'Chưa tốt nghiệp THPT', 'Thí sinh đã tốt nghiệp THPT.');

INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, ma_nhom, ten_nhom, mo_ta)
SELECT ct.de_an_id, ct.id, v.ma_nhom, v.ten_nhom, v.mo_ta
FROM xt_cong_thuc ct
JOIN (
            SELECT 'BKA_XTTN_11' AS ma_ct, 'TN_2026' AS ma_nhom, 'Không tốt nghiệp THPT năm 2026' AS ten_nhom, 'Thí sinh tốt nghiệp THPT năm 2026.' AS mo_ta
  UNION ALL SELECT 'BKA_XTTN_11', 'GIAI_QUOC_GIA', 'Không có giải Nhất/Nhì/Ba HSG, KHKT quốc gia hoặc dự thi quốc tế',
                   'Được triệu tập thi chọn đội tuyển Olympic hoặc giải Nhất, Nhì, Ba HSG quốc gia (Toán, Lý, Hóa, Sinh, Tin, Ngoại ngữ); đội tuyển KHKT quốc tế hoặc giải Nhất, Nhì, Ba KHKT quốc gia; không quá 3 năm.'
  UNION ALL SELECT 'BKA_XTTN_12', 'TBC_8', 'Điểm TBC từng năm lớp 10, 11, 12 dưới 8,00',
                   'Điểm TBC các môn văn hóa từng năm lớp 10, 11, 12 đạt từ 8,00 trở lên.'
  UNION ALL SELECT 'BKA_XTTN_12', 'CO_CHUNG_CHI_QT', 'Không có SAT, ACT, A-Level, AP hoặc IB còn hiệu lực',
                   'Có ít nhất một chứng chỉ quốc tế còn hiệu lực: SAT, ACT, A-Level, AP, IB.'
  UNION ALL SELECT 'BKA_XTTN_13', 'TN_2026', 'Không tốt nghiệp THPT năm 2026', 'Thí sinh tốt nghiệp THPT năm 2026.'
  UNION ALL SELECT 'BKA_XTTN_13', 'TBC_8', 'Điểm TBC từng năm lớp 10, 11, 12 dưới 8,00',
                   'Điểm TBC các môn văn hóa từng năm lớp 10, 11, 12 đạt từ 8,00 trở lên.'
  UNION ALL SELECT 'BKA_XTTN_13', 'THANH_TICH_HSNL', 'Không có thành tích thuộc diện hồ sơ năng lực',
                   'Một trong: giải HSG quốc gia hoặc cấp tỉnh; giải Ba trở lên cuộc thi KHKT; dự Đường lên đỉnh Olympia từ vòng tháng (chưa có mã thành tích); học hệ chuyên cả 3 năm.'
) v ON v.ma_ct = ct.ma_cong_thuc
WHERE ct.de_an_id = @da_bka;

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, v.ma_chi_so, v.khoa, v.toan_tu, v.gia_tri, v.mo_ta
FROM xt_nhom_dieu_kien n
JOIN (
            SELECT 'TN_THPT' AS ma_nhom, 'DA_TOT_NGHIEP_THPT' AS ma_chi_so, '' AS khoa, '=' AS toan_tu, 1 AS gia_tri, 'Đã tốt nghiệp THPT' AS mo_ta
  UNION ALL SELECT 'TN_2026', 'NAM_TOT_NGHIEP', '', '=', 2026, 'Tốt nghiệp năm 2026'
  UNION ALL SELECT 'GIAI_QUOC_GIA', 'THANH_TICH', 'HSG-QG',  '<=', 3, 'Giải Nhất/Nhì/Ba HSG quốc gia'
  UNION ALL SELECT 'GIAI_QUOC_GIA', 'THANH_TICH', 'NCKH-QG', '<=', 3, 'Giải Nhất/Nhì/Ba KHKT quốc gia'
  UNION ALL SELECT 'GIAI_QUOC_GIA', 'THANH_TICH', 'HSG-QT',  '<=', 9, 'Dự thi Olympic quốc tế'
  UNION ALL SELECT 'GIAI_QUOC_GIA', 'THANH_TICH', 'NCKH-QT', '<=', 9, 'Đội tuyển KHKT quốc tế'
  UNION ALL SELECT 'TBC_8', 'TBC_MIN_3_NAM', '', '>=', 8, 'TBC từng năm từ 8,00'
  UNION ALL SELECT 'CO_CHUNG_CHI_QT', 'DIEM_BAI_THI', 'SAT', '>', 0, 'Có điểm SAT'
  UNION ALL SELECT 'CO_CHUNG_CHI_QT', 'DIEM_BAI_THI', 'ACT', '>', 0, 'Có điểm ACT'
  UNION ALL SELECT 'CO_CHUNG_CHI_QT', 'CO_CHUNG_CHI', 'GCE_A_LEVEL', '=', 1, 'Có A-Level'
  UNION ALL SELECT 'CO_CHUNG_CHI_QT', 'CO_CHUNG_CHI', 'AP', '=', 1, 'Có AP'
  UNION ALL SELECT 'CO_CHUNG_CHI_QT', 'CO_CHUNG_CHI', 'IB_DP', '=', 1, 'Có IB'
  UNION ALL SELECT 'THANH_TICH_HSNL', 'THANH_TICH', 'HSG-QG',    '<=', 4, 'Đạt giải HSG quốc gia'
  UNION ALL SELECT 'THANH_TICH_HSNL', 'THANH_TICH', 'HSG-TINH',  '<=', 4, 'Đạt giải HSG cấp tỉnh/thành phố'
  UNION ALL SELECT 'THANH_TICH_HSNL', 'THANH_TICH', 'NCKH-QG',   '<=', 3, 'Giải Ba trở lên KHKT (Bộ GDĐT)'
  UNION ALL SELECT 'THANH_TICH_HSNL', 'THANH_TICH', 'NCKH-TINH', '<=', 3, 'Giải Ba trở lên KHKT (Sở GDĐT)'
  UNION ALL SELECT 'THANH_TICH_HSNL', 'HE_CHUYEN', '', '=', 1, 'Học hệ chuyên cả 3 năm'
) v ON v.ma_nhom = n.ma_nhom
WHERE n.de_an_id = @da_bka;

-- Điều kiện ngoại ngữ riêng của chương trình (mục III), áp dụng cho mọi phương thức
INSERT INTO xt_nhom_dieu_kien (de_an_id, cong_thuc_id, de_an_chuong_trinh_id, ma_nhom, ten_nhom, mo_ta)
SELECT c.de_an_id, NULL, c.id,
       IF(c.ma_xet_tuyen IN ('FL2', 'TROY-IT'), 'NGOAI_NGU_IELTS_55', 'NGOAI_NGU_B1'),
       IF(c.ma_xet_tuyen IN ('FL2', 'TROY-IT'), 'Chưa đạt IELTS 5.5 hoặc tương đương',
          'Chưa đạt VSTEP B1 / IELTS 5.0 / điểm thi THPT môn ngoại ngữ từ 6,5'),
       IF(c.ma_xet_tuyen IN ('FL2', 'TROY-IT'),
          'Chương trình liên kết đào tạo quốc tế: IELTS Academic từ 5.5 hoặc tương đương.',
          'Chương trình tiên tiến dạy bằng tiếng Anh, FL1, FL3, FL4: VSTEP B1 trở lên, hoặc IELTS Academic từ 5.0 hoặc tương đương, hoặc điểm thi THPT 2026 môn tiếng Anh (tiếng Trung với FL3, tiếng Hàn với FL4) từ 6,5.')
FROM dats_chuong_trinh_dao_tao c
WHERE c.de_an_id = @da_bka
  AND (c.ma_xet_tuyen IN ('FL1', 'FL2', 'FL3', 'FL4', 'TROY-IT') OR c.ghi_chu LIKE 'Nhóm: elitech_tien_tien_tieng_anh%');

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, 'DIEM_CHUNG_CHI', 'IELTS', '>=', IF(n.ma_nhom = 'NGOAI_NGU_IELTS_55', 5.5, 5.0), 'IELTS Academic'
FROM xt_nhom_dieu_kien n
WHERE n.de_an_id = @da_bka AND n.ma_nhom IN ('NGOAI_NGU_IELTS_55', 'NGOAI_NGU_B1');

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, 'DIEM_CHUNG_CHI', 'VSTEP', '>=', 3, 'VSTEP bậc 3 (B1) trở lên; hs_chung_chi.diem ghi số bậc'
FROM xt_nhom_dieu_kien n
WHERE n.de_an_id = @da_bka AND n.ma_nhom = 'NGOAI_NGU_B1';

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, 'DIEM_THI_THPT', 'ANH', '>=', 6.5, 'Điểm thi THPT môn tiếng Anh từ 6,5'
FROM xt_nhom_dieu_kien n
WHERE n.de_an_id = @da_bka AND n.ma_nhom = 'NGOAI_NGU_B1';

INSERT INTO xt_dieu_kien (nhom_dieu_kien_id, ma_chi_so, khoa, toan_tu, gia_tri_so, mo_ta)
SELECT n.id, 'DIEM_THI_THPT', IF(c.ma_xet_tuyen = 'FL3', 'TRUNG', 'HAN'), '>=', 6.5,
       IF(c.ma_xet_tuyen = 'FL3', 'Điểm thi THPT môn tiếng Trung từ 6,5', 'Điểm thi THPT môn tiếng Hàn từ 6,5')
FROM xt_nhom_dieu_kien n
JOIN dats_chuong_trinh_dao_tao c ON c.id = n.de_an_chuong_trinh_id
WHERE n.de_an_id = @da_bka AND n.ma_nhom = 'NGOAI_NGU_B1' AND c.ma_xet_tuyen IN ('FL3', 'FL4');

-- Kiểm tra nhanh số dòng đã nạp
SELECT da.ma_truong,
       (SELECT COUNT(*) FROM xt_cong_thuc x WHERE x.de_an_id = da.id) AS so_cong_thuc,
       (SELECT COUNT(*) FROM xt_phuong_an x WHERE x.de_an_id = da.id) AS so_phuong_an,
       (SELECT COUNT(DISTINCT x.de_an_chuong_trinh_id) FROM xt_phuong_an x WHERE x.de_an_id = da.id) AS so_chuong_trinh,
       (SELECT COUNT(*) FROM xt_nhom_dieu_kien x WHERE x.de_an_id = da.id) AS so_nhom_dieu_kien,
       (SELECT COUNT(*) FROM xt_diem_cong x WHERE x.de_an_id = da.id) AS so_diem_cong
FROM dats_tuyen_sinh da WHERE da.id IN (@da_ftu, @da_bka);
