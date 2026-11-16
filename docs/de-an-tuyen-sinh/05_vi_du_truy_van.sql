-- =====================================================================
-- 05_vi_du_truy_van.sql  -  DỮ LIỆU THỬ + CÁC TRUY VẤN MẪU
--
-- !!! File này tạo 2 hồ sơ học sinh giả lập và một số điểm chuẩn GIẢ ĐỊNH
-- !!! (ghi_chu = 'DEMO - SO LIEU GIA DINH'). Không phải điểm chuẩn thật.
-- !!! Chỉ chạy trên môi trường thử; khối dọn dẹp ở cuối file.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- A. Dữ liệu thử
-- ---------------------------------------------------------------------
DELETE FROM hs_ho_so WHERE ten_ho_so LIKE '[DEMO]%';
DELETE FROM xt_diem_chuan WHERE ghi_chu = 'DEMO - SO LIEU GIA DINH';

-- Học sinh A: chuyên Toán, KV2-NT, học lực Tốt, có IELTS 7.0, HSA 112, TSA 72.5, giải Nhì HSG tỉnh
INSERT INTO hs_ho_so (ten_ho_so, nam_tot_nghiep, da_tot_nghiep, chuong_trinh_thpt, he_chuyen, mon_chuyen_id,
                      tinh_thanh_id, khu_vuc_uu_tien_id, ngan_sach_hoc_phi_nam)
SELECT '[DEMO] Học sinh A', 2026, 1, 'GDPT_2018', 1, (SELECT id FROM dm_mon_hoc WHERE ma_mon_hoc = 'TOAN'),
       (SELECT id FROM dm_tinh_thanh WHERE ma_tinh = '01'),
       (SELECT id FROM dm_khu_vuc_uu_tien WHERE ma_khu_vuc = 'KV2-NT'), 60000000;
SET @hs_a := LAST_INSERT_ID();

INSERT INTO hs_ket_qua_nam_hoc (ho_so_id, lop, diem_tb_chung, hoc_luc, ren_luyen) VALUES
(@hs_a, 10, 8.9, 4, 4), (@hs_a, 11, 9.0, 4, 4), (@hs_a, 12, 9.2, 4, 4);

INSERT INTO hs_diem_mon (ho_so_id, mon_hoc_id, nguon_diem, lop, hoc_ky, diem, nam)
SELECT @hs_a, mh.id, v.nguon, v.lop, 0, v.diem, v.nam
FROM (
            SELECT 'TOAN' AS ma, 'THI_THPT' AS nguon, 0 AS lop, 9.00 AS diem, 2026 AS nam
  UNION ALL SELECT 'LY',  'THI_THPT', 0, 8.50, 2026
  UNION ALL SELECT 'HOA', 'THI_THPT', 0, 8.75, 2026
  UNION ALL SELECT 'ANH', 'THI_THPT', 0, 8.00, 2026
  UNION ALL SELECT 'VAN', 'THI_THPT', 0, 8.00, 2026
  UNION ALL SELECT 'TOAN', 'HOC_BA', 10, 9.2, 2024 UNION ALL SELECT 'TOAN', 'HOC_BA', 11, 9.4, 2025 UNION ALL SELECT 'TOAN', 'HOC_BA', 12, 9.6, 2026
  UNION ALL SELECT 'LY',   'HOC_BA', 10, 9.0, 2024 UNION ALL SELECT 'LY',   'HOC_BA', 11, 9.1, 2025 UNION ALL SELECT 'LY',   'HOC_BA', 12, 9.2, 2026
  UNION ALL SELECT 'HOA',  'HOC_BA', 10, 8.8, 2024 UNION ALL SELECT 'HOA',  'HOC_BA', 11, 9.0, 2025 UNION ALL SELECT 'HOA',  'HOC_BA', 12, 9.2, 2026
  UNION ALL SELECT 'VAN',  'HOC_BA', 10, 8.0, 2024 UNION ALL SELECT 'VAN',  'HOC_BA', 11, 8.2, 2025 UNION ALL SELECT 'VAN',  'HOC_BA', 12, 8.4, 2026
  UNION ALL SELECT 'ANH',  'HOC_BA', 10, 9.0, 2024 UNION ALL SELECT 'ANH',  'HOC_BA', 11, 9.2, 2025 UNION ALL SELECT 'ANH',  'HOC_BA', 12, 9.4, 2026
) v JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = v.ma;

INSERT INTO hs_chung_chi (ho_so_id, chung_chi_id, diem, ngay_cap, ngay_het_han)
SELECT @hs_a, id, 7.0, '2025-12-01', '2027-12-01' FROM dm_bang_cap_chung_chi WHERE ma_chung_chi = 'IELTS';

INSERT INTO hs_diem_bai_thi (ho_so_id, bai_thi_id, nam_thi, diem, phan_tu_chon)
SELECT @hs_a, id, 2026, IF(ma_bai_thi = 'HSA', 112, 72.5), IF(ma_bai_thi = 'HSA', 'KHOA_HOC', NULL)
FROM dm_bai_thi_danh_gia WHERE ma_bai_thi IN ('HSA', 'TSA');

INSERT INTO hs_thanh_tich (ho_so_id, thanh_tich_id, mon_hoc_id, muc_giai, nam_dat_giai, lop)
SELECT @hs_a, tt.id, mh.id, 2, 2026, 12
FROM dm_thanh_tich_hoc_tap_nghien_cuu tt JOIN dm_mon_hoc mh ON mh.ma_mon_hoc = 'TOAN'
WHERE tt.ma_thanh_tich = 'HSG-TINH';

INSERT INTO hs_tieu_chi_mong_muon (ho_so_id, loai, gia_tri) VALUES (@hs_a, 'TINH_THANH', '01');

-- Học sinh B: KV1, học lực Khá, chỉ có điểm thi THPT khối A00 mức trung bình khá
INSERT INTO hs_ho_so (ten_ho_so, nam_tot_nghiep, da_tot_nghiep, khu_vuc_uu_tien_id)
SELECT '[DEMO] Học sinh B', 2026, 1, (SELECT id FROM dm_khu_vuc_uu_tien WHERE ma_khu_vuc = 'KV1');
SET @hs_b := LAST_INSERT_ID();
INSERT INTO hs_ket_qua_nam_hoc (ho_so_id, lop, diem_tb_chung, hoc_luc, ren_luyen) VALUES
(@hs_b, 10, 7.2, 3, 4), (@hs_b, 11, 7.4, 3, 4), (@hs_b, 12, 7.6, 3, 4);
INSERT INTO hs_diem_mon (ho_so_id, mon_hoc_id, nguon_diem, diem, nam)
SELECT @hs_b, id, 'THI_THPT', CASE ma_mon_hoc WHEN 'TOAN' THEN 7.0 WHEN 'LY' THEN 7.5 ELSE 7.0 END, 2026
FROM dm_mon_hoc WHERE ma_mon_hoc IN ('TOAN', 'LY', 'HOA');

-- Điểm chuẩn GIẢ ĐỊNH (không phải số liệu thật)
INSERT INTO xt_diem_chuan (ma_truong, nam_tuyen_sinh, ma_xet_tuyen, ma_phuong_thuc_cua_bo, diem_chuan, thang_diem, ghi_chu) VALUES
('NTH', 2025, 'NTHKT02', NULL, 27.00, 30, 'DEMO - SO LIEU GIA DINH'),
('NTH', 2025, 'NTHKD06', NULL, 26.50, 30, 'DEMO - SO LIEU GIA DINH'),
('NTH', 2025, 'NTHKE16', NULL, 25.50, 30, 'DEMO - SO LIEU GIA DINH'),
('NTH', 2025, 'NTHCN18', NULL, 35.00, 40, 'DEMO - SO LIEU GIA DINH'),
('NTH', 2025, 'NTHKK23', NULL, 24.00, 30, 'DEMO - SO LIEU GIA DINH'),
('NTH', 2025, 'NTSKT01', NULL, 26.80, 30, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'IT1', '100', 28.50,  30, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'IT1', '401', 76.00, 100, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'ME1', '100', 26.00,  30, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'ME1', '401', 62.00, 100, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'BF1', '100', 23.00,  30, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'BF1', '401', 55.00, 100, 'DEMO - SO LIEU GIA DINH'),
('BKA', 2025, 'FL1', '100', 24.50,  30, 'DEMO - SO LIEU GIA DINH');

-- ---------------------------------------------------------------------
-- B. Chạy đánh giá
-- ---------------------------------------------------------------------
CALL sp_xt_danh_gia(@hs_a, 2026, NULL, @lan_a);
CALL sp_xt_danh_gia(@hs_b, 2026, NULL, @lan_b);

-- ---------------------------------------------------------------------
-- C. Truy vấn mẫu
-- ---------------------------------------------------------------------

-- C1. Danh sách chương trình phù hợp nhất của học sinh A (mỗi chương trình một dòng, theo phương án tốt nhất)
SELECT r.thu_hang, r.ma_truong, c.ma_xet_tuyen, c.ten_chuong_trinh,
       ct.ma_cong_thuc, th.ma_to_hop, r.diem_xet, r.thang_diem,
       k.diem_chuan_tham_chieu AS diem_chuan, k.nam_diem_chuan, r.chenh_lech_30,
       r.diem_kha_nang, r.diem_hoc_phi, r.diem_vi_tri, r.diem_phu_hop, r.xep_loai
FROM xt_ket_qua_chuong_trinh r
JOIN xt_ket_qua_phuong_an k ON k.id = r.ket_qua_phuong_an_id
JOIN dats_chuong_trinh_dao_tao c ON c.id = r.de_an_chuong_trinh_id
JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
LEFT JOIN dm_to_hop_mon_hoc th ON th.id = k.to_hop_id
WHERE r.lan_danh_gia_id = @lan_a
ORDER BY r.thu_hang
LIMIT 15;

-- C2. Đánh giá theo TRƯỜNG (view v_xt_ket_qua_truong): điểm trường = trung bình 3 chương trình tốt nhất
SELECT v.ma_truong, t.ten_truong, v.so_chuong_trinh_du_dieu_kien, v.so_chuong_trinh_da_cham,
       v.so_chuong_trinh_phu_hop, v.diem_phu_hop_cao_nhat, v.diem_truong
FROM v_xt_ket_qua_truong v
JOIN dm_truong t ON t.ma_truong = v.ma_truong
WHERE v.lan_danh_gia_id = @lan_a
ORDER BY v.diem_truong DESC;

-- C3. Mọi phương án của học sinh A vào một mã xét tuyển (giải thích cách tính)
SELECT c.ten_chuong_trinh, ct.ma_cong_thuc, th.ma_to_hop,
       ROUND(k.diem_goc, 2) AS diem_goc, k.diem_cong, k.diem_uu_tien, k.diem_xet, k.thang_diem,
       ROUND(k.tb_mon, 2) AS tb_mon, k.tong_thpt_to_hop, k.du_dieu_kien, k.ly_do_khong_dat, k.chenh_lech_30
FROM xt_ket_qua_phuong_an k
JOIN dats_chuong_trinh_dao_tao c ON c.id = k.de_an_chuong_trinh_id
JOIN dats_tuyen_sinh da ON da.id = c.de_an_id
JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
LEFT JOIN dm_to_hop_mon_hoc th ON th.id = k.to_hop_id
WHERE k.lan_danh_gia_id = @lan_a AND da.ma_truong = 'NTH' AND c.ma_xet_tuyen = 'NTHKT02'
ORDER BY c.id, k.diem_xet / k.thang_diem DESC;

-- C4. Lọc: chương trình tại Hà Nội, học phí trong ngân sách, điểm xét không thấp hơn điểm chuẩn tham chiếu
SELECT r.ma_truong, c.ma_xet_tuyen, c.ten_chuong_trinh, k.diem_xet, k.diem_chuan_tham_chieu, k.chenh_lech_30,
       hp.hoc_phi_tu, r.diem_phu_hop
FROM xt_ket_qua_chuong_trinh r
JOIN xt_ket_qua_phuong_an k ON k.id = r.ket_qua_phuong_an_id
JOIN dats_chuong_trinh_dao_tao c ON c.id = r.de_an_chuong_trinh_id
JOIN xt_lan_danh_gia l ON l.id = r.lan_danh_gia_id
JOIN hs_ho_so h ON h.id = l.ho_so_id
LEFT JOIN dats_hoc_phi hp ON hp.de_an_chuong_trinh_id = c.id
WHERE r.lan_danh_gia_id = @lan_a
  AND r.diem_vi_tri = 100
  AND k.chenh_lech_30 >= 0
  AND (hp.hoc_phi_tu IS NULL OR hp.hoc_phi_tu <= h.ngan_sach_hoc_phi_nam)
ORDER BY r.diem_phu_hop DESC, k.chenh_lech_30 DESC;

-- C5. Phương thức không tự tính điểm nhưng học sinh A đủ điều kiện nộp hồ sơ (xét tài năng...)
SELECT da.ma_truong, ct.ma_cong_thuc, ct.ten_cong_thuc, COUNT(*) AS so_chuong_trinh
FROM xt_ket_qua_phuong_an k
JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
JOIN dats_tuyen_sinh da ON da.id = ct.de_an_id
WHERE k.lan_danh_gia_id = @lan_a AND k.kieu_tinh IN ('THU_CONG', 'CHI_DIEU_KIEN') AND k.du_dieu_kien = 1
GROUP BY da.ma_truong, ct.ma_cong_thuc, ct.ten_cong_thuc;

-- C6. Học sinh B: vì sao không đạt (gom theo lý do)
SELECT da.ma_truong, ct.ma_cong_thuc, k.du_dieu_kien, k.ly_do_khong_dat,
       COUNT(*) AS so_phuong_an, MIN(k.diem_xet) AS diem_xet_thap_nhat, MAX(k.diem_xet) AS diem_xet_cao_nhat
FROM xt_ket_qua_phuong_an k
JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
JOIN dats_tuyen_sinh da ON da.id = ct.de_an_id
WHERE k.lan_danh_gia_id = @lan_b
GROUP BY da.ma_truong, ct.ma_cong_thuc, k.du_dieu_kien, k.ly_do_khong_dat
ORDER BY da.ma_truong, ct.ma_cong_thuc;

-- C7. Truy vấn trực tiếp không qua thủ tục: chương trình nào nhận tổ hợp mà học sinh có đủ điểm thi THPT
SELECT da.ma_truong, c.ma_xet_tuyen, c.ten_chuong_trinh, th.ma_to_hop, SUM(d.diem) AS tong_3_mon
FROM xt_phuong_an pa
JOIN xt_cong_thuc ct ON ct.id = pa.cong_thuc_id AND ct.ma_phuong_thuc_cua_bo = '100'
JOIN dats_tuyen_sinh da ON da.id = pa.de_an_id AND da.nam_tuyen_sinh = 2026
JOIN dats_chuong_trinh_dao_tao c ON c.id = pa.de_an_chuong_trinh_id
JOIN dm_to_hop_mon_hoc th ON th.id = pa.to_hop_id AND th.ma_to_hop IN ('A00', 'A01', 'D01', 'D07')
JOIN dm_to_hop_mon_hoc_chi_tiet tc ON tc.to_hop_id = th.id
JOIN hs_diem_mon d ON d.mon_hoc_id = tc.mon_hoc_id AND d.ho_so_id = @hs_b AND d.nguon_diem = 'THI_THPT'
GROUP BY da.ma_truong, c.id, c.ma_xet_tuyen, c.ten_chuong_trinh, th.ma_to_hop
HAVING COUNT(*) = 3
ORDER BY tong_3_mon DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- D. Dọn dữ liệu thử (bỏ chú thích để chạy)
-- ---------------------------------------------------------------------
-- DELETE FROM hs_ho_so WHERE ten_ho_so LIKE '[DEMO]%';          -- kéo theo hs_*, xt_lan_danh_gia, xt_ket_qua_*
-- DELETE FROM xt_diem_chuan WHERE ghi_chu = 'DEMO - SO LIEU GIA DINH';
