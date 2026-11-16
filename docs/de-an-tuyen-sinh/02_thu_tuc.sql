-- =====================================================================
-- 02_thu_tuc.sql  -  Hàm và thủ tục tính điểm, xét điều kiện, chấm phù hợp
-- MySQL 5.7 (không dùng CTE / window function).
--
--   fn_xt_so_sanh          so sánh giá trị với ngưỡng theo toán tử
--   sp_hs_cap_nhat_chi_so  dựng lại hs_chi_so cho một hồ sơ
--   sp_xt_tinh_diem        tính điểm + xét điều kiện mọi phương án (nội bộ)
--   sp_xt_danh_gia         điểm vào chính: chạy toàn bộ và chấm điểm phù hợp
--
-- Cách gọi:  CALL sp_xt_danh_gia(<ho_so_id>, 2026, NULL, @lan);
--            SELECT * FROM xt_ket_qua_chuong_trinh WHERE lan_danh_gia_id = @lan ORDER BY thu_hang;
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
DELIMITER $$

DROP FUNCTION IF EXISTS fn_xt_so_sanh $$
CREATE FUNCTION fn_xt_so_sanh(p_gia_tri DECIMAL(12,3), p_toan_tu VARCHAR(2), p_nguong DECIMAL(12,3))
RETURNS TINYINT(1) DETERMINISTIC NO SQL
BEGIN
  IF p_gia_tri IS NULL OR p_nguong IS NULL THEN
    RETURN 0;
  END IF;
  RETURN CASE p_toan_tu
    WHEN '>=' THEN p_gia_tri >= p_nguong
    WHEN '>'  THEN p_gia_tri >  p_nguong
    WHEN '='  THEN p_gia_tri =  p_nguong
    WHEN '<=' THEN p_gia_tri <= p_nguong
    WHEN '<'  THEN p_gia_tri <  p_nguong
    WHEN '!=' THEN p_gia_tri <> p_nguong
    ELSE 0 END;
END $$

-- ---------------------------------------------------------------------
-- Dựng lại bảng dẫn xuất hs_chi_so. Gọi sau mỗi lần học sinh sửa hồ sơ
-- (sp_xt_danh_gia tự gọi).
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_hs_cap_nhat_chi_so $$
CREATE PROCEDURE sp_hs_cap_nhat_chi_so(IN p_ho_so_id BIGINT UNSIGNED)
BEGIN
  DELETE FROM hs_chi_so WHERE ho_so_id = p_ho_so_id;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT id, 'DA_TOT_NGHIEP_THPT', '', da_tot_nghiep FROM hs_ho_so WHERE id = p_ho_so_id;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT id, 'NAM_TOT_NGHIEP', '', nam_tot_nghiep FROM hs_ho_so
  WHERE id = p_ho_so_id AND nam_tot_nghiep IS NOT NULL;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT id, 'HE_CHUYEN', '', he_chuyen FROM hs_ho_so WHERE id = p_ho_so_id;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT h.id, 'MON_CHUYEN', mh.ma_mon_hoc, 1
  FROM hs_ho_so h JOIN dm_mon_hoc mh ON mh.id = h.mon_chuyen_id
  WHERE h.id = p_ho_so_id AND h.he_chuyen = 1;

  -- Kết quả từng năm và mức thấp nhất của 3 năm (dùng cho điều kiện "từng năm lớp 10, 11, 12 đạt ...")
  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'TBC_LOP', CAST(lop AS CHAR), diem_tb_chung FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND diem_tb_chung IS NOT NULL;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'HOC_LUC_LOP', CAST(lop AS CHAR), hoc_luc FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND hoc_luc IS NOT NULL;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'REN_LUYEN_LOP', CAST(lop AS CHAR), ren_luyen FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND ren_luyen IS NOT NULL;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'TBC_MIN_3_NAM', '', MIN(diem_tb_chung) FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND lop IN (10, 11, 12) AND diem_tb_chung IS NOT NULL
  GROUP BY ho_so_id HAVING COUNT(DISTINCT lop) = 3;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'HOC_LUC_MIN_3_NAM', '', MIN(hoc_luc) FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND lop IN (10, 11, 12) AND hoc_luc IS NOT NULL
  GROUP BY ho_so_id HAVING COUNT(DISTINCT lop) = 3;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT ho_so_id, 'REN_LUYEN_MIN_3_NAM', '', MIN(ren_luyen) FROM hs_ket_qua_nam_hoc
  WHERE ho_so_id = p_ho_so_id AND lop IN (10, 11, 12) AND ren_luyen IS NOT NULL
  GROUP BY ho_so_id HAVING COUNT(DISTINCT lop) = 3;

  -- Điểm môn
  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT d.ho_so_id, 'DIEM_THI_THPT', mh.ma_mon_hoc, MAX(d.diem)
  FROM hs_diem_mon d JOIN dm_mon_hoc mh ON mh.id = d.mon_hoc_id
  WHERE d.ho_so_id = p_ho_so_id AND d.nguon_diem = 'THI_THPT'
  GROUP BY d.ho_so_id, mh.ma_mon_hoc;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT d.ho_so_id, 'DIEM_HOC_BA_TB', mh.ma_mon_hoc, AVG(d.diem)
  FROM hs_diem_mon d JOIN dm_mon_hoc mh ON mh.id = d.mon_hoc_id
  WHERE d.ho_so_id = p_ho_so_id AND d.nguon_diem = 'HOC_BA' AND d.hoc_ky = 0 AND d.lop IN (10, 11, 12)
  GROUP BY d.ho_so_id, mh.ma_mon_hoc HAVING COUNT(DISTINCT d.lop) = 3;

  -- Bài thi, chứng chỉ (còn hạn), thành tích (giải cao nhất = muc_giai nhỏ nhất)
  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT b.ho_so_id, 'DIEM_BAI_THI', bt.ma_bai_thi, MAX(b.diem)
  FROM hs_diem_bai_thi b JOIN dm_bai_thi_danh_gia bt ON bt.id = b.bai_thi_id
  WHERE b.ho_so_id = p_ho_so_id AND bt.ma_bai_thi IS NOT NULL
  GROUP BY b.ho_so_id, bt.ma_bai_thi;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT c.ho_so_id, 'DIEM_CHUNG_CHI', cc.ma_chung_chi, MAX(c.diem)
  FROM hs_chung_chi c JOIN dm_bang_cap_chung_chi cc ON cc.id = c.chung_chi_id
  WHERE c.ho_so_id = p_ho_so_id AND c.diem IS NOT NULL AND cc.ma_chung_chi IS NOT NULL
    AND (c.ngay_het_han IS NULL OR c.ngay_het_han >= CURDATE())
  GROUP BY c.ho_so_id, cc.ma_chung_chi;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT c.ho_so_id, 'CO_CHUNG_CHI', cc.ma_chung_chi, 1
  FROM hs_chung_chi c JOIN dm_bang_cap_chung_chi cc ON cc.id = c.chung_chi_id
  WHERE c.ho_so_id = p_ho_so_id AND cc.ma_chung_chi IS NOT NULL
    AND (c.ngay_het_han IS NULL OR c.ngay_het_han >= CURDATE())
  GROUP BY c.ho_so_id, cc.ma_chung_chi;

  INSERT INTO hs_chi_so (ho_so_id, ma_chi_so, khoa, gia_tri_so)
  SELECT t.ho_so_id, 'THANH_TICH', tt.ma_thanh_tich, MIN(t.muc_giai)
  FROM hs_thanh_tich t JOIN dm_thanh_tich_hoc_tap_nghien_cuu tt ON tt.id = t.thanh_tich_id
  WHERE t.ho_so_id = p_ho_so_id
  GROUP BY t.ho_so_id, tt.ma_thanh_tich;
END $$

-- ---------------------------------------------------------------------
-- Tính điểm xét và xét điều kiện cho mọi phương án của các đề án trong năm.
-- Ghi vào xt_ket_qua_phuong_an. Chỉ ghi phương án học sinh CÓ ĐỦ DỮ LIỆU để
-- tính (đủ môn của tổ hợp / có bài thi) hoặc phương án không tính điểm mà
-- học sinh đạt hết điều kiện.
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_xt_tinh_diem $$
CREATE PROCEDURE sp_xt_tinh_diem(IN p_lan_danh_gia_id BIGINT UNSIGNED)
BEGIN
  DECLARE v_ho_so BIGINT UNSIGNED;
  DECLARE v_nam SMALLINT UNSIGNED;
  DECLARE v_nam_tn SMALLINT UNSIGNED;
  DECLARE v_muc_kv DECIMAL(5,2) DEFAULT 0;
  DECLARE v_muc_dt DECIMAL(5,2) DEFAULT 0;
  DECLARE v_muc_ut DECIMAL(5,2) DEFAULT 0;

  SELECT ho_so_id, nam_tuyen_sinh INTO v_ho_so, v_nam
  FROM xt_lan_danh_gia WHERE id = p_lan_danh_gia_id;

  -- Mức ưu tiên (thang 30). Ưu tiên khu vực chỉ hưởng trong năm tốt nghiệp và năm kế tiếp (Điều 7 khoản 1c).
  SELECT h.nam_tot_nghiep, COALESCE(kv.diem_cong, 0), COALESCE(dt.diem_cong, 0)
    INTO v_nam_tn, v_muc_kv, v_muc_dt
  FROM hs_ho_so h
  LEFT JOIN dm_khu_vuc_uu_tien kv ON kv.id = h.khu_vuc_uu_tien_id
  LEFT JOIN dm_doi_tuong_uu_tien dt ON dt.id = h.doi_tuong_uu_tien_id
  WHERE h.id = v_ho_so;
  IF v_nam_tn IS NOT NULL AND v_nam > v_nam_tn + 1 THEN
    SET v_muc_kv = 0;
  END IF;
  SET v_muc_ut = v_muc_kv + v_muc_dt;

  DELETE FROM xt_ket_qua_phuong_an WHERE lan_danh_gia_id = p_lan_danh_gia_id;

  DROP TEMPORARY TABLE IF EXISTS tmp_xt_mon, tmp_xt_nn, tmp_xt_tp, tmp_xt_nhom, tmp_xt_dk, tmp_xt_cong;

  -- 1. Điểm từng môn của học sinh: thi THPT và trung bình học bạ cả năm lớp 10, 11, 12
  CREATE TEMPORARY TABLE tmp_xt_mon (
    mon_hoc_id INT NOT NULL PRIMARY KEY, diem_thpt DECIMAL(7,4) NULL, diem_hb DECIMAL(7,4) NULL
  ) ENGINE=MEMORY;
  INSERT INTO tmp_xt_mon (mon_hoc_id, diem_thpt)
  SELECT mon_hoc_id, MAX(diem) FROM hs_diem_mon
  WHERE ho_so_id = v_ho_so AND nguon_diem = 'THI_THPT' GROUP BY mon_hoc_id;
  INSERT INTO tmp_xt_mon (mon_hoc_id, diem_hb)
  SELECT mon_hoc_id, AVG(diem) FROM hs_diem_mon
  WHERE ho_so_id = v_ho_so AND nguon_diem = 'HOC_BA' AND hoc_ky = 0 AND lop IN (10, 11, 12)
  GROUP BY mon_hoc_id HAVING COUNT(DISTINCT lop) = 3
  ON DUPLICATE KEY UPDATE diem_hb = VALUES(diem_hb);

  -- 2. Điểm môn ngoại ngữ quy đổi từ chứng chỉ còn hạn, theo từng bảng quy đổi
  CREATE TEMPORARY TABLE tmp_xt_nn (
    bang_quy_doi_id BIGINT UNSIGNED NOT NULL, mon_hoc_id INT NOT NULL, diem DECIMAL(7,3) NOT NULL,
    PRIMARY KEY (bang_quy_doi_id, mon_hoc_id)
  ) ENGINE=MEMORY;
  INSERT INTO tmp_xt_nn (bang_quy_doi_id, mon_hoc_id, diem)
  SELECT q.bang_quy_doi_id, q.mon_hoc_id,
         MAX(q.diem_quy_doi + COALESCE(q.he_so_noi_suy * (cc.diem - q.diem_tu), 0))
  FROM hs_chung_chi cc
  JOIN xt_bang_quy_doi_chi_tiet q
    ON q.chung_chi_id = cc.chung_chi_id AND q.mon_hoc_id IS NOT NULL AND q.dat_nguong = 1
   AND (q.cap_do IS NULL OR q.cap_do = cc.cap_do)
   AND (q.diem_tu IS NULL OR cc.diem >= q.diem_tu)
   AND (q.diem_den IS NULL OR cc.diem <= q.diem_den)
  WHERE cc.ho_so_id = v_ho_so AND (cc.ngay_het_han IS NULL OR cc.ngay_het_han >= CURDATE())
  GROUP BY q.bang_quy_doi_id, q.mon_hoc_id;

  -- 3. Giá trị từng thành phần (bài thi / chứng chỉ) của các công thức kiểu THANH_PHAN
  CREATE TEMPORARY TABLE tmp_xt_tp (
    thanh_phan_id BIGINT UNSIGNED NOT NULL PRIMARY KEY, gia_tri DECIMAL(10,4) NOT NULL
  ) ENGINE=MEMORY;
  INSERT INTO tmp_xt_tp (thanh_phan_id, gia_tri)
  SELECT tp.id,
         MAX(CASE WHEN tp.bang_quy_doi_id IS NULL THEN b.diem
                  ELSE q.diem_quy_doi + COALESCE(q.he_so_noi_suy * (b.diem - q.diem_tu), 0) END)
  FROM xt_cong_thuc_thanh_phan tp
  JOIN hs_diem_bai_thi b
    ON b.bai_thi_id = tp.bai_thi_id AND b.ho_so_id = v_ho_so
   AND (tp.nam_thi_tu IS NULL OR b.nam_thi >= tp.nam_thi_tu)
   AND (tp.nam_thi_den IS NULL OR b.nam_thi <= tp.nam_thi_den)
   AND (tp.yeu_cau_phan_tu_chon IS NULL OR b.phan_tu_chon = tp.yeu_cau_phan_tu_chon)
  LEFT JOIN xt_bang_quy_doi_chi_tiet q
    ON q.bang_quy_doi_id = tp.bang_quy_doi_id AND q.bai_thi_id = b.bai_thi_id AND q.dat_nguong = 1
   AND (q.diem_tu IS NULL OR b.diem >= q.diem_tu)
   AND (q.diem_den IS NULL OR b.diem <= q.diem_den)
  WHERE tp.loai_nguon = 'BAI_THI' AND (tp.bang_quy_doi_id IS NULL OR q.id IS NOT NULL)
  GROUP BY tp.id;
  INSERT INTO tmp_xt_tp (thanh_phan_id, gia_tri)
  SELECT tp.id, MAX(q.diem_quy_doi + COALESCE(q.he_so_noi_suy * (cc.diem - q.diem_tu), 0))
  FROM xt_cong_thuc_thanh_phan tp
  JOIN xt_bang_quy_doi_chi_tiet q
    ON q.bang_quy_doi_id = tp.bang_quy_doi_id AND q.chung_chi_id IS NOT NULL AND q.dat_nguong = 1
   AND (tp.mon_hoc_id IS NULL OR q.mon_hoc_id = tp.mon_hoc_id)
  JOIN hs_chung_chi cc
    ON cc.chung_chi_id = q.chung_chi_id AND cc.ho_so_id = v_ho_so
   AND (cc.ngay_het_han IS NULL OR cc.ngay_het_han >= CURDATE())
   AND (q.cap_do IS NULL OR q.cap_do = cc.cap_do)
   AND (q.diem_tu IS NULL OR cc.diem >= q.diem_tu)
   AND (q.diem_den IS NULL OR cc.diem <= q.diem_den)
  WHERE tp.loai_nguon = 'CHUNG_CHI'
  GROUP BY tp.id;

  -- 4. Trạng thái đạt/không đạt của từng nhóm điều kiện bắt buộc (OR trong nhóm)
  CREATE TEMPORARY TABLE tmp_xt_nhom (
    nhom_id BIGINT UNSIGNED NOT NULL PRIMARY KEY, de_an_id BIGINT UNSIGNED NOT NULL,
    cong_thuc_id BIGINT UNSIGNED NULL, chuong_trinh_id BIGINT UNSIGNED NULL,
    ten_nhom VARCHAR(255) NOT NULL, dat TINYINT NOT NULL,
    KEY (de_an_id)
  ) ENGINE=MEMORY DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
  INSERT INTO tmp_xt_nhom (nhom_id, de_an_id, cong_thuc_id, chuong_trinh_id, ten_nhom, dat)
  SELECT n.id, n.de_an_id, n.cong_thuc_id, n.de_an_chuong_trinh_id, n.ten_nhom,
         COALESCE(MAX(fn_xt_so_sanh(cs.gia_tri_so, d.toan_tu, d.gia_tri_so)), 0)
  FROM xt_nhom_dieu_kien n
  JOIN dats_tuyen_sinh da ON da.id = n.de_an_id AND da.nam_tuyen_sinh = v_nam
  LEFT JOIN xt_dieu_kien d ON d.nhom_dieu_kien_id = n.id
  LEFT JOIN hs_chi_so cs ON cs.ho_so_id = v_ho_so AND cs.ma_chi_so = d.ma_chi_so AND cs.khoa = d.khoa
  WHERE n.bat_buoc = 1
  GROUP BY n.id, n.de_an_id, n.cong_thuc_id, n.de_an_chuong_trinh_id, n.ten_nhom;

  -- 5a. Phương án kiểu TO_HOP_MON.
  --     Mỗi vị trí (thu_tu_mon) của tổ hợp lấy môn có điểm cao nhất nếu vị trí đó cho chọn nhiều môn.
  INSERT INTO xt_ket_qua_phuong_an
    (lan_danh_gia_id, phuong_an_id, de_an_chuong_trinh_id, cong_thuc_id, to_hop_id, kieu_tinh, thang_diem,
     diem_goc, tb_mon, tong_thpt_to_hop)
  SELECT p_lan_danh_gia_id, x.phuong_an_id, x.chuong_trinh_id, x.cong_thuc_id, x.to_hop_id, 'TO_HOP_MON', x.thang_diem,
         SUM(x.diem_vt) * x.he_so_nhan,
         SUM(x.diem_mon) / NULLIF(COUNT(x.diem_mon), 0),
         CASE WHEN COUNT(x.diem_nguong) = COUNT(*) THEN SUM(x.diem_nguong) END
  FROM (
    SELECT pa.id AS phuong_an_id, pa.de_an_chuong_trinh_id AS chuong_trinh_id, pa.cong_thuc_id, pa.to_hop_id,
           ct.thang_diem, ct.he_so_nhan, ctm.thu_tu_mon,
           MAX(COALESCE(hm.he_so, hn.he_so, 1) *
               CASE WHEN mh.nhom_mon = 'Ngoại ngữ' AND ct.thay_ngoai_ngu = 'BAT_BUOC' THEN nn.diem
                    WHEN mh.nhom_mon = 'Ngoại ngữ' AND ct.thay_ngoai_ngu = 'DUOC_PHEP'
                      THEN NULLIF(GREATEST(COALESCE(IF(ct.nguon_diem_mon = 'THI_THPT', m.diem_thpt, m.diem_hb), -1), COALESCE(nn.diem, -1)), -1)
                    ELSE IF(ct.nguon_diem_mon = 'THI_THPT', m.diem_thpt, m.diem_hb) END) AS diem_vt,
           MAX(CASE WHEN mh.nhom_mon = 'Ngoại ngữ' AND ct.thay_ngoai_ngu = 'BAT_BUOC' THEN NULL
                    ELSE IF(ct.nguon_diem_mon = 'THI_THPT', m.diem_thpt, m.diem_hb) END) AS diem_mon,
           MAX(CASE WHEN mh.nhom_mon = 'Ngoại ngữ' AND ct.thay_ngoai_ngu = 'BAT_BUOC' THEN nn.diem
                    WHEN mh.nhom_mon = 'Ngoại ngữ' AND ct.thay_ngoai_ngu = 'DUOC_PHEP'
                      THEN NULLIF(GREATEST(COALESCE(m.diem_thpt, -1), COALESCE(nn.diem, -1)), -1)
                    ELSE m.diem_thpt END) AS diem_nguong
    FROM xt_phuong_an pa
    JOIN dats_tuyen_sinh da ON da.id = pa.de_an_id AND da.nam_tuyen_sinh = v_nam
    JOIN xt_cong_thuc ct ON ct.id = pa.cong_thuc_id AND ct.kieu_tinh = 'TO_HOP_MON' AND ct.trang_thai = 1
    JOIN dm_to_hop_mon_hoc_chi_tiet ctm ON ctm.to_hop_id = pa.to_hop_id
    JOIN dm_mon_hoc mh ON mh.id = ctm.mon_hoc_id
    LEFT JOIN tmp_xt_mon m ON m.mon_hoc_id = ctm.mon_hoc_id
    LEFT JOIN tmp_xt_nn nn ON nn.bang_quy_doi_id = ct.bang_quy_doi_ngoai_ngu_id AND nn.mon_hoc_id = ctm.mon_hoc_id
    LEFT JOIN xt_cong_thuc_he_so_mon hm ON hm.cong_thuc_id = ct.id AND hm.mon_hoc_id = ctm.mon_hoc_id
    LEFT JOIN xt_cong_thuc_he_so_mon hn ON hn.cong_thuc_id = ct.id AND hn.mon_hoc_id IS NULL AND hn.nhom_mon = mh.nhom_mon
    WHERE pa.trang_thai = 1
    GROUP BY pa.id, pa.de_an_chuong_trinh_id, pa.cong_thuc_id, pa.to_hop_id, ct.thang_diem, ct.he_so_nhan, ctm.thu_tu_mon
  ) x
  GROUP BY x.phuong_an_id, x.chuong_trinh_id, x.cong_thuc_id, x.to_hop_id, x.thang_diem, x.he_so_nhan
  HAVING COUNT(x.diem_vt) = COUNT(*);

  -- 5b. Phương án kiểu THANH_PHAN (bài thi / chứng chỉ quy đổi)
  INSERT INTO xt_ket_qua_phuong_an
    (lan_danh_gia_id, phuong_an_id, de_an_chuong_trinh_id, cong_thuc_id, to_hop_id, kieu_tinh, thang_diem, diem_goc)
  SELECT p_lan_danh_gia_id, x.phuong_an_id, x.chuong_trinh_id, x.cong_thuc_id, NULL, 'THANH_PHAN', x.thang_diem,
         SUM(x.diem_vt) * x.he_so_nhan
  FROM (
    SELECT pa.id AS phuong_an_id, pa.de_an_chuong_trinh_id AS chuong_trinh_id, pa.cong_thuc_id,
           ct.thang_diem, ct.he_so_nhan, tp.vi_tri, MAX(tp.he_so * t.gia_tri) AS diem_vt
    FROM xt_phuong_an pa
    JOIN dats_tuyen_sinh da ON da.id = pa.de_an_id AND da.nam_tuyen_sinh = v_nam
    JOIN xt_cong_thuc ct ON ct.id = pa.cong_thuc_id AND ct.kieu_tinh = 'THANH_PHAN' AND ct.trang_thai = 1
    JOIN xt_cong_thuc_thanh_phan tp ON tp.cong_thuc_id = ct.id
    LEFT JOIN tmp_xt_tp t ON t.thanh_phan_id = tp.id
    WHERE pa.trang_thai = 1
    GROUP BY pa.id, pa.de_an_chuong_trinh_id, pa.cong_thuc_id, ct.thang_diem, ct.he_so_nhan, tp.vi_tri
  ) x
  GROUP BY x.phuong_an_id, x.chuong_trinh_id, x.cong_thuc_id, x.thang_diem, x.he_so_nhan
  HAVING COUNT(x.diem_vt) = COUNT(*);

  -- 5c. Phương án không tự tính điểm (xét thẳng, hồ sơ năng lực...): chỉ ghi khi học sinh đạt
  --     mọi nhóm điều kiện và công thức đó có ít nhất một nhóm điều kiện riêng.
  INSERT INTO xt_ket_qua_phuong_an
    (lan_danh_gia_id, phuong_an_id, de_an_chuong_trinh_id, cong_thuc_id, to_hop_id, kieu_tinh, thang_diem)
  SELECT p_lan_danh_gia_id, pa.id, pa.de_an_chuong_trinh_id, pa.cong_thuc_id, pa.to_hop_id, ct.kieu_tinh, ct.thang_diem
  FROM xt_phuong_an pa
  JOIN dats_tuyen_sinh da ON da.id = pa.de_an_id AND da.nam_tuyen_sinh = v_nam
  JOIN xt_cong_thuc ct ON ct.id = pa.cong_thuc_id AND ct.kieu_tinh IN ('CHI_DIEU_KIEN', 'THU_CONG') AND ct.trang_thai = 1
  JOIN tmp_xt_nhom g ON g.de_an_id = pa.de_an_id
                    AND (g.cong_thuc_id IS NULL OR g.cong_thuc_id = pa.cong_thuc_id)
                    AND (g.chuong_trinh_id IS NULL OR g.chuong_trinh_id = pa.de_an_chuong_trinh_id)
  WHERE pa.trang_thai = 1
  GROUP BY pa.id, pa.de_an_chuong_trinh_id, pa.cong_thuc_id, pa.to_hop_id, ct.kieu_tinh, ct.thang_diem
  HAVING SUM(g.dat = 0) = 0 AND SUM(g.cong_thuc_id IS NOT NULL) > 0;

  -- 6. Điểm cộng: mỗi nhóm lấy mức cao nhất, cộng các nhóm, chặn trần 10% thang (Điều 6 khoản 2c)
  CREATE TEMPORARY TABLE tmp_xt_cong (
    cong_thuc_id BIGINT UNSIGNED NOT NULL PRIMARY KEY, diem DECIMAL(6,2) NOT NULL
  ) ENGINE=MEMORY;
  INSERT INTO tmp_xt_cong (cong_thuc_id, diem)
  SELECT g.cong_thuc_id, SUM(g.diem)
  FROM (
    SELECT ct.id AS cong_thuc_id, dc.nhom_cong, MAX(dc.diem_cong) AS diem
    FROM xt_cong_thuc ct
    JOIN dats_tuyen_sinh da ON da.id = ct.de_an_id AND da.nam_tuyen_sinh = v_nam
    JOIN xt_diem_cong dc ON dc.de_an_id = ct.de_an_id AND (dc.cong_thuc_id IS NULL OR dc.cong_thuc_id = ct.id)
    JOIN hs_chi_so cs ON cs.ho_so_id = v_ho_so AND cs.ma_chi_so = dc.ma_chi_so AND cs.khoa = dc.khoa
    WHERE ct.ap_dung_diem_cong = 1 AND fn_xt_so_sanh(cs.gia_tri_so, dc.toan_tu, dc.gia_tri_so) = 1
    GROUP BY ct.id, dc.nhom_cong
  ) g
  GROUP BY g.cong_thuc_id;

  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
  LEFT JOIN tmp_xt_cong c ON c.cong_thuc_id = k.cong_thuc_id
  SET k.diem_cong = ROUND(LEAST(COALESCE(c.diem, 0), 30 * ct.ty_le_diem_cong_toi_da) * ct.thang_diem / 30, 2)
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id AND k.diem_goc IS NOT NULL;

  -- 7. Điểm ưu tiên (Điều 7 khoản 3, 4): quy tổng về thang 30; từ 22,5 trở lên thì giảm dần
  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
  SET k.diem_uu_tien = CASE WHEN ct.ap_dung_uu_tien = 0 THEN 0 ELSE
        ROUND(v_muc_ut * ct.thang_diem / 30 *
              CASE WHEN LEAST(ct.thang_diem, k.diem_goc + k.diem_cong) * 30 / ct.thang_diem >= 22.5
                   THEN (30 - LEAST(ct.thang_diem, k.diem_goc + k.diem_cong) * 30 / ct.thang_diem) / 7.5
                   ELSE 1 END, 2) END
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id AND k.diem_goc IS NOT NULL;

  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
  SET k.diem_xet = ROUND(LEAST(ct.thang_diem, k.diem_goc + k.diem_cong + k.diem_uu_tien), ct.so_le_lam_tron)
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id AND k.diem_goc IS NOT NULL;

  -- 8. Các ngưỡng điểm của công thức
  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_cong_thuc ct ON ct.id = k.cong_thuc_id
  SET k.dat_nguong =
        (ct.diem_san IS NULL OR k.diem_xet >= ct.diem_san)
    AND (ct.nguong_tb_mon IS NULL OR COALESCE(ROUND(k.tb_mon, 2) >= ct.nguong_tb_mon, 0))
    AND (ct.nguong_thpt_to_hop IS NULL OR COALESCE(
          k.tong_thpt_to_hop + v_muc_ut * IF(k.tong_thpt_to_hop >= 22.5, (30 - k.tong_thpt_to_hop) / 7.5, 1)
            >= ct.nguong_thpt_to_hop, 0)),
      k.ly_do_khong_dat = NULLIF(CONCAT_WS('; ',
        CASE WHEN ct.diem_san IS NOT NULL AND k.diem_xet < ct.diem_san
             THEN CONCAT('Điểm xét ', k.diem_xet, ' dưới ngưỡng nhận hồ sơ ', ct.diem_san) END,
        CASE WHEN ct.nguong_tb_mon IS NOT NULL AND COALESCE(ROUND(k.tb_mon, 2) < ct.nguong_tb_mon, 1)
             THEN CONCAT('Trung bình các môn xét ', COALESCE(ROUND(k.tb_mon, 2), '?'), ' dưới ngưỡng ', ct.nguong_tb_mon) END,
        CASE WHEN ct.nguong_thpt_to_hop IS NOT NULL AND k.tong_thpt_to_hop IS NULL
             THEN 'Thiếu điểm thi THPT của tổ hợp để xét ngưỡng'
             WHEN ct.nguong_thpt_to_hop IS NOT NULL
              AND k.tong_thpt_to_hop + v_muc_ut * IF(k.tong_thpt_to_hop >= 22.5, (30 - k.tong_thpt_to_hop) / 7.5, 1) < ct.nguong_thpt_to_hop
             THEN CONCAT('Tổng điểm thi THPT theo tổ hợp (gồm ưu tiên) dưới ngưỡng ', ct.nguong_thpt_to_hop) END
      ), '')
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id AND k.diem_goc IS NOT NULL;

  -- 9. Điều kiện dự tuyển: mọi nhóm áp dụng phải đạt
  CREATE TEMPORARY TABLE tmp_xt_dk (
    ket_qua_id BIGINT UNSIGNED NOT NULL PRIMARY KEY, so_nhom INT NOT NULL, so_dat INT NOT NULL, ly_do VARCHAR(1000) NULL
  ) ENGINE=MEMORY DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
  INSERT INTO tmp_xt_dk (ket_qua_id, so_nhom, so_dat, ly_do)
  SELECT k.id, COUNT(g.nhom_id), COALESCE(SUM(g.dat), 0),
         LEFT(GROUP_CONCAT(CASE WHEN g.dat = 0 THEN g.ten_nhom END ORDER BY g.nhom_id SEPARATOR '; '), 1000)
  FROM xt_ket_qua_phuong_an k
  JOIN xt_phuong_an pa ON pa.id = k.phuong_an_id
  LEFT JOIN tmp_xt_nhom g ON g.de_an_id = pa.de_an_id
                         AND (g.cong_thuc_id IS NULL OR g.cong_thuc_id = pa.cong_thuc_id)
                         AND (g.chuong_trinh_id IS NULL OR g.chuong_trinh_id = pa.de_an_chuong_trinh_id)
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id
  GROUP BY k.id;

  UPDATE xt_ket_qua_phuong_an k
  JOIN tmp_xt_dk d ON d.ket_qua_id = k.id
  SET k.so_nhom_dieu_kien = d.so_nhom,
      k.so_nhom_dat = d.so_dat,
      k.du_dieu_kien = (d.so_nhom = d.so_dat AND COALESCE(k.dat_nguong, 1) = 1),
      k.ly_do_khong_dat = NULLIF(LEFT(CONCAT_WS('; ', d.ly_do, k.ly_do_khong_dat), 1000), '');

  -- 10. Điểm chuẩn tham chiếu: năm gần nhất, ưu tiên dòng khớp tổ hợp rồi khớp phương thức
  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_phuong_an pa ON pa.id = k.phuong_an_id
  JOIN dats_chuong_trinh_dao_tao c ON c.id = pa.de_an_chuong_trinh_id
  JOIN dats_tuyen_sinh da ON da.id = pa.de_an_id
  JOIN xt_cong_thuc ct ON ct.id = pa.cong_thuc_id
  SET k.diem_chuan_id = (
        SELECT dc.id FROM xt_diem_chuan dc
        WHERE dc.ma_truong = da.ma_truong AND dc.ma_xet_tuyen = c.ma_xet_tuyen
          AND dc.nam_tuyen_sinh <= v_nam
          AND (dc.ma_phuong_thuc_cua_bo IS NULL OR dc.ma_phuong_thuc_cua_bo = ct.ma_phuong_thuc_cua_bo)
          AND (dc.to_hop_id IS NULL OR dc.to_hop_id = pa.to_hop_id)
        ORDER BY dc.nam_tuyen_sinh DESC, (dc.to_hop_id IS NOT NULL) DESC,
                 (dc.ma_phuong_thuc_cua_bo IS NOT NULL) DESC, dc.id
        LIMIT 1)
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id AND k.diem_xet IS NOT NULL;

  UPDATE xt_ket_qua_phuong_an k
  JOIN xt_diem_chuan dc ON dc.id = k.diem_chuan_id
  SET k.diem_chuan_tham_chieu = dc.diem_chuan,
      k.nam_diem_chuan = dc.nam_tuyen_sinh,
      k.chenh_lech_30 = ROUND(k.diem_xet * 30 / k.thang_diem - dc.diem_chuan * 30 / dc.thang_diem, 2)
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id;

  DROP TEMPORARY TABLE IF EXISTS tmp_xt_mon, tmp_xt_nn, tmp_xt_tp, tmp_xt_nhom, tmp_xt_dk, tmp_xt_cong;
END $$

-- ---------------------------------------------------------------------
-- Điểm vào chính.
--   p_bo_tieu_chi_id = NULL -> dùng bộ tiêu chí mặc định.
--   p_lan_danh_gia_id (OUT) -> khóa để đọc xt_ket_qua_phuong_an / xt_ket_qua_chuong_trinh.
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_xt_danh_gia $$
CREATE PROCEDURE sp_xt_danh_gia(
  IN p_ho_so_id BIGINT UNSIGNED,
  IN p_nam_tuyen_sinh SMALLINT UNSIGNED,
  IN p_bo_tieu_chi_id BIGINT UNSIGNED,
  OUT p_lan_danh_gia_id BIGINT UNSIGNED)
BEGIN
  DECLARE v_bo BIGINT UNSIGNED;
  DECLARE v_ngan_sach DECIMAL(15,0);
  DECLARE v_w_kn DECIMAL(5,2) DEFAULT 0;
  DECLARE v_w_ng DECIMAL(5,2) DEFAULT 0;
  DECLARE v_w_hp DECIMAL(5,2) DEFAULT 0;
  DECLARE v_w_vt DECIMAL(5,2) DEFAULT 0;
  DECLARE v_co_nganh INT DEFAULT 0;
  DECLARE v_co_vi_tri INT DEFAULT 0;

  SET v_bo = COALESCE(p_bo_tieu_chi_id,
                      (SELECT id FROM xt_bo_tieu_chi ORDER BY mac_dinh DESC, id LIMIT 1));
  IF v_bo IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chua co bo tieu chi cham diem (xt_bo_tieu_chi)';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM hs_ho_so WHERE id = p_ho_so_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Khong tim thay ho so hoc sinh';
  END IF;

  CALL sp_hs_cap_nhat_chi_so(p_ho_so_id);

  INSERT INTO xt_lan_danh_gia (ho_so_id, nam_tuyen_sinh, bo_tieu_chi_id)
  VALUES (p_ho_so_id, p_nam_tuyen_sinh, v_bo);
  SET p_lan_danh_gia_id = LAST_INSERT_ID();

  CALL sp_xt_tinh_diem(p_lan_danh_gia_id);

  -- Mỗi chương trình giữ phương án tốt nhất trong các phương án đủ điều kiện:
  -- xét thẳng trước, rồi đến chênh lệch so với điểm chuẩn lớn nhất, rồi điểm xét (theo tỷ lệ thang) cao nhất.
  INSERT INTO xt_ket_qua_chuong_trinh
    (lan_danh_gia_id, de_an_chuong_trinh_id, ma_truong, ket_qua_phuong_an_id, la_xet_thang, diem_xet, thang_diem, chenh_lech_30)
  SELECT k.lan_danh_gia_id, k.de_an_chuong_trinh_id, da.ma_truong, k.id, (k.kieu_tinh = 'CHI_DIEU_KIEN'),
         k.diem_xet, k.thang_diem, k.chenh_lech_30
  FROM xt_ket_qua_phuong_an k
  JOIN dats_chuong_trinh_dao_tao c ON c.id = k.de_an_chuong_trinh_id
  JOIN dats_tuyen_sinh da ON da.id = c.de_an_id
  WHERE k.lan_danh_gia_id = p_lan_danh_gia_id
    AND k.id = (
      SELECT k2.id FROM xt_ket_qua_phuong_an k2
      WHERE k2.lan_danh_gia_id = p_lan_danh_gia_id
        AND k2.de_an_chuong_trinh_id = k.de_an_chuong_trinh_id
        AND k2.du_dieu_kien = 1
        AND (k2.diem_xet IS NOT NULL OR k2.kieu_tinh = 'CHI_DIEU_KIEN')
      ORDER BY (k2.kieu_tinh = 'CHI_DIEU_KIEN') DESC, (k2.chenh_lech_30 IS NULL), k2.chenh_lech_30 DESC,
               k2.diem_xet / k2.thang_diem DESC, k2.id
      LIMIT 1);

  -- Tiêu chí 1: khả năng trúng tuyển, từ chênh lệch điểm (thang 30) theo các mốc của bộ tiêu chí
  UPDATE xt_ket_qua_chuong_trinh r
  JOIN xt_ket_qua_phuong_an k ON k.id = r.ket_qua_phuong_an_id
  LEFT JOIN xt_muc_phu_hop m
    ON m.bo_tieu_chi_id = v_bo AND m.loai_muc = 'KHA_NANG_TRUNG_TUYEN'
   AND (m.gia_tri_tu IS NULL OR k.chenh_lech_30 >= m.gia_tri_tu)
   AND (m.gia_tri_den IS NULL OR k.chenh_lech_30 < m.gia_tri_den)
   AND k.chenh_lech_30 IS NOT NULL
  SET r.diem_kha_nang = CASE WHEN r.la_xet_thang = 1 THEN 100 ELSE m.diem END
  WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;

  -- Tiêu chí 2: ngành. 100 = đúng ngành / nhóm ngành / lĩnh vực đã chọn; 60 = cùng nhóm với một ngành đã chọn
  SELECT COUNT(*) INTO v_co_nganh FROM hs_tieu_chi_mong_muon
  WHERE ho_so_id = p_ho_so_id AND loai IN ('NGANH', 'NHOM_NGANH', 'LINH_VUC');
  IF v_co_nganh > 0 THEN
    UPDATE xt_ket_qua_chuong_trinh r
    JOIN dats_chuong_trinh_dao_tao c ON c.id = r.de_an_chuong_trinh_id
    LEFT JOIN dm_nganh_dao_tao ng ON ng.id = c.nganh_dao_tao_id
    LEFT JOIN dm_nhom_nganh_dao_tao nh ON nh.ma_nhom_nganh = ng.ma_nhom_nganh
    SET r.diem_nganh = CASE
      WHEN ng.id IS NULL THEN NULL
      WHEN EXISTS (SELECT 1 FROM hs_tieu_chi_mong_muon w
                   WHERE w.ho_so_id = p_ho_so_id
                     AND ((w.loai = 'NGANH' AND w.gia_tri = ng.ma_nganh)
                       OR (w.loai = 'NHOM_NGANH' AND w.gia_tri = ng.ma_nhom_nganh)
                       OR (w.loai = 'LINH_VUC' AND w.gia_tri = nh.ma_linh_vuc))) THEN 100
      WHEN EXISTS (SELECT 1 FROM hs_tieu_chi_mong_muon w
                   JOIN dm_nganh_dao_tao ng2 ON ng2.ma_nganh = w.gia_tri
                   WHERE w.ho_so_id = p_ho_so_id AND w.loai = 'NGANH'
                     AND ng2.ma_nhom_nganh = ng.ma_nhom_nganh) THEN 60
      ELSE 0 END
    WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;
  END IF;

  -- Tiêu chí 3: học phí so với ngân sách. Trong ngân sách = 100; vượt 50% trở lên = 0
  SELECT ngan_sach_hoc_phi_nam INTO v_ngan_sach FROM hs_ho_so WHERE id = p_ho_so_id;
  IF v_ngan_sach IS NOT NULL AND v_ngan_sach > 0 THEN
    UPDATE xt_ket_qua_chuong_trinh r
    JOIN (SELECT de_an_chuong_trinh_id, MIN(hoc_phi_tu) AS hoc_phi
          FROM dats_hoc_phi GROUP BY de_an_chuong_trinh_id) hp
      ON hp.de_an_chuong_trinh_id = r.de_an_chuong_trinh_id
    SET r.diem_hoc_phi = CASE WHEN hp.hoc_phi <= v_ngan_sach THEN 100
                              ELSE GREATEST(0, ROUND(100 - (hp.hoc_phi - v_ngan_sach) / v_ngan_sach * 200, 2)) END
    WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;
  END IF;

  -- Tiêu chí 4: vị trí. Tỉnh của cơ sở đào tạo (dats_tru_so), nếu chưa gắn thì lấy tỉnh trụ sở chính của trường
  SELECT COUNT(*) INTO v_co_vi_tri FROM hs_tieu_chi_mong_muon
  WHERE ho_so_id = p_ho_so_id AND loai IN ('TINH_THANH', 'VUNG_MIEN');
  IF v_co_vi_tri > 0 THEN
    UPDATE xt_ket_qua_chuong_trinh r
    JOIN dats_chuong_trinh_dao_tao c ON c.id = r.de_an_chuong_trinh_id
    JOIN dm_truong t ON t.ma_truong = r.ma_truong
    LEFT JOIN dats_tru_so ts ON ts.id = c.co_so_id
    LEFT JOIN dm_tinh_thanh t1 ON t1.id = ts.tinh_thanh_id
    LEFT JOIN dm_tinh_thanh t2 ON t2.ten_tinh = t.ten_tinh_thanh
    SET r.diem_vi_tri = CASE
      WHEN COALESCE(t1.id, t2.id) IS NULL THEN NULL
      WHEN EXISTS (SELECT 1 FROM hs_tieu_chi_mong_muon w
                   WHERE w.ho_so_id = p_ho_so_id AND w.loai = 'TINH_THANH'
                     AND w.gia_tri = COALESCE(t1.ma_tinh, t2.ma_tinh)) THEN 100
      WHEN EXISTS (SELECT 1 FROM hs_tieu_chi_mong_muon w
                   WHERE w.ho_so_id = p_ho_so_id AND w.loai = 'VUNG_MIEN'
                     AND w.gia_tri = COALESCE(t1.khu_vuc, t2.khu_vuc)) THEN 70
      ELSE 20 END
    WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;
  END IF;

  -- Điểm phù hợp = trung bình có trọng số của các tiêu chí CÓ dữ liệu.
  -- Ngành, học phí, vị trí thiếu dữ liệu thì bỏ khỏi mẫu số (coi như học sinh không đặt yêu cầu).
  -- Riêng khả năng trúng tuyển là tiêu chí nền: chưa có điểm chuẩn tham chiếu thì KHÔNG chấm điểm phù hợp.
  SELECT COALESCE(MAX(IF(ma_tieu_chi = 'KHA_NANG_TRUNG_TUYEN', trong_so, NULL)), 0),
         COALESCE(MAX(IF(ma_tieu_chi = 'NGANH', trong_so, NULL)), 0),
         COALESCE(MAX(IF(ma_tieu_chi = 'HOC_PHI', trong_so, NULL)), 0),
         COALESCE(MAX(IF(ma_tieu_chi = 'VI_TRI', trong_so, NULL)), 0)
    INTO v_w_kn, v_w_ng, v_w_hp, v_w_vt
  FROM xt_tieu_chi_phu_hop WHERE bo_tieu_chi_id = v_bo;

  UPDATE xt_ket_qua_chuong_trinh r
  SET r.diem_phu_hop = CASE WHEN r.diem_kha_nang IS NULL THEN NULL ELSE ROUND(
        (r.diem_kha_nang * v_w_kn + COALESCE(r.diem_nganh * v_w_ng, 0)
         + COALESCE(r.diem_hoc_phi * v_w_hp, 0) + COALESCE(r.diem_vi_tri * v_w_vt, 0))
        / NULLIF(v_w_kn + IF(r.diem_nganh IS NULL, 0, v_w_ng)
                 + IF(r.diem_hoc_phi IS NULL, 0, v_w_hp) + IF(r.diem_vi_tri IS NULL, 0, v_w_vt), 0), 2) END
  WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;

  UPDATE xt_ket_qua_chuong_trinh r
  LEFT JOIN xt_muc_phu_hop m
    ON m.bo_tieu_chi_id = v_bo AND m.loai_muc = 'TONG_HOP'
   AND (m.gia_tri_tu IS NULL OR r.diem_phu_hop >= m.gia_tri_tu)
   AND (m.gia_tri_den IS NULL OR r.diem_phu_hop < m.gia_tri_den)
   AND r.diem_phu_hop IS NOT NULL
  SET r.xep_loai = COALESCE(m.nhan, 'Chưa có điểm chuẩn tham chiếu')
  WHERE r.lan_danh_gia_id = p_lan_danh_gia_id;

  -- Thứ hạng: có điểm phù hợp xếp trước; cùng điểm thì chênh lệch điểm lớn hơn xếp trước;
  -- chương trình chưa chấm được xếp sau, theo điểm xét quy về cùng tỷ lệ thang.
  SET @xt_thu_hang := 0;
  UPDATE xt_ket_qua_chuong_trinh
  SET thu_hang = (@xt_thu_hang := @xt_thu_hang + 1)
  WHERE lan_danh_gia_id = p_lan_danh_gia_id
  ORDER BY (diem_phu_hop IS NULL), diem_phu_hop DESC, chenh_lech_30 DESC, diem_xet / thang_diem DESC, id;
END $$

DELIMITER ;

-- ---------------------------------------------------------------------
-- Đánh giá theo TRƯỜNG cho một lần đánh giá.
-- diem_truong = trung bình điểm phù hợp của tối đa 3 chương trình tốt nhất của trường.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_xt_ket_qua_truong AS
SELECT r.lan_danh_gia_id,
       r.ma_truong,
       COUNT(*) AS so_chuong_trinh_du_dieu_kien,
       SUM(r.diem_phu_hop IS NOT NULL) AS so_chuong_trinh_da_cham,
       SUM(r.diem_phu_hop >= 65) AS so_chuong_trinh_phu_hop,
       MAX(r.diem_phu_hop) AS diem_phu_hop_cao_nhat,
       ROUND(AVG(CASE WHEN (SELECT COUNT(*) FROM xt_ket_qua_chuong_trinh r2
                            WHERE r2.lan_danh_gia_id = r.lan_danh_gia_id AND r2.ma_truong = r.ma_truong
                              AND r2.thu_hang < r.thu_hang) < 3
                      THEN r.diem_phu_hop END), 2) AS diem_truong,
       MIN(r.thu_hang) AS thu_hang_tot_nhat
FROM xt_ket_qua_chuong_trinh r
GROUP BY r.lan_danh_gia_id, r.ma_truong;
