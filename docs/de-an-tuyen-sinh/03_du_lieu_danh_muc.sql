-- =====================================================================
-- 03_du_lieu_danh_muc.sql  -  Dữ liệu nền dùng chung cho mọi đề án
--   1. dm_chi_so_xet_tuyen
--   2. dm_to_hop_mon_hoc_chi_tiet (đang rỗng) dựng từ dm_to_hop_mon_hoc.ds_mon_hoc
--   3. Bộ tiêu chí chấm điểm phù hợp mặc định
-- Chạy lại nhiều lần được.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 1. Danh mục chỉ số
-- ---------------------------------------------------------------------
INSERT INTO dm_chi_so_xet_tuyen (ma_chi_so, ten_chi_so, kieu_khoa, y_nghia_gia_tri) VALUES
('DA_TOT_NGHIEP_THPT',  'Đã tốt nghiệp THPT hoặc tương đương', NULL, '1 = có, 0 = chưa'),
('NAM_TOT_NGHIEP',      'Năm tốt nghiệp THPT', NULL, 'Năm, ví dụ 2026'),
('HE_CHUYEN',           'Học hệ chuyên cả 3 năm THPT', NULL, '1 = có, 0 = không'),
('MON_CHUYEN',          'Môn chuyên', 'MON_HOC', '1 nếu đúng môn ở cột khoa'),
('TBC_LOP',             'Điểm trung bình chung cả năm của một lớp', 'LOP', 'Thang 10; khoa = 10/11/12'),
('TBC_MIN_3_NAM',       'Điểm trung bình chung thấp nhất trong 3 năm lớp 10, 11, 12', NULL, 'Thang 10; chỉ có khi đủ cả 3 năm. Dùng cho điều kiện "từng năm đạt từ ..."'),
('HOC_LUC_LOP',         'Kết quả học tập cả năm của một lớp', 'LOP', '4 = Tốt/Giỏi, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu'),
('HOC_LUC_MIN_3_NAM',   'Kết quả học tập thấp nhất trong 3 năm', NULL, 'Như HOC_LUC_LOP; chỉ có khi đủ cả 3 năm'),
('REN_LUYEN_LOP',       'Kết quả rèn luyện/hạnh kiểm cả năm của một lớp', 'LOP', '4 = Tốt, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu'),
('REN_LUYEN_MIN_3_NAM', 'Kết quả rèn luyện thấp nhất trong 3 năm', NULL, 'Như REN_LUYEN_LOP; chỉ có khi đủ cả 3 năm'),
('DIEM_THI_THPT',       'Điểm thi tốt nghiệp THPT của một môn', 'MON_HOC', 'Thang 10'),
('DIEM_HOC_BA_TB',      'Điểm học bạ trung bình cả năm lớp 10, 11, 12 của một môn', 'MON_HOC', 'Thang 10; chỉ có khi đủ cả 3 năm'),
('DIEM_BAI_THI',        'Điểm cao nhất của một bài thi ĐGNL/ĐGTD/SAT/ACT', 'BAI_THI', 'Theo thang gốc của bài thi'),
('DIEM_CHUNG_CHI',      'Điểm cao nhất của một chứng chỉ còn hạn', 'CHUNG_CHI', 'Theo thang của chứng chỉ (VSTEP: số bậc)'),
('CO_CHUNG_CHI',        'Có chứng chỉ còn hạn (không xét điểm)', 'CHUNG_CHI', '1 = có'),
('THANH_TICH',          'Giải cao nhất của một loại thành tích', 'THANH_TICH', '1 = Nhất/Vàng, 2 = Nhì/Bạc, 3 = Ba/Đồng, 4 = Khuyến khích/Tư, 9 = chỉ tham gia. Số càng nhỏ giải càng cao nên điều kiện viết dạng <=')
ON DUPLICATE KEY UPDATE ten_chi_so = VALUES(ten_chi_so), kieu_khoa = VALUES(kieu_khoa), y_nghia_gia_tri = VALUES(y_nghia_gia_tri);

-- ---------------------------------------------------------------------
-- 2. Chi tiết tổ hợp môn.
--    thu_tu_mon là VỊ TRÍ tính điểm. Nhiều môn cùng một thu_tu_mon nghĩa là
--    "chọn một trong các môn" (thủ tục lấy môn điểm cao nhất), ví dụ K01.
-- ---------------------------------------------------------------------
INSERT IGNORE INTO dm_to_hop_mon_hoc_chi_tiet (to_hop_id, mon_hoc_id, thu_tu_mon)
SELECT th.id, mh.id, n.i + 1
FROM dm_to_hop_mon_hoc th
JOIN (SELECT 0 AS i UNION ALL SELECT 1 UNION ALL SELECT 2) n
JOIN dm_mon_hoc mh
  ON mh.ma_mon_hoc = CONVERT(JSON_UNQUOTE(JSON_EXTRACT(th.ds_mon_hoc, CONCAT('$[', n.i, ']'))) USING utf8mb4) COLLATE utf8mb4_unicode_ci
WHERE JSON_LENGTH(th.ds_mon_hoc) = 3;

-- K01 (ĐH Bách khoa Hà Nội): Toán, Ngữ văn và MỘT trong Lý/Hóa/Sinh/Tin
INSERT IGNORE INTO dm_to_hop_mon_hoc_chi_tiet (to_hop_id, mon_hoc_id, thu_tu_mon, ghi_chu)
SELECT th.id, mh.id,
       CASE mh.ma_mon_hoc WHEN 'TOAN' THEN 1 WHEN 'VAN' THEN 2 ELSE 3 END,
       CASE WHEN mh.ma_mon_hoc IN ('TOAN', 'VAN') THEN NULL ELSE 'Chọn một trong Lý/Hóa/Sinh/Tin' END
FROM dm_to_hop_mon_hoc th
JOIN dm_mon_hoc mh ON mh.ma_mon_hoc IN ('TOAN', 'VAN', 'LY', 'HOA', 'SINH', 'TIN')
WHERE th.ma_to_hop = 'K01';

-- Bỏ các tổ hợp không dựng đủ 3 vị trí (mã môn trong ds_mon_hoc không có ở dm_mon_hoc)
DELETE c FROM dm_to_hop_mon_hoc_chi_tiet c
JOIN (SELECT to_hop_id FROM dm_to_hop_mon_hoc_chi_tiet
      GROUP BY to_hop_id HAVING COUNT(DISTINCT thu_tu_mon) < 3) b ON b.to_hop_id = c.to_hop_id;

-- ---------------------------------------------------------------------
-- 3. Bộ tiêu chí mặc định. Trọng số và các mốc là THAM SỐ NGHIỆP VỤ, chỉnh ở đây.
-- ---------------------------------------------------------------------
INSERT INTO xt_bo_tieu_chi (ma_bo, ten_bo, mac_dinh, ghi_chu)
VALUES ('MAC_DINH_V1', 'Bộ tiêu chí mặc định v1', 1,
        'Điểm phù hợp = trung bình có trọng số của các tiêu chí có dữ liệu.')
ON DUPLICATE KEY UPDATE ten_bo = VALUES(ten_bo);
SET @bo := (SELECT id FROM xt_bo_tieu_chi WHERE ma_bo = 'MAC_DINH_V1');

INSERT INTO xt_tieu_chi_phu_hop (bo_tieu_chi_id, ma_tieu_chi, trong_so, mo_ta) VALUES
(@bo, 'KHA_NANG_TRUNG_TUYEN', 50, 'Chênh lệch giữa điểm xét của học sinh và điểm chuẩn năm gần nhất'),
(@bo, 'NGANH',                25, 'Chương trình thuộc ngành / nhóm ngành / lĩnh vực học sinh chọn'),
(@bo, 'HOC_PHI',              15, 'Học phí so với ngân sách của gia đình'),
(@bo, 'VI_TRI',               10, 'Cơ sở đào tạo ở tỉnh / vùng học sinh mong muốn')
ON DUPLICATE KEY UPDATE trong_so = VALUES(trong_so), mo_ta = VALUES(mo_ta);

DELETE FROM xt_muc_phu_hop WHERE bo_tieu_chi_id = @bo;
INSERT INTO xt_muc_phu_hop (bo_tieu_chi_id, loai_muc, gia_tri_tu, gia_tri_den, diem, nhan) VALUES
-- chênh lệch = điểm xét - điểm chuẩn, cùng quy về thang 30
(@bo, 'KHA_NANG_TRUNG_TUYEN',  2.00,  NULL, 100, 'An toàn'),
(@bo, 'KHA_NANG_TRUNG_TUYEN',  1.00,  2.00,  90, 'Khả năng cao'),
(@bo, 'KHA_NANG_TRUNG_TUYEN',  0.00,  1.00,  75, 'Vừa sức'),
(@bo, 'KHA_NANG_TRUNG_TUYEN', -1.00,  0.00,  50, 'Cần cố gắng'),
(@bo, 'KHA_NANG_TRUNG_TUYEN', -2.00, -1.00,  25, 'Thử thách'),
(@bo, 'KHA_NANG_TRUNG_TUYEN',  NULL, -2.00,   5, 'Rất khó'),
-- xếp loại theo điểm phù hợp tổng hợp
(@bo, 'TONG_HOP', 80.00,  NULL, NULL, 'Rất phù hợp'),
(@bo, 'TONG_HOP', 65.00, 80.00, NULL, 'Phù hợp'),
(@bo, 'TONG_HOP', 50.00, 65.00, NULL, 'Có thể cân nhắc'),
(@bo, 'TONG_HOP',  NULL, 50.00, NULL, 'Ít phù hợp');
