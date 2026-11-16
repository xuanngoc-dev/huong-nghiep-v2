-- =====================================================================
-- 01_schema.sql  -  Lớp dữ liệu "xét tuyển tính toán được"
-- CSDL: huongnghiep (MySQL 5.7.44, utf8mb4_unicode_ci)
--
-- Bổ sung vào schema hiện có (dm_*, dats_*), KHÔNG sửa/xóa bảng cũ, trừ
-- 1 cột thêm vào dats_tru_so (xem cuối file).
--
--   hs_*  : hồ sơ điểm của học sinh (đầu vào truy vấn)
--   xt_*  : quy tắc xét tuyển đã chuẩn hóa từ đề án (công thức, điều kiện,
--           quy đổi, điểm cộng, điểm chuẩn) + kết quả đánh giá
--   dats_hoc_phi : học phí theo chương trình (thuộc đề án)
--
-- Thứ tự chạy: 01_schema -> 02_thu_tuc -> 03_du_lieu_danh_muc
--              -> 04_du_lieu_ftu_bka_2026 -> (05_vi_du_truy_van để thử)
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- A. DANH MỤC BỔ SUNG
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `dm_chi_so_xet_tuyen` (
  `ma_chi_so` varchar(50) NOT NULL COMMENT 'Mã chỉ số, dùng trong hs_chi_so, xt_dieu_kien, xt_diem_cong.',
  `ten_chi_so` varchar(255) NOT NULL COMMENT 'Tên chỉ số.',
  `kieu_khoa` varchar(30) DEFAULT NULL COMMENT 'Ý nghĩa cột khoa: MON_HOC (ma_mon_hoc), BAI_THI (ma_bai_thi), CHUNG_CHI (ma_chung_chi), THANH_TICH (ma_thanh_tich), LOP; NULL nếu chỉ số không cần khóa.',
  `y_nghia_gia_tri` varchar(500) DEFAULT NULL COMMENT 'Cách đọc gia_tri_so.',
  `ghi_chu` text COMMENT 'Ghi chú.',
  PRIMARY KEY (`ma_chi_so`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh mục chỉ số (dữ kiện) của học sinh dùng để kiểm tra điều kiện xét tuyển';

-- ---------------------------------------------------------------------
-- B. HỒ SƠ HỌC SINH
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hs_ho_so` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `nguoi_dung_id` int(11) DEFAULT NULL COMMENT 'Tài khoản sở hữu; NULL nếu khách vãng lai.',
  `ma_thiet_bi` varchar(64) DEFAULT NULL COMMENT 'Mã thiết bị của khách vãng lai.',
  `ten_ho_so` varchar(150) DEFAULT NULL COMMENT 'Tên gợi nhớ (một tài khoản có thể có nhiều hồ sơ giả định).',
  `nam_tot_nghiep` smallint(5) unsigned DEFAULT NULL COMMENT 'Năm tốt nghiệp THPT (thực tế hoặc dự kiến).',
  `da_tot_nghiep` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: đã/đủ điều kiện tốt nghiệp THPT (hoặc tương đương) tại thời điểm xét.',
  `chuong_trinh_thpt` enum('GDPT_2018','GDPT_2006','NUOC_NGOAI') NOT NULL DEFAULT 'GDPT_2018' COMMENT 'Chương trình THPT đã học.',
  `he_chuyen` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1: học hệ chuyên cả 3 năm THPT.',
  `mon_chuyen_id` int(11) DEFAULT NULL COMMENT 'Môn chuyên; FK dm_mon_hoc.id.',
  `ten_truong_thpt` varchar(255) DEFAULT NULL COMMENT 'Trường THPT.',
  `tinh_thanh_id` int(11) DEFAULT NULL COMMENT 'Tỉnh/thành nơi học THPT; FK dm_tinh_thanh.id.',
  `khu_vuc_uu_tien_id` int(11) DEFAULT NULL COMMENT 'Khu vực ưu tiên; FK dm_khu_vuc_uu_tien.id.',
  `doi_tuong_uu_tien_id` int(11) DEFAULT NULL COMMENT 'Đối tượng ưu tiên (mức cao nhất); FK dm_doi_tuong_uu_tien.id.',
  `ngan_sach_hoc_phi_nam` decimal(15,0) DEFAULT NULL COMMENT 'Học phí tối đa gia đình chi trả được mỗi năm (VNĐ).',
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cap_nhat_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_hs_ho_so_nguoi_dung_id` (`nguoi_dung_id`),
  KEY `idx_hs_ho_so_ma_thiet_bi` (`ma_thiet_bi`),
  CONSTRAINT `fk_hs_ho_so_nguoi_dung_id` FOREIGN KEY (`nguoi_dung_id`) REFERENCES `nguoi_dung` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_ho_so_mon_chuyen_id` FOREIGN KEY (`mon_chuyen_id`) REFERENCES `dm_mon_hoc` (`id`),
  CONSTRAINT `fk_hs_ho_so_tinh_thanh_id` FOREIGN KEY (`tinh_thanh_id`) REFERENCES `dm_tinh_thanh` (`id`),
  CONSTRAINT `fk_hs_ho_so_khu_vuc_uu_tien_id` FOREIGN KEY (`khu_vuc_uu_tien_id`) REFERENCES `dm_khu_vuc_uu_tien` (`id`),
  CONSTRAINT `fk_hs_ho_so_doi_tuong_uu_tien_id` FOREIGN KEY (`doi_tuong_uu_tien_id`) REFERENCES `dm_doi_tuong_uu_tien` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Hồ sơ xét tuyển của học sinh';

CREATE TABLE IF NOT EXISTS `hs_ket_qua_nam_hoc` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `lop` tinyint(3) unsigned NOT NULL COMMENT '10, 11 hoặc 12.',
  `diem_tb_chung` decimal(4,2) DEFAULT NULL COMMENT 'Điểm trung bình chung các môn cả năm, thang 10.',
  `hoc_luc` tinyint(3) unsigned DEFAULT NULL COMMENT 'Kết quả học tập cả năm: 4 = Tốt/Giỏi, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu.',
  `ren_luyen` tinyint(3) unsigned DEFAULT NULL COMMENT 'Kết quả rèn luyện/hạnh kiểm cả năm: 4 = Tốt, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_hs_ket_qua_nam_hoc` (`ho_so_id`,`lop`),
  CONSTRAINT `fk_hs_ket_qua_nam_hoc_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kết quả tổng kết từng năm THPT của học sinh';

CREATE TABLE IF NOT EXISTS `hs_diem_mon` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `mon_hoc_id` int(11) NOT NULL COMMENT 'FK dm_mon_hoc.id (ngoại ngữ ghi đúng môn: ANH, PHAP, TRUNG...).',
  `nguon_diem` enum('THI_THPT','HOC_BA') NOT NULL COMMENT 'THI_THPT: điểm thi tốt nghiệp THPT; HOC_BA: điểm tổng kết môn trong học bạ.',
  `lop` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT 'HOC_BA: 10/11/12; THI_THPT: 0.',
  `hoc_ky` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT 'HOC_BA: 0 = cả năm, 1, 2; THI_THPT: 0.',
  `diem` decimal(5,2) NOT NULL COMMENT 'Điểm thang 10.',
  `nam` smallint(5) unsigned DEFAULT NULL COMMENT 'Năm thi/năm học.',
  `la_du_kien` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1: điểm thi thử/ước lượng, chưa chính thức.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_hs_diem_mon` (`ho_so_id`,`nguon_diem`,`mon_hoc_id`,`lop`,`hoc_ky`),
  KEY `idx_hs_diem_mon_mon_hoc_id` (`mon_hoc_id`),
  CONSTRAINT `fk_hs_diem_mon_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_diem_mon_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Điểm từng môn: thi tốt nghiệp THPT và học bạ';

CREATE TABLE IF NOT EXISTS `hs_diem_bai_thi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `bai_thi_id` bigint(20) unsigned NOT NULL COMMENT 'FK dm_bai_thi_danh_gia.id (HSA, V-ACT, TSA, SAT, ACT, V-SAT...).',
  `nam_thi` smallint(5) unsigned NOT NULL COMMENT 'Năm dự thi.',
  `dot_thi` varchar(30) DEFAULT NULL COMMENT 'Đợt thi.',
  `ngay_thi` date DEFAULT NULL,
  `diem` decimal(8,2) NOT NULL COMMENT 'Tổng điểm theo thang gốc của bài thi.',
  `phan_tu_chon` varchar(50) DEFAULT NULL COMMENT 'Phần thi tự chọn nếu có, ví dụ HSA phần 3: KHOA_HOC / TIENG_ANH.',
  `diem_thanh_phan` json DEFAULT NULL COMMENT 'Điểm từng phần thi (để hiển thị).',
  PRIMARY KEY (`id`),
  KEY `idx_hs_diem_bai_thi_ho_so_id` (`ho_so_id`,`bai_thi_id`),
  KEY `idx_hs_diem_bai_thi_bai_thi_id` (`bai_thi_id`),
  CONSTRAINT `fk_hs_diem_bai_thi_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_diem_bai_thi_bai_thi_id` FOREIGN KEY (`bai_thi_id`) REFERENCES `dm_bai_thi_danh_gia` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kết quả các bài thi ĐGNL/ĐGTD/SAT/ACT của học sinh';

CREATE TABLE IF NOT EXISTS `hs_chung_chi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `chung_chi_id` bigint(20) unsigned NOT NULL COMMENT 'FK dm_bang_cap_chung_chi.id (IELTS, TOEFL, JLPT, HSK, DELF, VSTEP...).',
  `diem` decimal(8,2) DEFAULT NULL COMMENT 'Điểm số theo thang của chứng chỉ; NULL nếu chứng chỉ chỉ có cấp độ.',
  `cap_do` varchar(30) DEFAULT NULL COMMENT 'Cấp độ nếu chứng chỉ chia cấp: N3, N2, HSK4, B1, B2, C1...',
  `ngay_cap` date DEFAULT NULL,
  `ngay_het_han` date DEFAULT NULL COMMENT 'NULL: không thời hạn/chưa biết.',
  `diem_thanh_phan` json DEFAULT NULL COMMENT 'Điểm kỹ năng/điểm môn thành phần (để hiển thị).',
  PRIMARY KEY (`id`),
  KEY `idx_hs_chung_chi_ho_so_id` (`ho_so_id`,`chung_chi_id`),
  KEY `idx_hs_chung_chi_chung_chi_id` (`chung_chi_id`),
  CONSTRAINT `fk_hs_chung_chi_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_chung_chi_chung_chi_id` FOREIGN KEY (`chung_chi_id`) REFERENCES `dm_bang_cap_chung_chi` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chứng chỉ ngoại ngữ/quốc tế của học sinh';

CREATE TABLE IF NOT EXISTS `hs_thanh_tich` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `thanh_tich_id` int(11) NOT NULL COMMENT 'FK dm_thanh_tich_hoc_tap_nghien_cuu.id (HSG-QG, HSG-TINH, NCKH-QG...).',
  `mon_hoc_id` int(11) DEFAULT NULL COMMENT 'Môn đạt giải; FK dm_mon_hoc.id.',
  `linh_vuc` varchar(150) DEFAULT NULL COMMENT 'Lĩnh vực đề tài (KHKT) nếu không gắn với môn học.',
  `muc_giai` tinyint(3) unsigned NOT NULL COMMENT '1 = Nhất/Vàng, 2 = Nhì/Bạc, 3 = Ba/Đồng, 4 = Khuyến khích/Tư, 9 = tham gia, không đạt giải.',
  `nam_dat_giai` smallint(5) unsigned DEFAULT NULL,
  `lop` tinyint(3) unsigned DEFAULT NULL COMMENT 'Lớp khi đạt giải.',
  PRIMARY KEY (`id`),
  KEY `idx_hs_thanh_tich_ho_so_id` (`ho_so_id`,`thanh_tich_id`),
  KEY `idx_hs_thanh_tich_thanh_tich_id` (`thanh_tich_id`),
  CONSTRAINT `fk_hs_thanh_tich_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_thanh_tich_thanh_tich_id` FOREIGN KEY (`thanh_tich_id`) REFERENCES `dm_thanh_tich_hoc_tap_nghien_cuu` (`id`),
  CONSTRAINT `fk_hs_thanh_tich_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Giải thưởng, thành tích của học sinh';

CREATE TABLE IF NOT EXISTS `hs_tieu_chi_mong_muon` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `loai` enum('NGANH','NHOM_NGANH','LINH_VUC','TINH_THANH','VUNG_MIEN','LOAI_HINH_TRUONG') NOT NULL COMMENT 'Loại mong muốn.',
  `gia_tri` varchar(100) NOT NULL COMMENT 'NGANH: ma_nganh; NHOM_NGANH: ma_nhom_nganh; LINH_VUC: ma_linh_vuc; TINH_THANH: dm_tinh_thanh.ma_tinh; VUNG_MIEN: Bắc/Trung/Nam; LOAI_HINH_TRUONG: dm_truong.loai_hinh.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_hs_tieu_chi_mong_muon` (`ho_so_id`,`loai`,`gia_tri`),
  CONSTRAINT `fk_hs_tieu_chi_mong_muon_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Ngành, địa điểm, loại trường học sinh mong muốn (dùng để lọc và chấm điểm phù hợp)';

CREATE TABLE IF NOT EXISTS `hs_chi_so` (
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `ma_chi_so` varchar(50) NOT NULL COMMENT 'FK dm_chi_so_xet_tuyen.ma_chi_so.',
  `khoa` varchar(50) NOT NULL DEFAULT '' COMMENT 'Khóa phụ theo dm_chi_so_xet_tuyen.kieu_khoa; rỗng nếu không cần.',
  `gia_tri_so` decimal(12,3) DEFAULT NULL,
  PRIMARY KEY (`ho_so_id`,`ma_chi_so`,`khoa`),
  KEY `idx_hs_chi_so_ma_chi_so` (`ma_chi_so`,`khoa`),
  CONSTRAINT `fk_hs_chi_so_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_hs_chi_so_ma_chi_so` FOREIGN KEY (`ma_chi_so`) REFERENCES `dm_chi_so_xet_tuyen` (`ma_chi_so`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng DẪN XUẤT: dữ kiện phẳng của học sinh, sinh từ các bảng hs_* bởi sp_hs_cap_nhat_chi_so; dùng để so điều kiện';

-- ---------------------------------------------------------------------
-- C. QUY TẮC XÉT TUYỂN (chuẩn hóa từ đề án)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `xt_bang_quy_doi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL COMMENT 'Đề án ban hành bảng quy đổi.',
  `ma_bang` varchar(50) NOT NULL COMMENT 'Mã bảng trong đề án.',
  `ten_bang` varchar(255) NOT NULL,
  `thang_diem_dich` decimal(6,2) NOT NULL COMMENT 'Thang điểm sau quy đổi (10, 20, 30...).',
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_bang_quy_doi` (`de_an_id`,`ma_bang`),
  CONSTRAINT `fk_xt_bang_quy_doi_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng quy đổi chứng chỉ/bài thi sang điểm xét';

CREATE TABLE IF NOT EXISTS `xt_bang_quy_doi_chi_tiet` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bang_quy_doi_id` bigint(20) unsigned NOT NULL,
  `chung_chi_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Chứng chỉ nguồn; FK dm_bang_cap_chung_chi.id.',
  `bai_thi_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Bài thi nguồn; FK dm_bai_thi_danh_gia.id. Mỗi dòng chỉ điền chung_chi_id HOẶC bai_thi_id.',
  `mon_hoc_id` int(11) DEFAULT NULL COMMENT 'Môn ngoại ngữ mà chứng chỉ thay thế (IELTS -> ANH, HSK -> TRUNG...).',
  `cap_do` varchar(30) DEFAULT NULL COMMENT 'Cấp độ phải khớp (N3, HSK4, B2...); NULL nếu không xét cấp độ.',
  `diem_tu` decimal(8,2) DEFAULT NULL COMMENT 'Cận dưới (>=); NULL nếu không giới hạn.',
  `diem_den` decimal(8,2) DEFAULT NULL COMMENT 'Cận trên (<=); NULL nếu không giới hạn.',
  `diem_quy_doi` decimal(7,3) NOT NULL COMMENT 'Điểm quy đổi tại diem_tu.',
  `he_so_noi_suy` decimal(12,8) NOT NULL DEFAULT '0.00000000' COMMENT 'Điểm quy đổi = diem_quy_doi + he_so_noi_suy * (điểm - diem_tu). 0 = bảng bậc thang.',
  `dat_nguong` tinyint(1) NOT NULL DEFAULT '1' COMMENT '0: mức có trong bảng nhưng dưới ngưỡng bảo đảm chất lượng, không dùng để xét.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_bang_quy_doi_chi_tiet_bang` (`bang_quy_doi_id`,`chung_chi_id`),
  KEY `idx_xt_bang_quy_doi_chi_tiet_bai_thi` (`bang_quy_doi_id`,`bai_thi_id`),
  CONSTRAINT `fk_xt_bqd_ct_bang_quy_doi_id` FOREIGN KEY (`bang_quy_doi_id`) REFERENCES `xt_bang_quy_doi` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_bqd_ct_chung_chi_id` FOREIGN KEY (`chung_chi_id`) REFERENCES `dm_bang_cap_chung_chi` (`id`),
  CONSTRAINT `fk_xt_bqd_ct_bai_thi_id` FOREIGN KEY (`bai_thi_id`) REFERENCES `dm_bai_thi_danh_gia` (`id`),
  CONSTRAINT `fk_xt_bqd_ct_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Các mức của bảng quy đổi (bậc thang hoặc nội suy tuyến tính)';

CREATE TABLE IF NOT EXISTS `xt_cong_thuc` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL COMMENT 'Đề án quy định công thức.',
  `ma_cong_thuc` varchar(50) NOT NULL COMMENT 'Mã công thức trong đề án.',
  `ten_cong_thuc` varchar(255) NOT NULL,
  `ma_phuong_thuc_cua_bo` varchar(20) NOT NULL COMMENT 'FK dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc.',
  `kieu_tinh` enum('TO_HOP_MON','THANH_PHAN','CHI_DIEU_KIEN','THU_CONG') NOT NULL COMMENT 'TO_HOP_MON: tổng có hệ số các môn của tổ hợp; THANH_PHAN: tổng các thành phần bài thi/chứng chỉ quy đổi; CHI_DIEU_KIEN: không tính điểm, chỉ xét điều kiện (xét tuyển thẳng); THU_CONG: có điểm nhưng hệ thống chưa tự tính (hồ sơ năng lực, phỏng vấn...).',
  `nguon_diem_mon` enum('THI_THPT','HOC_BA') DEFAULT NULL COMMENT 'TO_HOP_MON: nguồn điểm môn. HOC_BA = trung bình cả năm lớp 10, 11, 12.',
  `thay_ngoai_ngu` enum('KHONG','DUOC_PHEP','BAT_BUOC') NOT NULL DEFAULT 'KHONG' COMMENT 'TO_HOP_MON: môn ngoại ngữ trong tổ hợp có lấy điểm quy đổi chứng chỉ không. DUOC_PHEP: lấy mức cao hơn; BAT_BUOC: chỉ dùng chứng chỉ.',
  `bang_quy_doi_ngoai_ngu_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Bảng quy đổi chứng chỉ ngoại ngữ -> điểm môn (thang 10).',
  `thang_diem` decimal(6,2) NOT NULL DEFAULT '30.00' COMMENT 'Điểm tối đa của điểm xét.',
  `he_so_nhan` decimal(12,8) NOT NULL DEFAULT '1.00000000' COMMENT 'Nhân vào tổng các thành phần (ví dụ 0,5 hoặc 4/3).',
  `nguong_tb_mon` decimal(4,2) DEFAULT NULL COMMENT 'TO_HOP_MON: trung bình cộng điểm các môn học dùng để xét (không tính môn thay bằng chứng chỉ) phải >= giá trị này.',
  `nguong_thpt_to_hop` decimal(5,2) DEFAULT NULL COMMENT 'TO_HOP_MON: tổng điểm thi THPT 3 môn của chính tổ hợp đó (môn ngoại ngữ được thay bằng chứng chỉ nếu công thức cho phép) + điểm ưu tiên phải >= giá trị này.',
  `diem_san` decimal(7,2) DEFAULT NULL COMMENT 'Ngưỡng nhận hồ sơ tính trên điểm xét cuối cùng.',
  `ap_dung_diem_cong` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: có cộng điểm thưởng/xét thưởng/khuyến khích (xt_diem_cong).',
  `ap_dung_uu_tien` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: có cộng điểm ưu tiên khu vực, đối tượng theo Điều 7 Quy chế.',
  `ty_le_diem_cong_toi_da` decimal(4,3) NOT NULL DEFAULT '0.100' COMMENT 'Trần tổng điểm cộng so với thang điểm (Quy chế: 10%).',
  `so_le_lam_tron` tinyint(3) unsigned NOT NULL DEFAULT '2',
  `mo_ta_cong_thuc` text COMMENT 'Công thức nguyên văn để hiển thị/đối chiếu.',
  `trang_thai` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: dùng để tính; 0: chưa dùng (chờ xác minh).',
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_cong_thuc` (`de_an_id`,`ma_cong_thuc`),
  KEY `idx_xt_cong_thuc_ma_phuong_thuc` (`ma_phuong_thuc_cua_bo`),
  CONSTRAINT `fk_xt_cong_thuc_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`),
  CONSTRAINT `fk_xt_cong_thuc_ma_phuong_thuc` FOREIGN KEY (`ma_phuong_thuc_cua_bo`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`ma_phuong_thuc`),
  CONSTRAINT `fk_xt_cong_thuc_bang_quy_doi` FOREIGN KEY (`bang_quy_doi_ngoai_ngu_id`) REFERENCES `xt_bang_quy_doi` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Công thức tính điểm xét tuyển (một "họ" cách tính của đề án)';

CREATE TABLE IF NOT EXISTS `xt_cong_thuc_he_so_mon` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `cong_thuc_id` bigint(20) unsigned NOT NULL,
  `mon_hoc_id` int(11) DEFAULT NULL COMMENT 'Môn được nhân hệ số; NULL nếu áp theo nhóm môn.',
  `nhom_mon` varchar(50) DEFAULT NULL COMMENT 'Áp cho mọi môn có dm_mon_hoc.nhom_mon này (ví dụ: Ngoại ngữ). Hệ số theo môn được ưu tiên hơn theo nhóm.',
  `he_so` decimal(6,3) NOT NULL COMMENT 'Môn không khai báo mặc định hệ số 1.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_cong_thuc_he_so_mon` (`cong_thuc_id`,`mon_hoc_id`),
  CONSTRAINT `fk_xt_cthsm_cong_thuc_id` FOREIGN KEY (`cong_thuc_id`) REFERENCES `xt_cong_thuc` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_cthsm_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Hệ số môn của công thức kiểu TO_HOP_MON';

CREATE TABLE IF NOT EXISTS `xt_cong_thuc_thanh_phan` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `cong_thuc_id` bigint(20) unsigned NOT NULL,
  `vi_tri` tinyint(3) unsigned NOT NULL COMMENT 'Thứ tự thành phần (M1, M2...). Các dòng cùng vi_tri là phương án thay thế nhau, lấy giá trị cao nhất.',
  `ten_thanh_phan` varchar(255) DEFAULT NULL,
  `loai_nguon` enum('BAI_THI','CHUNG_CHI') NOT NULL COMMENT 'BAI_THI: điểm hs_diem_bai_thi; CHUNG_CHI: điểm quy đổi của bất kỳ chứng chỉ nào có trong bảng quy đổi.',
  `bai_thi_id` bigint(20) unsigned DEFAULT NULL COMMENT 'BAI_THI: bài thi sử dụng.',
  `bang_quy_doi_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Bảng quy đổi; NULL (chỉ với BAI_THI) = dùng điểm gốc.',
  `mon_hoc_id` int(11) DEFAULT NULL COMMENT 'CHUNG_CHI: chỉ nhận chứng chỉ của ngoại ngữ này; NULL = mọi ngoại ngữ trong bảng.',
  `he_so` decimal(6,3) NOT NULL DEFAULT '1.000',
  `nam_thi_tu` smallint(5) unsigned DEFAULT NULL COMMENT 'BAI_THI: chỉ nhận kết quả từ năm này.',
  `nam_thi_den` smallint(5) unsigned DEFAULT NULL COMMENT 'BAI_THI: chỉ nhận kết quả đến năm này.',
  `yeu_cau_phan_tu_chon` varchar(50) DEFAULT NULL COMMENT 'BAI_THI: bắt buộc hs_diem_bai_thi.phan_tu_chon bằng giá trị này.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_cong_thuc_thanh_phan` (`cong_thuc_id`,`vi_tri`),
  CONSTRAINT `fk_xt_cttp_cong_thuc_id` FOREIGN KEY (`cong_thuc_id`) REFERENCES `xt_cong_thuc` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_cttp_bai_thi_id` FOREIGN KEY (`bai_thi_id`) REFERENCES `dm_bai_thi_danh_gia` (`id`),
  CONSTRAINT `fk_xt_cttp_bang_quy_doi_id` FOREIGN KEY (`bang_quy_doi_id`) REFERENCES `xt_bang_quy_doi` (`id`),
  CONSTRAINT `fk_xt_cttp_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Thành phần điểm của công thức kiểu THANH_PHAN';

CREATE TABLE IF NOT EXISTS `xt_phuong_an` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL COMMENT 'Đề án (lặp lại để lọc nhanh theo năm).',
  `de_an_chuong_trinh_id` bigint(20) unsigned NOT NULL COMMENT 'Chương trình; FK dats_chuong_trinh_dao_tao.id.',
  `de_an_phuong_thuc_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Dòng mô tả phương thức tương ứng; FK dats_phuong_thuc.id.',
  `cong_thuc_id` bigint(20) unsigned NOT NULL COMMENT 'Cách tính điểm.',
  `to_hop_id` int(11) DEFAULT NULL COMMENT 'Tổ hợp môn (bắt buộc với công thức TO_HOP_MON).',
  `trang_thai` tinyint(1) NOT NULL DEFAULT '1',
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_phuong_an` (`de_an_chuong_trinh_id`,`cong_thuc_id`,`to_hop_id`),
  KEY `idx_xt_phuong_an_de_an_id` (`de_an_id`),
  KEY `idx_xt_phuong_an_cong_thuc_id` (`cong_thuc_id`),
  KEY `idx_xt_phuong_an_to_hop_id` (`to_hop_id`),
  KEY `idx_xt_phuong_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  CONSTRAINT `fk_xt_phuong_an_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`),
  CONSTRAINT `fk_xt_phuong_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`),
  CONSTRAINT `fk_xt_phuong_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`),
  CONSTRAINT `fk_xt_phuong_an_cong_thuc_id` FOREIGN KEY (`cong_thuc_id`) REFERENCES `xt_cong_thuc` (`id`),
  CONSTRAINT `fk_xt_phuong_an_to_hop_id` FOREIGN KEY (`to_hop_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phương án xét tuyển: một cách cụ thể để vào một chương trình = chương trình x công thức x tổ hợp';

CREATE TABLE IF NOT EXISTS `xt_nhom_dieu_kien` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL,
  `cong_thuc_id` bigint(20) unsigned DEFAULT NULL COMMENT 'NULL = áp dụng cho mọi công thức của đề án.',
  `de_an_chuong_trinh_id` bigint(20) unsigned DEFAULT NULL COMMENT 'NULL = áp dụng cho mọi chương trình.',
  `ma_nhom` varchar(50) NOT NULL,
  `ten_nhom` varchar(255) NOT NULL COMMENT 'Tên ngắn, dùng làm lý do khi không đạt.',
  `mo_ta` text COMMENT 'Nguyên văn điều kiện trong đề án.',
  `bat_buoc` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1: không đạt thì loại; 0: chỉ để cảnh báo.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_nhom_dieu_kien_de_an` (`de_an_id`,`cong_thuc_id`,`de_an_chuong_trinh_id`),
  CONSTRAINT `fk_xt_ndk_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`),
  CONSTRAINT `fk_xt_ndk_cong_thuc_id` FOREIGN KEY (`cong_thuc_id`) REFERENCES `xt_cong_thuc` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_ndk_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Nhóm điều kiện dự tuyển. Các nhóm áp dụng cho một phương án phải CÙNG đạt (AND)';

CREATE TABLE IF NOT EXISTS `xt_dieu_kien` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `nhom_dieu_kien_id` bigint(20) unsigned NOT NULL,
  `ma_chi_so` varchar(50) NOT NULL COMMENT 'FK dm_chi_so_xet_tuyen.ma_chi_so.',
  `khoa` varchar(50) NOT NULL DEFAULT '',
  `toan_tu` enum('>=','>','=','<=','<','!=') NOT NULL,
  `gia_tri_so` decimal(12,3) NOT NULL,
  `mo_ta` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_xt_dieu_kien_nhom` (`nhom_dieu_kien_id`),
  KEY `idx_xt_dieu_kien_chi_so` (`ma_chi_so`,`khoa`),
  CONSTRAINT `fk_xt_dk_nhom_dieu_kien_id` FOREIGN KEY (`nhom_dieu_kien_id`) REFERENCES `xt_nhom_dieu_kien` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_dk_ma_chi_so` FOREIGN KEY (`ma_chi_so`) REFERENCES `dm_chi_so_xet_tuyen` (`ma_chi_so`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Điều kiện đơn. Trong một nhóm chỉ cần MỘT điều kiện đạt (OR). Học sinh không có chỉ số = không đạt';

CREATE TABLE IF NOT EXISTS `xt_diem_cong` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL,
  `cong_thuc_id` bigint(20) unsigned DEFAULT NULL COMMENT 'NULL = mọi công thức của đề án có ap_dung_diem_cong = 1.',
  `loai_diem_cong` enum('DIEM_THUONG','DIEM_XET_THUONG','DIEM_KHUYEN_KHICH') NOT NULL COMMENT 'Theo khoản 20 Điều 2 Quy chế.',
  `nhom_cong` varchar(50) NOT NULL COMMENT 'Trong cùng nhóm chỉ lấy mức cao nhất; các nhóm khác nhau cộng dồn.',
  `ma_chi_so` varchar(50) NOT NULL,
  `khoa` varchar(50) NOT NULL DEFAULT '',
  `toan_tu` enum('>=','>','=','<=','<','!=') NOT NULL,
  `gia_tri_so` decimal(12,3) NOT NULL,
  `diem_cong` decimal(5,2) NOT NULL COMMENT 'Mức cộng tính trên thang 30; tự quy đổi theo thang_diem của công thức.',
  `mo_ta` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_xt_diem_cong_de_an` (`de_an_id`,`cong_thuc_id`),
  CONSTRAINT `fk_xt_diem_cong_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`),
  CONSTRAINT `fk_xt_diem_cong_cong_thuc_id` FOREIGN KEY (`cong_thuc_id`) REFERENCES `xt_cong_thuc` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_diem_cong_ma_chi_so` FOREIGN KEY (`ma_chi_so`) REFERENCES `dm_chi_so_xet_tuyen` (`ma_chi_so`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Quy tắc điểm cộng (thưởng, xét thưởng, khuyến khích) có cấu trúc';

CREATE TABLE IF NOT EXISTS `xt_diem_chuan` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ma_truong` varchar(20) NOT NULL COMMENT 'FK dm_truong.ma_truong.',
  `nam_tuyen_sinh` smallint(5) unsigned NOT NULL,
  `ma_xet_tuyen` varchar(20) NOT NULL COMMENT 'Mã xét tuyển năm đó; dùng để nối với chương trình của đề án hiện hành.',
  `ten_chuong_trinh` varchar(255) DEFAULT NULL,
  `ma_phuong_thuc_cua_bo` varchar(20) DEFAULT NULL COMMENT 'NULL = điểm chuẩn chung mọi phương thức.',
  `to_hop_id` int(11) DEFAULT NULL COMMENT 'NULL = chung mọi tổ hợp.',
  `diem_chuan` decimal(7,2) NOT NULL,
  `thang_diem` decimal(6,2) NOT NULL DEFAULT '30.00',
  `tieu_chi_phu` varchar(255) DEFAULT NULL,
  `nguon_du_lieu_url` varchar(1000) DEFAULT NULL,
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  KEY `idx_xt_diem_chuan_tra_cuu` (`ma_truong`,`ma_xet_tuyen`,`nam_tuyen_sinh`),
  KEY `idx_xt_diem_chuan_to_hop_id` (`to_hop_id`),
  KEY `idx_xt_diem_chuan_ma_phuong_thuc` (`ma_phuong_thuc_cua_bo`),
  CONSTRAINT `fk_xt_diem_chuan_ma_truong` FOREIGN KEY (`ma_truong`) REFERENCES `dm_truong` (`ma_truong`) ON UPDATE CASCADE,
  CONSTRAINT `fk_xt_diem_chuan_ma_phuong_thuc` FOREIGN KEY (`ma_phuong_thuc_cua_bo`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`ma_phuong_thuc`),
  CONSTRAINT `fk_xt_diem_chuan_to_hop_id` FOREIGN KEY (`to_hop_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Điểm trúng tuyển các năm, làm mốc so sánh';

CREATE TABLE IF NOT EXISTS `dats_hoc_phi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `de_an_id` bigint(20) unsigned NOT NULL,
  `de_an_chuong_trinh_id` bigint(20) unsigned NOT NULL,
  `nam_hoc` varchar(20) DEFAULT NULL COMMENT 'Ví dụ 2026-2027.',
  `hoc_phi_tu` decimal(15,0) NOT NULL COMMENT 'VNĐ/năm, mức thấp.',
  `hoc_phi_den` decimal(15,0) DEFAULT NULL COMMENT 'VNĐ/năm, mức cao.',
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  KEY `idx_dats_hoc_phi_chuong_trinh` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_hoc_phi_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_hoc_phi_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`),
  CONSTRAINT `fk_dats_hoc_phi_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Học phí dự kiến theo chương trình';

-- ---------------------------------------------------------------------
-- D. CHẤM ĐIỂM PHÙ HỢP VÀ KẾT QUẢ
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `xt_bo_tieu_chi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ma_bo` varchar(50) NOT NULL,
  `ten_bo` varchar(255) NOT NULL,
  `mac_dinh` tinyint(1) NOT NULL DEFAULT '0',
  `ghi_chu` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_bo_tieu_chi_ma_bo` (`ma_bo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bộ tiêu chí chấm điểm mức độ phù hợp (có thể có nhiều phiên bản)';

CREATE TABLE IF NOT EXISTS `xt_tieu_chi_phu_hop` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bo_tieu_chi_id` bigint(20) unsigned NOT NULL,
  `ma_tieu_chi` enum('KHA_NANG_TRUNG_TUYEN','NGANH','HOC_PHI','VI_TRI') NOT NULL,
  `trong_so` decimal(5,2) NOT NULL COMMENT 'Trọng số tương đối; tiêu chí thiếu dữ liệu bị loại khỏi mẫu số.',
  `mo_ta` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_tieu_chi_phu_hop` (`bo_tieu_chi_id`,`ma_tieu_chi`),
  CONSTRAINT `fk_xt_tcph_bo_tieu_chi_id` FOREIGN KEY (`bo_tieu_chi_id`) REFERENCES `xt_bo_tieu_chi` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Trọng số từng tiêu chí phù hợp';

CREATE TABLE IF NOT EXISTS `xt_muc_phu_hop` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bo_tieu_chi_id` bigint(20) unsigned NOT NULL,
  `loai_muc` enum('KHA_NANG_TRUNG_TUYEN','TONG_HOP') NOT NULL COMMENT 'KHA_NANG_TRUNG_TUYEN: quy chênh lệch điểm (thang 30) thành điểm 0-100; TONG_HOP: xếp loại theo điểm phù hợp.',
  `gia_tri_tu` decimal(7,2) DEFAULT NULL COMMENT 'Cận dưới (>=); NULL = âm vô cùng.',
  `gia_tri_den` decimal(7,2) DEFAULT NULL COMMENT 'Cận trên (<); NULL = dương vô cùng.',
  `diem` decimal(5,2) DEFAULT NULL COMMENT 'Điểm 0-100 (với KHA_NANG_TRUNG_TUYEN).',
  `nhan` varchar(50) NOT NULL COMMENT 'Nhãn hiển thị.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_muc_phu_hop` (`bo_tieu_chi_id`,`loai_muc`),
  CONSTRAINT `fk_xt_mph_bo_tieu_chi_id` FOREIGN KEY (`bo_tieu_chi_id`) REFERENCES `xt_bo_tieu_chi` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Các mốc quy đổi thành điểm/nhãn phù hợp';

CREATE TABLE IF NOT EXISTS `xt_lan_danh_gia` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ho_so_id` bigint(20) unsigned NOT NULL,
  `nam_tuyen_sinh` smallint(5) unsigned NOT NULL COMMENT 'Năm của các đề án được dùng để đánh giá.',
  `bo_tieu_chi_id` bigint(20) unsigned NOT NULL,
  `lich_su_tim_truong_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Liên kết tn_lich_su_tim_truong_phu_hop.id nếu chạy từ một lượt tìm trường.',
  `tao_luc` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_xt_lan_danh_gia_ho_so` (`ho_so_id`,`tao_luc`),
  KEY `idx_xt_lan_danh_gia_lich_su` (`lich_su_tim_truong_id`),
  CONSTRAINT `fk_xt_ldg_ho_so_id` FOREIGN KEY (`ho_so_id`) REFERENCES `hs_ho_so` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_ldg_bo_tieu_chi_id` FOREIGN KEY (`bo_tieu_chi_id`) REFERENCES `xt_bo_tieu_chi` (`id`),
  CONSTRAINT `fk_xt_ldg_lich_su_id` FOREIGN KEY (`lich_su_tim_truong_id`) REFERENCES `tn_lich_su_tim_truong_phu_hop` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mỗi lần chạy đánh giá cho một hồ sơ';

CREATE TABLE IF NOT EXISTS `xt_ket_qua_phuong_an` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `lan_danh_gia_id` bigint(20) unsigned NOT NULL,
  `phuong_an_id` bigint(20) unsigned NOT NULL,
  `de_an_chuong_trinh_id` bigint(20) unsigned NOT NULL,
  `cong_thuc_id` bigint(20) unsigned NOT NULL,
  `to_hop_id` int(11) DEFAULT NULL,
  `kieu_tinh` varchar(20) NOT NULL,
  `thang_diem` decimal(6,2) NOT NULL,
  `diem_goc` decimal(9,4) DEFAULT NULL COMMENT 'Điểm theo công thức, chưa cộng.',
  `tb_mon` decimal(6,3) DEFAULT NULL COMMENT 'Trung bình các môn học dùng xét (so với nguong_tb_mon).',
  `tong_thpt_to_hop` decimal(6,2) DEFAULT NULL COMMENT 'Tổng điểm thi THPT theo tổ hợp, chưa gồm ưu tiên (so với nguong_thpt_to_hop).',
  `diem_cong` decimal(6,2) NOT NULL DEFAULT '0.00' COMMENT 'Điểm cộng đã quy về thang của công thức.',
  `diem_uu_tien` decimal(6,2) NOT NULL DEFAULT '0.00' COMMENT 'Điểm ưu tiên đã quy về thang của công thức.',
  `diem_xet` decimal(7,2) DEFAULT NULL COMMENT 'Điểm xét tuyển cuối cùng.',
  `dat_nguong` tinyint(1) DEFAULT NULL COMMENT '1: đạt mọi ngưỡng điểm của công thức.',
  `so_nhom_dieu_kien` smallint(5) unsigned NOT NULL DEFAULT '0',
  `so_nhom_dat` smallint(5) unsigned NOT NULL DEFAULT '0',
  `du_dieu_kien` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1: đạt mọi điều kiện và ngưỡng.',
  `ly_do_khong_dat` varchar(1000) DEFAULT NULL,
  `diem_chuan_id` bigint(20) unsigned DEFAULT NULL COMMENT 'Dòng xt_diem_chuan dùng làm mốc.',
  `diem_chuan_tham_chieu` decimal(7,2) DEFAULT NULL,
  `nam_diem_chuan` smallint(5) unsigned DEFAULT NULL,
  `chenh_lech_30` decimal(6,2) DEFAULT NULL COMMENT '(điểm xét - điểm chuẩn) sau khi cùng quy về thang 30.',
  PRIMARY KEY (`id`),
  KEY `idx_xt_kqpa_lan` (`lan_danh_gia_id`,`de_an_chuong_trinh_id`),
  KEY `idx_xt_kqpa_phuong_an` (`phuong_an_id`),
  CONSTRAINT `fk_xt_kqpa_lan_danh_gia_id` FOREIGN KEY (`lan_danh_gia_id`) REFERENCES `xt_lan_danh_gia` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_kqpa_phuong_an_id` FOREIGN KEY (`phuong_an_id`) REFERENCES `xt_phuong_an` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kết quả tính điểm và xét điều kiện của học sinh trên từng phương án';

CREATE TABLE IF NOT EXISTS `xt_ket_qua_chuong_trinh` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `lan_danh_gia_id` bigint(20) unsigned NOT NULL,
  `de_an_chuong_trinh_id` bigint(20) unsigned NOT NULL,
  `ma_truong` varchar(20) NOT NULL,
  `ket_qua_phuong_an_id` bigint(20) unsigned NOT NULL COMMENT 'Phương án tốt nhất của học sinh cho chương trình này.',
  `la_xet_thang` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1: đủ điều kiện một diện xét tuyển thẳng đã mô hình hóa.',
  `diem_xet` decimal(7,2) DEFAULT NULL COMMENT 'Điểm xét của phương án tốt nhất (chép từ xt_ket_qua_phuong_an).',
  `thang_diem` decimal(6,2) DEFAULT NULL COMMENT 'Thang của diem_xet.',
  `chenh_lech_30` decimal(6,2) DEFAULT NULL COMMENT 'Chênh lệch so với điểm chuẩn tham chiếu, thang 30.',
  `diem_kha_nang` decimal(5,2) DEFAULT NULL COMMENT '0-100; NULL nếu chưa có điểm chuẩn tham chiếu.',
  `diem_nganh` decimal(5,2) DEFAULT NULL COMMENT '0-100; NULL nếu học sinh chưa chọn ngành hoặc chương trình chưa gắn mã ngành.',
  `diem_hoc_phi` decimal(5,2) DEFAULT NULL COMMENT '0-100; NULL nếu thiếu ngân sách hoặc học phí.',
  `diem_vi_tri` decimal(5,2) DEFAULT NULL COMMENT '0-100; NULL nếu học sinh không nêu địa điểm mong muốn.',
  `diem_phu_hop` decimal(5,2) DEFAULT NULL COMMENT 'Điểm tổng hợp 0-100 theo trọng số của bộ tiêu chí; NULL nếu chưa có diem_kha_nang (không chấm khi thiếu điểm chuẩn).',
  `xep_loai` varchar(50) DEFAULT NULL,
  `thu_hang` int(10) unsigned DEFAULT NULL COMMENT 'Thứ hạng trong lần đánh giá (1 = phù hợp nhất).',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_xt_kqct` (`lan_danh_gia_id`,`de_an_chuong_trinh_id`),
  KEY `idx_xt_kqct_xep_hang` (`lan_danh_gia_id`,`thu_hang`),
  KEY `idx_xt_kqct_truong` (`lan_danh_gia_id`,`ma_truong`),
  CONSTRAINT `fk_xt_kqct_lan_danh_gia_id` FOREIGN KEY (`lan_danh_gia_id`) REFERENCES `xt_lan_danh_gia` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xt_kqct_ket_qua_phuong_an_id` FOREIGN KEY (`ket_qua_phuong_an_id`) REFERENCES `xt_ket_qua_phuong_an` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mức độ phù hợp của từng chương trình với học sinh (mỗi chương trình một dòng, theo phương án tốt nhất)';

-- ---------------------------------------------------------------------
-- E. THAY ĐỔI DUY NHẤT TRÊN BẢNG CŨ
--    dats_tru_so chưa có tỉnh/thành -> không lọc được theo địa điểm cơ sở.
--    (Chạy lại file này sẽ báo lỗi "Duplicate column" ở câu dưới; bỏ qua.)
-- ---------------------------------------------------------------------
ALTER TABLE `dats_tru_so`
  ADD COLUMN `tinh_thanh_id` int(11) DEFAULT NULL COMMENT 'Tỉnh/thành của cơ sở; FK dm_tinh_thanh.id.' AFTER `dia_chi`,
  ADD KEY `idx_dats_tru_so_tinh_thanh_id` (`tinh_thanh_id`),
  ADD CONSTRAINT `fk_dats_tru_so_tinh_thanh_id` FOREIGN KEY (`tinh_thanh_id`) REFERENCES `dm_tinh_thanh` (`id`);
