-- Schema hiện có của database huongnghiep (không gồm dữ liệu).
-- Nguồn: MySQL INFORMATION_SCHEMA / SHOW CREATE TABLE.
-- Bỏ bảng alembic_version vì chỉ phục vụ migration.
-- Quan hệ:
--   truong_hoc_tuyen_sinh_theo_nam.ma_truong  ->  dm_truong.ma_truong
--
-- Khóa ngoại:
--   dm_chuyen_nganh.ma_nganh -> dm_nganh_dao_tao.ma_nganh  (fk_dm_chuyen_nganh_nganh, ON UPDATE CASCADE, ON DELETE RESTRICT)
--   dm_nganh_dao_tao.ma_nhom_nganh -> dm_nhom_nganh_dao_tao.ma_nhom_nganh  (fk_dm_nganh_nhom_nganh, ON UPDATE CASCADE, ON DELETE RESTRICT)
--   dm_nhom_nganh_dao_tao.ma_linh_vuc -> dm_linh_vuc_dao_tao.ma_linh_vuc  (fk_dm_nhom_nganh_linh_vuc, ON UPDATE CASCADE, ON DELETE RESTRICT)
--   nguoi_dung_thong_tin.doi_tuong_uu_tien_id -> dm_doi_tuong_uu_tien.id  (fk_nguoi_dung_thong_tin_doi_tuong, ON UPDATE RESTRICT, ON DELETE SET NULL)
--   nguoi_dung_thong_tin.khu_vuc_uu_tien_id -> dm_khu_vuc_uu_tien.id  (fk_nguoi_dung_thong_tin_khu_vuc, ON UPDATE RESTRICT, ON DELETE SET NULL)
--   nguoi_dung_thong_tin.tinh_thanh_id -> dm_tinh_thanh.id  (fk_nguoi_dung_thong_tin_tinh, ON UPDATE RESTRICT, ON DELETE SET NULL)
--   nguoi_dung_thong_tin.nguoi_dung_id -> nguoi_dung.id  (fk_nguoi_dung_thong_tin_user, ON UPDATE RESTRICT, ON DELETE CASCADE)
--   tn_cau_hoi_trac_nghiem.ma_holand -> dm_nhom_tinh_cach_holland.ma_nhom  (fk_tn_cau_hoi_holland, ON UPDATE CASCADE, ON DELETE RESTRICT)
--   tn_cau_hoi_trac_nghiem.loai_cau_hoi_id -> dm_loai_cau_hoi.id  (fk_tn_cau_hoi_loai, ON UPDATE RESTRICT, ON DELETE RESTRICT)
--   tn_cau_tra_loi.cau_hoi_id -> tn_cau_hoi_trac_nghiem.id  (fk_tn_cau_tra_loi_cau_hoi, ON UPDATE RESTRICT, ON DELETE CASCADE)
--   tn_chi_tiet_tra_loi.cau_hoi_id -> tn_cau_hoi_trac_nghiem.id  (fk_tn_chi_tiet_tra_loi_cau_hoi, ON UPDATE RESTRICT, ON DELETE RESTRICT)
--   tn_chi_tiet_tra_loi.loai_cau_hoi_id -> dm_loai_cau_hoi.id  (fk_tn_chi_tiet_tra_loi_loai, ON UPDATE RESTRICT, ON DELETE RESTRICT)
--   tn_chi_tiet_tra_loi.ssid -> tn_phien_khao_sat.ssid  (fk_tn_chi_tiet_tra_loi_phien, ON UPDATE CASCADE, ON DELETE CASCADE)
--   tn_chi_tiet_tra_loi.cau_tra_loi_id -> tn_cau_tra_loi.id  (fk_tn_chi_tiet_tra_loi_tra_loi, ON UPDATE RESTRICT, ON DELETE RESTRICT)
--   tn_phien_khao_sat.nguoi_khao_sat_id -> nguoi_dung.id  (fk_tn_phien_khao_sat_nguoi_dung, ON UPDATE RESTRICT, ON DELETE SET NULL)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- dm_bai_thi_danh_gia_nang_luc đã gộp vào dm_bai_thi_danh_gia.
-- dm_chung_chi_ngoai_ngu đã gộp vào dm_bang_cap_chung_chi.

CREATE TABLE `dm_chuyen_nganh` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_chuyen_nganh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_chuyen_nganh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_tieng_anh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `ma_holand` json DEFAULT NULL COMMENT 'Danh sách mã nhóm Holland (ma_nhom), không bắt buộc',
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ma_nganh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_chuyen_nganh_ma` (`ma_chuyen_nganh`),
  KEY `ix_dm_chuyen_nganh_ten` (`ten_chuyen_nganh`),
  KEY `ix_dm_chuyen_nganh_ma` (`ma_chuyen_nganh`),
  KEY `ix_dm_chuyen_nganh_ma_nganh` (`ma_nganh`),
  CONSTRAINT `fk_dm_chuyen_nganh_nganh` FOREIGN KEY (`ma_nganh`) REFERENCES `dm_nganh_dao_tao` (`ma_nganh`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_dan_toc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_dan_toc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_dan_toc` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_goi_khac` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dan_so` int(11) DEFAULT NULL,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_dan_toc_ma_dan_toc` (`ma_dan_toc`),
  KEY `ix_dm_dan_toc_ten_dan_toc` (`ten_dan_toc`),
  KEY `ix_dm_dan_toc_ma_dan_toc` (`ma_dan_toc`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_doi_tuong_uu_tien` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_doi_tuong` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_doi_tuong` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `diem_cong` decimal(5,2) NOT NULL DEFAULT '0.00',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_doi_tuong_uu_tien_ma_doi_tuong` (`ma_doi_tuong`),
  KEY `ix_dm_doi_tuong_uu_tien_ten_doi_tuong` (`ten_doi_tuong`),
  KEY `ix_dm_doi_tuong_uu_tien_ma_doi_tuong` (`ma_doi_tuong`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_khu_vuc_uu_tien` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_khu_vuc` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_khu_vuc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `diem_cong` decimal(5,2) NOT NULL DEFAULT '0.00',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_khu_vuc_uu_tien_ma_khu_vuc` (`ma_khu_vuc`),
  KEY `ix_dm_khu_vuc_uu_tien_ten_khu_vuc` (`ten_khu_vuc`),
  KEY `ix_dm_khu_vuc_uu_tien_ma_khu_vuc` (`ma_khu_vuc`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_linh_vuc_dao_tao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_linh_vuc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_linh_vuc` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_tieng_anh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_linh_vuc_ma` (`ma_linh_vuc`),
  KEY `ix_dm_linh_vuc_ten` (`ten_linh_vuc`),
  KEY `ix_dm_linh_vuc_ma` (`ma_linh_vuc`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_loai_cau_hoi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_loai_cau_hoi` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `thu_tu_uu_tien` int(11) NOT NULL,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_loai_cau_hoi_thu_tu` (`thu_tu_uu_tien`),
  KEY `ix_dm_loai_cau_hoi_ten` (`ten_loai_cau_hoi`),
  KEY `ix_dm_loai_cau_hoi_thu_tu` (`thu_tu_uu_tien`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_mon_hoc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_mon_hoc` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_mon_hoc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_viet_tat` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nhom_mon` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Nhóm môn: tự nhiên, xã hội, ngoại ngữ, ...',
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_mon_hoc_ma_mon_hoc` (`ma_mon_hoc`),
  KEY `ix_dm_mon_hoc_ten` (`ten_mon_hoc`),
  KEY `ix_dm_mon_hoc_ma` (`ma_mon_hoc`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_nganh_dao_tao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_nganh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_nganh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_tieng_anh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trinh_do` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_holand` json DEFAULT NULL COMMENT 'Danh sách mã nhóm Holland (ma_nhom), không bắt buộc',
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ma_nhom_nganh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hinh_anh_mo_ta` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'URL hình ảnh mô tả',
  `muc_luong_tham_khao` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mức lương tham khảo',
  `nhan_dan` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Nhãn dán nổi bật',
  `thoi_gian_dao_tao` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Thời gian đào tạo',
  `chi_tiet` text COLLATE utf8mb4_unicode_ci COMMENT 'Chi tiết ngành',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_nganh_ma` (`ma_nganh`),
  KEY `ix_dm_nganh_ten` (`ten_nganh`),
  KEY `ix_dm_nganh_ma` (`ma_nganh`),
  KEY `ix_dm_nganh_ma_nhom` (`ma_nhom_nganh`),
  CONSTRAINT `fk_dm_nganh_nhom_nganh` FOREIGN KEY (`ma_nhom_nganh`) REFERENCES `dm_nhom_nganh_dao_tao` (`ma_nhom_nganh`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_nhom_nganh_dao_tao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_nhom_nganh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_nhom_nganh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_tieng_anh` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ma_linh_vuc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_nhom_nganh_ma` (`ma_nhom_nganh`),
  KEY `ix_dm_nhom_nganh_ten` (`ten_nhom_nganh`),
  KEY `ix_dm_nhom_nganh_ma` (`ma_nhom_nganh`),
  KEY `ix_dm_nhom_nganh_ma_linh_vuc` (`ma_linh_vuc`),
  CONSTRAINT `fk_dm_nhom_nganh_linh_vuc` FOREIGN KEY (`ma_linh_vuc`) REFERENCES `dm_linh_vuc_dao_tao` (`ma_linh_vuc`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_nhom_tinh_cach_holland` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_nhom` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_nhom` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_tieng_anh` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `vi_du_nghe_nghiep` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_nhom_holland_ma_nhom` (`ma_nhom`),
  KEY `ix_dm_nhom_holland_ten` (`ten_nhom`),
  KEY `ix_dm_nhom_holland_ma` (`ma_nhom`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_phuong_thuc_tuyen_sinh` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_phuong_thuc` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_phuong_thuc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `giai_thich` text COLLATE utf8mb4_unicode_ci,
  `truong_hop_cu_the` text COLLATE utf8mb4_unicode_ci,
  `luu_y` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_phuong_thuc_tuyen_sinh_ma` (`ma_phuong_thuc`),
  KEY `ix_dm_phuong_thuc_tuyen_sinh_ten` (`ten_phuong_thuc`),
  KEY `ix_dm_phuong_thuc_tuyen_sinh_ma` (`ma_phuong_thuc`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_thanh_tich_hoc_tap_nghien_cuu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_thanh_tich` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_thanh_tich` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_chi_tiet` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `linh_vuc` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mon` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `thang_diem` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_thanh_tich_hoc_tap_nghien_cuu_ma` (`ma_thanh_tich`),
  KEY `ix_dm_thanh_tich_hoc_tap_nghien_cuu_ma` (`ma_thanh_tich`),
  KEY `ix_dm_thanh_tich_hoc_tap_nghien_cuu_ten` (`ten_thanh_tich`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_tinh_thanh` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_tinh` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_tinh` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `khu_vuc` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dien_tich` decimal(12,2) DEFAULT NULL,
  `nam_thanh_lap` smallint(6) DEFAULT NULL,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_tinh_thanh_ma_tinh` (`ma_tinh`),
  KEY `ix_dm_tinh_thanh_ten_tinh` (`ten_tinh`),
  KEY `ix_dm_tinh_thanh_ma_tinh` (`ma_tinh`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_to_hop_mon_hoc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ten_to_hop` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ma_to_hop` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ds_mon_hoc` json NOT NULL COMMENT 'Danh sách mã môn học (ma_mon_hoc) lấy từ dm_mon_hoc',
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_to_hop_mon_hoc_ma_to_hop` (`ma_to_hop`),
  KEY `ix_dm_to_hop_mon_hoc_ten` (`ten_to_hop`),
  KEY `ix_dm_to_hop_mon_hoc_ma` (`ma_to_hop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `dm_ton_giao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_ton_giao` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_ton_giao` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_dm_ton_giao_ma_ton_giao` (`ma_ton_giao`),
  KEY `ix_dm_ton_giao_ten_ton_giao` (`ten_ton_giao`),
  KEY `ix_dm_ton_giao_ma_ton_giao` (`ma_ton_giao`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `nguoi_dung` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ho_ten` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `so_dien_thoai` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mat_khau` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vai_tro` smallint(6) NOT NULL DEFAULT '0' COMMENT '0: người dùng, 1: admin',
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: khóa, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `so_dien_thoai` (`so_dien_thoai`),
  KEY `ix_nguoi_dung_email` (`email`),
  KEY `ix_nguoi_dung_so_dien_thoai` (`so_dien_thoai`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `nguoi_dung_thong_tin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nguoi_dung_id` int(11) NOT NULL,
  `gioi_tinh` smallint(6) DEFAULT NULL COMMENT '1: nam, 2: nữ, 3: khác',
  `ngay_sinh` date DEFAULT NULL,
  `dan_toc` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ton_giao` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trinh_do_hoc_van` json DEFAULT NULL,
  `suc_khoe_the_chat` json DEFAULT NULL,
  `kha_nang_tai_chinh` json DEFAULT NULL,
  `tinh_thanh_id` int(11) DEFAULT NULL,
  `edu_coin` int(11) NOT NULL DEFAULT '0',
  `xu_he_thong` int(11) NOT NULL DEFAULT '0',
  `mat_khau_thanh_toan` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `khu_vuc_uu_tien_id` int(11) DEFAULT NULL,
  `doi_tuong_uu_tien_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_nguoi_dung_thong_tin_user` (`nguoi_dung_id`),
  KEY `ix_nguoi_dung_thong_tin_tinh` (`tinh_thanh_id`),
  KEY `ix_nguoi_dung_thong_tin_khu_vuc` (`khu_vuc_uu_tien_id`),
  KEY `ix_nguoi_dung_thong_tin_doi_tuong` (`doi_tuong_uu_tien_id`),
  CONSTRAINT `fk_nguoi_dung_thong_tin_doi_tuong` FOREIGN KEY (`doi_tuong_uu_tien_id`) REFERENCES `dm_doi_tuong_uu_tien` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_nguoi_dung_thong_tin_khu_vuc` FOREIGN KEY (`khu_vuc_uu_tien_id`) REFERENCES `dm_khu_vuc_uu_tien` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_nguoi_dung_thong_tin_tinh` FOREIGN KEY (`tinh_thanh_id`) REFERENCES `dm_tinh_thanh` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_nguoi_dung_thong_tin_user` FOREIGN KEY (`nguoi_dung_id`) REFERENCES `nguoi_dung` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tn_cau_hoi_trac_nghiem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ma_holand` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `loai_cau_hoi_id` int(11) NOT NULL,
  `noi_dung_cau_hoi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `ghi_chu` text COLLATE utf8mb4_unicode_ci,
  `trang_thai` smallint(6) NOT NULL DEFAULT '1' COMMENT '0: ngừng sử dụng, 1: hoạt động',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_tn_cau_hoi_holland` (`ma_holand`),
  KEY `ix_tn_cau_hoi_loai` (`loai_cau_hoi_id`),
  CONSTRAINT `fk_tn_cau_hoi_holland` FOREIGN KEY (`ma_holand`) REFERENCES `dm_nhom_tinh_cach_holland` (`ma_nhom`) ON UPDATE CASCADE,
  CONSTRAINT `fk_tn_cau_hoi_loai` FOREIGN KEY (`loai_cau_hoi_id`) REFERENCES `dm_loai_cau_hoi` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=462 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tn_cau_tra_loi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cau_hoi_id` int(11) NOT NULL,
  `noi_dung_cau_tra_loi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `diem` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_tn_cau_tra_loi_cau_hoi` (`cau_hoi_id`),
  CONSTRAINT `fk_tn_cau_tra_loi_cau_hoi` FOREIGN KEY (`cau_hoi_id`) REFERENCES `tn_cau_hoi_trac_nghiem` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2234 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tn_chi_tiet_tra_loi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ssid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `loai_cau_hoi_id` int(11) NOT NULL,
  `cau_hoi_id` int(11) NOT NULL,
  `cau_tra_loi_id` int(11) DEFAULT NULL,
  `diem_dat_duoc` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_tn_chi_tiet_tra_loi_ssid` (`ssid`),
  KEY `ix_tn_chi_tiet_tra_loi_loai` (`loai_cau_hoi_id`),
  KEY `ix_tn_chi_tiet_tra_loi_cau_hoi` (`cau_hoi_id`),
  KEY `ix_tn_chi_tiet_tra_loi_tra_loi` (`cau_tra_loi_id`),
  CONSTRAINT `fk_tn_chi_tiet_tra_loi_cau_hoi` FOREIGN KEY (`cau_hoi_id`) REFERENCES `tn_cau_hoi_trac_nghiem` (`id`),
  CONSTRAINT `fk_tn_chi_tiet_tra_loi_loai` FOREIGN KEY (`loai_cau_hoi_id`) REFERENCES `dm_loai_cau_hoi` (`id`),
  CONSTRAINT `fk_tn_chi_tiet_tra_loi_phien` FOREIGN KEY (`ssid`) REFERENCES `tn_phien_khao_sat` (`ssid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_tn_chi_tiet_tra_loi_tra_loi` FOREIGN KEY (`cau_tra_loi_id`) REFERENCES `tn_cau_tra_loi` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=673 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tn_phien_khao_sat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ssid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nguoi_khao_sat_id` int(11) DEFAULT NULL,
  `ma_giao_dich` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `chi_tiet_ket_qua` json DEFAULT NULL,
  `thong_tin_thanh_toan` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tn_phien_khao_sat_ssid` (`ssid`),
  UNIQUE KEY `uq_tn_phien_khao_sat_ma_gd` (`ma_giao_dich`),
  KEY `ix_tn_phien_khao_sat_nguoi` (`nguoi_khao_sat_id`),
  CONSTRAINT `fk_tn_phien_khao_sat_nguoi_dung` FOREIGN KEY (`nguoi_khao_sat_id`) REFERENCES `nguoi_dung` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `truong_hoc_tuyen_sinh_theo_nam` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ma_truong` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã trường, tham chiếu dm_truong.ma_truong',
  `ten_truong` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tên trường trong đề án năm đó',
  `loai_hinh` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Loại hình trong đề án, ví dụ DaiHoc',
  `nam_tuyen_sinh` int(11) NOT NULL COMMENT 'Năm tuyển sinh',
  `dieu_kien_chung` json DEFAULT NULL COMMENT 'Điều kiện chung của trường. Mỗi phần tử có loai, toan_tu, gia_tri',
  `danh_sach_nganh` json NOT NULL COMMENT 'Danh sách ngành. Mỗi ngành có ma_nganh, ma_xet_tuyen, ten_nganh, ten_chuong_trinh, chi_tieu_nganh, dieu_kien_nganh và phuong_thuc_tuyen_sinh',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tuyen_sinh_nam_ma_truong_nam` (`ma_truong`,`nam_tuyen_sinh`),
  KEY `idx_tuyen_sinh_nam_nam` (`nam_tuyen_sinh`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
