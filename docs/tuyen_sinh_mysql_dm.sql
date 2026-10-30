-- ================================================================================
-- CẤU TRÚC CƠ SỞ DỮ LIỆU TUYỂN SINH (MySQL 8.0.16 trở lên)
-- Nguồn: Các bảng trong database (1).xlsx (14 sheet; 34 bảng, 454 cột gốc)
-- Phiên bản chuyển đổi: 2026-10-30
-- Bổ sung 3 bảng cần thiết để hoàn thiện các quan hệ:
--   dm_van_ban, dm_to_hop_mon_hoc_chi_tiet, dats_phuong_thuc_to_hop.
-- Tổng: 37 bảng; không dùng dữ liệu ở cột "Ví dụ" để INSERT.
-- Không DROP, TRUNCATE hoặc thay thế bảng hiện có.
-- Quy ước: bảng danh mục dm_* (14 bảng), bảng đề án dats_* (23 bảng).
-- LƯU Ý: dành cho database mới; CREATE IF NOT EXISTS không đổi tên bảng đã tồn tại.
-- CÁCH DÙNG: tạo/chọn database trước, sau đó import file này vào database đó.
-- Ví dụ (terminal): mysql -u root -p ten_database < tuyen_sinh_mysql_dm.sql
-- SQL được viết theo MySQL 8, InnoDB, UTF-8 và tương thích FOREIGN KEY.
-- Không mặc định nghiệp vụ; các cột chưa công bố cho phép NULL.
-- Trường de_an_id tại 2 bảng chính sách được chuẩn hóa sang UNSIGNED để tạo FK.
-- Các cột phuong_thuc_nguon_id/dich_id quy ước tham chiếu phương thức danh mục.
-- Chưa có dữ liệu quy đổi chính thức: không suy diễn mốc/công thức từ ví dụ.
-- ================================================================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 1;

-- Lưu ý: các giá trị ngày/số trong cột ví dụ Excel chỉ có tính minh họa.

-- ==== BẢNG BỔ SUNG: VĂN BẢN THAM CHIẾU ====
-- Văn bản quy phạm hoặc văn bản tham chiếu cho các danh mục (bổ sung thiết kế)
CREATE TABLE IF NOT EXISTS `dm_van_ban` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính kỹ thuật của văn bản.',
  `so_ky_hieu` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Số, ký hiệu văn bản được công bố.',
  `ten_van_ban` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Tên đầy đủ hoặc trích yếu văn bản.',
  `loai_van_ban` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Loại văn bản: thông tư, quyết định, quy chế,...',
  `co_quan_ban_hanh` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Cơ quan ban hành văn bản.',
  `ngay_ban_hanh` DATE NULL DEFAULT NULL COMMENT 'Ngày ban hành văn bản nếu được công bố.',
  `ngay_hieu_luc` DATE NULL DEFAULT NULL COMMENT 'Ngày có hiệu lực nếu được công bố.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn văn bản gốc để xác minh.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú hoặc phạm vi áp dụng.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_van_ban_so_ky_hieu` (`so_ky_hieu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Văn bản quy phạm hoặc văn bản tham chiếu cho các danh mục (bổ sung thiết kế)';

-- ==== CÁC BẢNG DANH MỤC ====
-- Thông tin các trường học
CREATE TABLE IF NOT EXISTS `dm_truong` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng, dùng liên kết với các bảng khác.',
  `ma_truong` VARCHAR(20) NOT NULL COMMENT 'Mã trường do cơ quan quản lý quy định.',
  `ten_truong` VARCHAR(255) NOT NULL COMMENT 'Tên tiếng Việt chính thức.',
  `ten_tieng_anh` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên tiếng Anh chính thức.',
  `ten_viet_tat` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Tên viết tắt thường dùng.',
  `ten_goi_khac` JSON NULL DEFAULT NULL COMMENT 'Danh sách tên cũ hoặc tên thường gọi, hỗ trợ tìm kiếm.',
  `slug` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Định danh dùng trong đường dẫn trang thông tin trường.',
  `loai_co_so` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Phân loại cơ sở giáo dục: cao đẳng, trường đại học, đại học, học viện.',
  `loai_hinh` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Loại hình sở hữu: công lập, tư thục hoặc có vốn đầu tư nước ngoài.',
  `co_quan_chu_quan` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Cơ quan hoặc tổ chức chủ quản, nếu có.',
  `truong_cha_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID của đại học mà trường trực thuộc; tham chiếu dm_truong.id.',
  `ngay_thanh_lap` DATE NULL DEFAULT NULL COMMENT 'Ngày thành lập chính thức, nếu biết đầy đủ ngày, tháng, năm.',
  `nam_thanh_lap` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm thành lập; vẫn lưu được khi chưa biết ngày và tháng.',
  `gioi_thieu_ngan` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Mô tả ngắn để hiển thị trong danh sách trường.',
  `gioi_thieu_chi_tiet` TEXT NULL DEFAULT NULL COMMENT 'Nội dung giới thiệu đầy đủ về lịch sử, hoạt động và định hướng phát triển.',
  `the_manh` TEXT NULL DEFAULT NULL COMMENT 'Thế mạnh nổi bật về đào tạo, nghiên cứu hoặc hợp tác.',
  `bac_dao_tao` JSON NULL DEFAULT NULL COMMENT 'Danh sách các bậc đào tạo trường cung cấp.',
  `linh_vuc_dao_tao_chinh` JSON NULL DEFAULT NULL COMMENT 'Danh sách lĩnh vực đào tạo chính.',
  `linh_vuc_dao_tao_khac` JSON NULL DEFAULT NULL COMMENT 'Các lĩnh vực đào tạo khác ngoài lĩnh vực chính.',
  `ma_tinh_thanh` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Mã tỉnh/thành phố nơi đặt trụ sở chính.',
  `ten_tinh_thanh` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Tên tỉnh/thành phố của trụ sở chính.',
  `ma_phuong_xa` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Mã phường/xã của trụ sở chính.',
  `ten_phuong_xa` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Tên phường/xã của trụ sở chính.',
  `dia_chi_tru_so` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Địa chỉ đầy đủ của trụ sở chính.',
  `vung_mien` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Vùng miền để tìm kiếm, lọc trường.',
  `vi_do` DECIMAL(10,7) NULL DEFAULT NULL COMMENT 'Vĩ độ trụ sở chính, phục vụ hiển thị trên bản đồ.',
  `kinh_do` DECIMAL(10,7) NULL DEFAULT NULL COMMENT 'Kinh độ trụ sở chính.',
  `so_dien_thoai` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Số điện thoại liên hệ chung; lưu chuỗi để giữ số 0 đầu hoặc dấu +.',
  `email` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Email liên hệ chung.',
  `website` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Địa chỉ website chính thức.',
  `website_tuyen_sinh` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Địa chỉ trang thông tin tuyển sinh chính thức.',
  `hotline_tuyen_sinh` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Số điện thoại hỗ trợ tuyển sinh.',
  `email_tuyen_sinh` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Email hỗ trợ tuyển sinh.',
  `logo_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn ảnh logo của trường.',
  `anh_dai_dien_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn ảnh đại diện hoặc ảnh khuôn viên.',
  `dien_tich_m2` DECIMAL(15,2) NULL DEFAULT NULL COMMENT 'Diện tích tính bằng m²; cần thống nhất phạm vi đo.',
  `hoc_phi_trung_binh` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Mức học phí tham khảo.',
  `trang_thai_hoat_dong` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Trạng thái hoạt động của trường.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn nguồn chính dùng để xác minh thông tin.',
  `ngay_xac_minh` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm gần nhất thông tin được kiểm tra với nguồn.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung hoặc nội dung cần xác minh.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật bản ghi gần nhất.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_truong_ma_truong` (`ma_truong`),
  KEY `idx_dm_truong_slug` (`slug`),
  KEY `idx_dm_truong_loai_co_so_vung_mien` (`loai_co_so`, `vung_mien`),
  KEY `idx_dm_truong_truong_cha_id` (`truong_cha_id`),
  CONSTRAINT `chk_dm_truong_vi_do` CHECK (vi_do IS NULL OR (vi_do BETWEEN -90 AND 90)),
  CONSTRAINT `chk_dm_truong_kinh_do` CHECK (kinh_do IS NULL OR (kinh_do BETWEEN -180 AND 180)),
  CONSTRAINT `fk_dm_truong_truong_cha_id` FOREIGN KEY (`truong_cha_id`) REFERENCES `dm_truong` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Thông tin các trường học';

-- Danh mục ngành đào tạo
CREATE TABLE IF NOT EXISTS `dm_nganh_dao_tao` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_nganh` VARCHAR(20) NOT NULL COMMENT 'Mã số lĩnh vực, nhóm ngành hoặc ngành trong danh mục của Bộ. Lưu dạng chuỗi để giữ nguyên mã.',
  `ten_nganh` VARCHAR(255) NOT NULL COMMENT 'Tên lĩnh vực, nhóm ngành hoặc ngành theo danh mục.',
  `cap_danh_muc` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Cấp của bản ghi trong hệ thống phân cấp.',
  `nganh_cha_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID lĩnh vực hoặc nhóm ngành cấp trên; tham chiếu dm_nganh_dao_tao.id. Để NULL nếu là cấp cao nhất.',
  `trinh_do_ap_dung` JSON NULL DEFAULT NULL COMMENT 'Các trình độ áp dụng theo danh mục hoặc dữ liệu đối chiếu.',
  `ngay_hieu_luc_tu` DATE NULL DEFAULT NULL COMMENT 'Ngày bắt đầu hiệu lực của mã hoặc tên ngành.',
  `ngay_hieu_luc_den` DATE NULL DEFAULT NULL COMMENT 'Ngày kết thúc hiệu lực, nếu có; để NULL nếu chưa xác định.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái của bản ghi trong danh mục.',
  `ghi_chu_theo_thong_tu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú được nêu trong phụ lục danh mục ngành.',
  `van_ban_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID văn bản nguồn; tham chiếu bảng văn bản pháp lý nếu có.',
  `thu_tu_hien_thi` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự sắp xếp trong danh mục.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật gần nhất.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_nganh_dao_tao_ma_nganh` (`ma_nganh`),
  KEY `idx_dm_nganh_dao_tao_ngay_hieu_luc_tu` (`ngay_hieu_luc_tu`),
  KEY `idx_dm_nganh_dao_tao_nganh_cha_id` (`nganh_cha_id`),
  KEY `idx_dm_nganh_dao_tao_van_ban_id` (`van_ban_id`),
  CONSTRAINT `fk_dm_nganh_dao_tao_nganh_cha_id` FOREIGN KEY (`nganh_cha_id`) REFERENCES `dm_nganh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dm_nganh_dao_tao_van_ban_id` FOREIGN KEY (`van_ban_id`) REFERENCES `dm_van_ban` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục ngành đào tạo';

-- Danh mục bằng cấp và chứng chỉ
CREATE TABLE IF NOT EXISTS `dm_bang_cap_chung_chi` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_chung_chi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã định danh chứng chỉ trong hệ thống.',
  `ten_chung_chi` VARCHAR(255) NOT NULL COMMENT 'Tên chứng chỉ.',
  `ten_chi_tiet` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Tên đầy đủ hoặc mô tả ngắn của chứng chỉ.',
  `linh_vuc` VARCHAR(150) NULL DEFAULT NULL COMMENT 'Lĩnh vực của chứng chỉ.',
  `mon` VARCHAR(150) NULL DEFAULT NULL COMMENT 'Môn hoặc nội dung được đánh giá.',
  `ma_ngon_ngu` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Mã ngôn ngữ được đánh giá.',
  `ten_ngon_ngu` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Tên ngôn ngữ được đánh giá.',
  `don_vi_cap` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tổ chức cấp hoặc đồng sở hữu chứng chỉ.',
  `loai_chung_chi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Nhóm hoặc loại chứng chỉ.',
  `thang_diem` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Mô tả thang điểm bằng chữ, ví dụ 0-9 hoặc Bậc 1-6.',
  `thang_diem_min` DECIMAL(6,2) NULL DEFAULT NULL COMMENT 'Điểm thấp nhất của thang điểm chứng chỉ.',
  `thang_diem_max` DECIMAL(6,2) NULL DEFAULT NULL COMMENT 'Điểm cao nhất của thang điểm chứng chỉ.',
  `don_vi_diem` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Đơn vị ghi điểm của chứng chỉ.',
  `ky_nang_duoc_danh_gia` JSON NULL DEFAULT NULL COMMENT 'Danh sách kỹ năng được đánh giá.',
  `hinh_thuc_thi` JSON NULL DEFAULT NULL COMMENT 'Danh sách hình thức thi có thể có.',
  `ghi_chu_hinh_thuc_thi` TEXT NULL DEFAULT NULL COMMENT 'Mô tả hoặc lưu ý về các hình thức thi.',
  `thoi_han_hieu_luc_thang` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thời hạn hiệu lực tính bằng tháng, nếu có quy định thống nhất.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng trong danh mục.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú chung về chứng chỉ hoặc cách xác minh.',
  `tao_luc` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Thời điểm cập nhật bản ghi gần nhất.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_bang_cap_chung_chi_ma_chung_chi` (`ma_chung_chi`),
  CONSTRAINT `chk_dm_bang_cap_chung_chi_thang_diem_min` CHECK (thang_diem_min IS NULL OR thang_diem_max IS NULL OR thang_diem_max >= thang_diem_min)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục bằng cấp và chứng chỉ';

-- Danh mục các bài thi đánh giá
CREATE TABLE IF NOT EXISTS `dm_bai_thi_danh_gia` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_bai_thi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã định danh bài thi trong hệ thống.',
  `ten_bai_thi` VARCHAR(255) NOT NULL COMMENT 'Tên chính thức của bài thi hoặc kỳ thi.',
  `ten_chi_tiet` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Tên đầy đủ hoặc mô tả ngắn của bài thi.',
  `linh_vuc` VARCHAR(150) NULL DEFAULT NULL COMMENT 'Lĩnh vực của bài thi.',
  `mon` VARCHAR(150) NULL DEFAULT NULL COMMENT 'Môn hoặc nội dung được đánh giá.',
  `ten_viet_tat` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Tên viết tắt thường dùng.',
  `don_vi_to_chuc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Đơn vị tổ chức hoặc quản lý bài thi.',
  `loai_danh_gia` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Loại bài thi hoặc năng lực được đánh giá.',
  `loai_chung_chi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Nhóm trong nước hoặc quốc tế: trong_nuoc, quoc_te.',
  `mo_ta` TEXT NULL DEFAULT NULL COMMENT 'Mô tả mục tiêu và phạm vi đánh giá của bài thi.',
  `doi_tuong_du_thi` TEXT NULL DEFAULT NULL COMMENT 'Nhóm đối tượng có thể dự thi.',
  `hinh_thuc_thi` JSON NULL DEFAULT NULL COMMENT 'Các hình thức tổ chức có thể áp dụng.',
  `thang_diem` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Mô tả thang điểm bằng chữ, ví dụ 0-150 hoặc 400-1600.',
  `diem_toi_thieu` DECIMAL(8,2) NULL DEFAULT NULL COMMENT 'Điểm thấp nhất có thể ghi nhận, nếu xác định được.',
  `don_vi_diem` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Đơn vị hoặc cách biểu diễn điểm.',
  `cau_truc_bai_thi` JSON NULL DEFAULT NULL COMMENT 'Các phần thi, số câu, thời lượng hoặc trọng số.',
  `thoi_luong_phut` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổng thời lượng làm bài tính bằng phút.',
  `cach_cong_bo_ket_qua` TEXT NULL DEFAULT NULL COMMENT 'Mô tả cách đơn vị tổ chức công bố kết quả, nếu có.',
  `nam_ap_dung_tu` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm bắt đầu có thông tin trong danh mục.',
  `nam_ap_dung_den` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm kết thúc áp dụng; để NULL nếu chưa xác định.',
  `website_chinh_thuc` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Trang thông tin chính thức của bài thi hoặc đơn vị tổ chức.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn nguồn dùng để xác minh thông tin.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái của bài thi trong danh mục.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  `tao_luc` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Thời điểm cập nhật bản ghi gần nhất.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_bai_thi_danh_gia_ma_bai_thi` (`ma_bai_thi`),
  KEY `idx_dm_bai_thi_danh_gia_ma_bai_thi` (`ma_bai_thi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục các bài thi đánh giá';

-- Danh mục thành tích học tập
CREATE TABLE IF NOT EXISTS `dm_thanh_tich_hoc_tap` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_loai_thanh_tich` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Mã loại thành tích.',
  `ten_loai_thanh_tich` VARCHAR(255) NOT NULL COMMENT 'Tên loại thành tích.',
  `loai_cuoc_thi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Nhóm cuộc thi hoặc hoạt động.',
  `cap_cuoc_thi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Cấp tổ chức hoặc phạm vi cuộc thi.',
  `cac_muc_giai` JSON NULL DEFAULT NULL COMMENT 'Danh sách giải thưởng có thể đạt trong loại thành tích này. Mỗi giải gồm mã, tên và thứ tự.',
  `mo_ta` TEXT NULL DEFAULT NULL COMMENT 'Mô tả loại thành tích.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng trong danh mục.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_thanh_tich_hoc_tap_ma_loai_thanh_tich` (`ma_loai_thanh_tich`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục thành tích học tập';

-- Danh mục dân tộc
CREATE TABLE IF NOT EXISTS `dm_dan_toc` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_dan_toc` VARCHAR(10) NOT NULL COMMENT 'Mã dân tộc theo danh mục hệ thống sử dụng.',
  `ten_dan_toc` VARCHAR(100) NOT NULL COMMENT 'Tên dân tộc.',
  `ten_goi_khac` JSON NULL DEFAULT NULL COMMENT 'Tên gọi khác hoặc tên biến thể, nếu có.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_dan_toc_ma_dan_toc` (`ma_dan_toc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục dân tộc';

-- Danh mục tôn giáo
CREATE TABLE IF NOT EXISTS `dm_ton_giao` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_ton_giao` VARCHAR(10) NOT NULL COMMENT 'Mã tôn giáo theo danh mục hệ thống sử dụng.',
  `ten_ton_giao` VARCHAR(100) NOT NULL COMMENT 'Tên tôn giáo.',
  `ten_goi_khac` JSON NULL DEFAULT NULL COMMENT 'Tên gọi khác hoặc tên viết tắt.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_ton_giao_ma_ton_giao` (`ma_ton_giao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục tôn giáo';

-- Danh mục đối tượng ưu tiên
CREATE TABLE IF NOT EXISTS `dm_doi_tuong_uu_tien` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_doi_tuong` VARCHAR(10) NOT NULL COMMENT 'Mã đối tượng theo quy chế.',
  `ten_doi_tuong` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên ngắn của diện ưu tiên.',
  `mo_ta_dieu_kien` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện để được hưởng ưu tiên.',
  `nhom_uu_tien` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Nhóm ưu tiên.',
  `diem_uu_tien_co_ban` DECIMAL(5,2) NULL DEFAULT NULL COMMENT 'Mức điểm ưu tiên cơ bản theo thang điểm 30.',
  `nam_ap_dung` SMALLINT UNSIGNED NOT NULL COMMENT 'Năm tuyển sinh áp dụng.',
  `van_ban_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID văn bản quy định, nếu có bảng văn bản.',
  `thu_tu_hien_thi` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự hiển thị.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái bản ghi.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú về phạm vi hoặc cách áp dụng.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_doi_tuong_uu_tien_ma_doi_tuong_nam_ap_dung` (`ma_doi_tuong`, `nam_ap_dung`),
  KEY `idx_dm_doi_tuong_uu_tien_van_ban_id` (`van_ban_id`),
  CONSTRAINT `fk_dm_doi_tuong_uu_tien_van_ban_id` FOREIGN KEY (`van_ban_id`) REFERENCES `dm_van_ban` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục đối tượng ưu tiên';

-- Danh mục khu vực ưu tiên
CREATE TABLE IF NOT EXISTS `dm_khu_vuc_uu_tien` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_khu_vuc` VARCHAR(10) NOT NULL COMMENT 'Mã khu vực ưu tiên.',
  `ten_khu_vuc` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Tên khu vực.',
  `mo_ta_dieu_kien` TEXT NULL DEFAULT NULL COMMENT 'Mô tả địa bàn hoặc tiêu chí xác định khu vực.',
  `diem_uu_tien_co_ban` DECIMAL(5,2) NULL DEFAULT NULL COMMENT 'Mức điểm ưu tiên cơ bản theo thang điểm 30.',
  `nam_ap_dung` SMALLINT UNSIGNED NOT NULL COMMENT 'Năm tuyển sinh áp dụng.',
  `van_ban_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'ID văn bản quy định, nếu có bảng văn bản.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái bản ghi.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú về địa bàn hoặc cách xác định.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_khu_vuc_uu_tien_ma_khu_vuc_nam_ap_dung` (`ma_khu_vuc`, `nam_ap_dung`),
  KEY `idx_dm_khu_vuc_uu_tien_van_ban_id` (`van_ban_id`),
  CONSTRAINT `fk_dm_khu_vuc_uu_tien_van_ban_id` FOREIGN KEY (`van_ban_id`) REFERENCES `dm_van_ban` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục khu vực ưu tiên';

-- Danh mục phương thức tuyển sinh
CREATE TABLE IF NOT EXISTS `dm_phuong_thuc_tuyen_sinh` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_phuong_thuc` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Mã phương thức; dùng kiểu chuỗi để hỗ trợ cả mã số và mã chữ.',
  `ten_phuong_thuc` VARCHAR(255) NOT NULL COMMENT 'Tên phương thức tuyển sinh.',
  `giai_thich` TEXT NULL DEFAULT NULL COMMENT 'Mô tả cách thức xét tuyển của phương thức.',
  `truong_hop_cu_the` TEXT NULL DEFAULT NULL COMMENT 'Ví dụ hoặc tình huống cụ thể áp dụng phương thức.',
  `luu_y` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện, giới hạn hoặc lưu ý khi áp dụng.',
  `loai_phuong_thuc` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Nhóm phương thức để phân loại.',
  `pham_vi_ap_dung` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Phạm vi định nghĩa: danh mục chung hay phương thức riêng của trường.',
  `nam_ap_dung_tu` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm bắt đầu áp dụng bản ghi.',
  `nam_ap_dung_den` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm kết thúc áp dụng; để NULL nếu chưa xác định.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái bản ghi trong danh mục.',
  `thu_tu_hien_thi` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự hiển thị trong giao diện.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn văn bản hoặc trang nguồn của thông tin.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú quản trị hoặc nội dung cần kiểm tra.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật gần nhất.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_phuong_thuc_tuyen_sinh_ma_phuong_thuc` (`ma_phuong_thuc`),
  KEY `idx_dm_phuong_thuc_tuyen_sinh_nam_ap_dung_tu` (`nam_ap_dung_tu`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục phương thức tuyển sinh';

-- Danh mục môn học
CREATE TABLE IF NOT EXISTS `dm_mon_hoc` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_mon` VARCHAR(20) NOT NULL COMMENT 'Mã định danh môn học.',
  `ten_mon` VARCHAR(100) NOT NULL COMMENT 'Tên môn học.',
  `ten_tieng_anh` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Tên tiếng Anh, nếu có.',
  `ten_goi_khac` JSON NULL DEFAULT NULL COMMENT 'Tên viết tắt hoặc tên gọi khác.',
  `mo_ta` TEXT NULL DEFAULT NULL COMMENT 'Mô tả nội dung hoặc phạm vi môn học.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng trong danh mục.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật gần nhất.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dm_mon_hoc_ma_mon` (`ma_mon`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục môn học';

-- Danh mục tổ hợp môn học
CREATE TABLE IF NOT EXISTS `dm_to_hop_mon_hoc` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `ma_to_hop` VARCHAR(20) NOT NULL COMMENT 'Mã tổ hợp môn học.',
  `ten_to_hop` VARCHAR(255) NOT NULL COMMENT 'Tên đầy đủ của tổ hợp.',
  `mo_ta` TEXT NULL DEFAULT NULL COMMENT 'Mô tả tổ hợp hoặc mục đích sử dụng.',
  `nam_ap_dung_tu` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm bắt đầu áp dụng, nếu tổ hợp có thời hạn.',
  `nam_ap_dung_den` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm kết thúc áp dụng; để NULL nếu chưa xác định.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái sử dụng của tổ hợp.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật gần nhất.',
  PRIMARY KEY (`id`),
  KEY `idx_dm_to_hop_mon_hoc_ma_to_hop` (`ma_to_hop`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh mục tổ hợp môn học';

-- ==== BẢNG LIÊN KẾT TỔ HỢP - MÔN HỌC ====
-- Bảng nối nhiều-nhiều giữa tổ hợp và môn học (bổ sung thiết kế)
CREATE TABLE IF NOT EXISTS `dm_to_hop_mon_hoc_chi_tiet` (
  `to_hop_id` BIGINT UNSIGNED NOT NULL COMMENT 'Khóa ngoại đến tổ hợp môn học.',
  `mon_hoc_id` BIGINT UNSIGNED NOT NULL COMMENT 'Khóa ngoại đến môn học trong tổ hợp.',
  `thu_tu_mon` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự của môn trong tổ hợp, nếu có.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Lưu ý riêng về môn học trong tổ hợp.',
  PRIMARY KEY (`to_hop_id`, `mon_hoc_id`),
  KEY `idx_dm_to_hop_mon_hoc_chi_tiet_to_hop_id` (`to_hop_id`),
  KEY `idx_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id` (`mon_hoc_id`),
  CONSTRAINT `fk_dm_to_hop_mon_hoc_chi_tiet_to_hop_id` FOREIGN KEY (`to_hop_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id` FOREIGN KEY (`mon_hoc_id`) REFERENCES `dm_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Bảng nối nhiều-nhiều giữa tổ hợp và môn học (bổ sung thiết kế)';

-- ==== CÁC BẢNG ĐỀ ÁN TUYỂN SINH ====
-- Thông tin chung của đề án theo trường và năm tuyển sinh
CREATE TABLE IF NOT EXISTS `dats_tuyen_sinh` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính, tự tăng.',
  `truong_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đơn vị đào tạo; khóa ngoại đến dm_truong.id.',
  `nam_tuyen_sinh` SMALLINT UNSIGNED NOT NULL COMMENT 'Năm tuyển sinh của đề án.',
  `chi_tieu` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổng chỉ tiêu của đợt tuyển sinh',
  `ten_de_an` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên đề án/thông tin tuyển sinh.',
  `hinh_thuc_dao_tao` JSON NULL DEFAULT NULL COMMENT 'Danh sách hình thức đào tạo tuyển sinh.',
  `gioi_thieu` TEXT NULL DEFAULT NULL COMMENT 'Nội dung tổng quan đề án.',
  `ngay_cong_bo` DATE NULL DEFAULT NULL COMMENT 'Ngày công bố đề án.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Đường dẫn đề án gốc.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái đề án.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú/cập nhật.',
  `tao_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm tạo bản ghi.',
  `cap_nhat_luc` DATETIME NULL DEFAULT NULL COMMENT 'Thời điểm cập nhật gần nhất.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_tuyen_sinh_truong_id_nam_tuyen_sinh` (`truong_id`, `nam_tuyen_sinh`),
  CONSTRAINT `fk_dats_tuyen_sinh_truong_id` FOREIGN KEY (`truong_id`) REFERENCES `dm_truong` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Thông tin chung của đề án theo trường và năm tuyển sinh';

-- Trụ sở, cơ sở và phân hiệu của trường
CREATE TABLE IF NOT EXISTS `dats_tru_so` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `vai_tro` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Vai trò địa điểm: chính/phụ.',
  `ten_co_so` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên trụ sở/cơ sở/phân hiệu.',
  `loai_co_so` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Loại địa điểm.',
  `dia_chi` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Địa chỉ đầy đủ.',
  `so_dien_thoai` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Số liên hệ tại địa điểm.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_tru_so_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_tru_so_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Trụ sở, cơ sở và phân hiệu của trường';

-- Các trang thông tin điện tử liên quan đến đề án
CREATE TABLE IF NOT EXISTS `dats_website` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `loai_website` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Phân loại website.',
  `ten_trang` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên trang thông tin.',
  `url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'Địa chỉ trang.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Mô tả/lưu ý.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_website_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_website_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Các trang thông tin điện tử liên quan đến đề án';

-- Đầu mối, số điện thoại và email tư vấn tuyển sinh
CREATE TABLE IF NOT EXISTS `dats_lien_he_tuyen_sinh` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `ten_don_vi` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Đơn vị phụ trách.',
  `ten_nguoi_lien_he` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Người liên hệ nếu công bố.',
  `chuc_vu` VARCHAR(150) NULL DEFAULT NULL COMMENT 'Chức vụ người liên hệ.',
  `so_dien_thoai` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Số điện thoại.',
  `email` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Email liên hệ.',
  `thoi_gian_lien_he` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Khung giờ hỗ trợ.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin liên hệ bổ sung.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_lien_he_tuyen_sinh_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_lien_he_tuyen_sinh_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Đầu mối, số điện thoại và email tư vấn tuyển sinh';

-- Danh sách chương trình và chỉ tiêu tổng theo chương trình
CREATE TABLE IF NOT EXISTS `dats_chuong_trinh_dao_tao` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `nganh_dao_tao_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Ngành chuẩn; FK dm_nganh_dao_tao.id.',
  `ma_xet_tuyen` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Mã xét tuyển do trường công bố.',
  `ten_chuong_trinh` VARCHAR(255) NOT NULL COMMENT 'Tên chương trình/ngành trong đề án.',
  `trinh_do_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Trình độ đào tạo.',
  `hinh_thuc_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Hình thức đào tạo.',
  `co_so_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Cơ sở/phân hiệu phụ trách; có thể NULL.',
  `thoi_gian_dao_tao_nam` DECIMAL(4,1) NULL DEFAULT NULL COMMENT 'Thời lượng đào tạo theo năm.',
  `ngon_ngu_dao_tao` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Ngôn ngữ giảng dạy.',
  `chi_tieu_tuyen_sinh` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổng chỉ tiêu chương trình.',
  `kieu_phan_bo_chi_tieu` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Phân bổ theo phương thức hay dùng chung.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_chuong_trinh_dao_tao_de_an_id_ma_xet_tuyen` (`de_an_id`, `ma_xet_tuyen`),
  KEY `idx_dats_chuong_trinh_dao_tao_nganh_dao_tao_id` (`nganh_dao_tao_id`),
  KEY `idx_dats_chuong_trinh_dao_tao_co_so_id` (`co_so_id`),
  CONSTRAINT `fk_dats_chuong_trinh_dao_tao_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_chuong_trinh_dao_tao_nganh_dao_tao_id` FOREIGN KEY (`nganh_dao_tao_id`) REFERENCES `dm_nganh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_chuong_trinh_dao_tao_co_so_id` FOREIGN KEY (`co_so_id`) REFERENCES `dats_tru_so` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Danh sách chương trình và chỉ tiêu tổng theo chương trình';

-- Kế hoạch và phạm vi tuyển sinh của chương trình
CREATE TABLE IF NOT EXISTS `dats_ke_hoach_tuyen_sinh` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NOT NULL COMMENT 'Chương trình tuyển sinh.',
  `don_vi_chi_tieu` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Đơn vị tính chỉ tiêu.',
  `pham_vi_tuyen_sinh` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Phạm vi tuyển sinh.',
  `dot_tuyen_sinh` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Đợt tuyển sinh.',
  `thoi_gian_nhan_ho_so` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Thời gian nhận hồ sơ.',
  `dieu_kien_chung` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện chung trong kế hoạch.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú kế hoạch.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  CONSTRAINT `fk_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Kế hoạch và phạm vi tuyển sinh của chương trình';

-- Phương thức, điều kiện và chỉ tiêu theo phương thức
CREATE TABLE IF NOT EXISTS `dats_phuong_thuc` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NOT NULL COMMENT 'Chương trình áp dụng.',
  `phuong_thuc_id` BIGINT UNSIGNED NOT NULL COMMENT 'Danh mục phương thức; FK dm_phuong_thuc_tuyen_sinh.id.',
  `ma_phuong_thuc_cua_truong` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Mã riêng của trường.',
  `ten_phuong_thuc_cua_truong` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên phương thức theo đề án.',
  `chi_tieu_phuong_thuc` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Chỉ tiêu riêng; NULL nếu không chia chỉ tiêu.',
  `dieu_kien_can` JSON NULL DEFAULT NULL COMMENT 'Điều kiện bắt buộc.',
  `dieu_kien_du` JSON NULL DEFAULT NULL COMMENT 'Tiêu chí để đủ điều kiện trúng tuyển.',
  `diem_san` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Ngưỡng nhận hồ sơ nếu công bố.',
  `diem_chuan` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Ngưỡng trúng tuyển hồ sơ.',
  `thang_diem` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Thang điểm xét tuyển.',
  `cong_thuc_tinh_diem` TEXT NULL DEFAULT NULL COMMENT 'Công thức điểm xét tuyển.',
  `to_hop_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổ hợp áp dụng; NULL nếu không dùng tổ hợp.; một tổ hợp theo Excel; nhiều tổ hợp dùng dats_phuong_thuc_to_hop.',
  `thu_tu_uu_tien` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự hiển thị.',
  `ghi_chu_chi_tieu` TEXT NULL DEFAULT NULL COMMENT 'Cách phân bổ chỉ tiêu.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Lưu ý phương thức.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_phuong_thuc_de_an_chuong_trinh_id_phuong_thuc_id` (`de_an_chuong_trinh_id`, `phuong_thuc_id`),
  KEY `idx_dats_phuong_thuc_phuong_thuc_id` (`phuong_thuc_id`),
  KEY `idx_dats_phuong_thuc_to_hop_id` (`to_hop_id`),
  CONSTRAINT `fk_dats_phuong_thuc_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_phuong_thuc_phuong_thuc_id` FOREIGN KEY (`phuong_thuc_id`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_phuong_thuc_to_hop_id` FOREIGN KEY (`to_hop_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Phương thức, điều kiện và chỉ tiêu theo phương thức';

-- ==== BẢNG LIÊN KẾT PHƯƠNG THỨC - TỔ HỢP ====
-- Liên kết N-N giữa phương thức của đề án và tổ hợp môn (bổ sung thiết kế)
CREATE TABLE IF NOT EXISTS `dats_phuong_thuc_to_hop` (
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NOT NULL COMMENT 'Khóa ngoại đến phương thức xét tuyển cụ thể trong đề án.',
  `to_hop_id` BIGINT UNSIGNED NOT NULL COMMENT 'Khóa ngoại đến tổ hợp môn xét tuyển.',
  `thu_tu_hien_thi` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự hiển thị tổ hợp của phương thức.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Lưu ý phạm vi hoặc điều kiện riêng của tổ hợp.',
  PRIMARY KEY (`de_an_phuong_thuc_id`, `to_hop_id`),
  KEY `idx_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  KEY `idx_dats_phuong_thuc_to_hop_to_hop_id` (`to_hop_id`),
  CONSTRAINT `fk_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_phuong_thuc_to_hop_to_hop_id` FOREIGN KEY (`to_hop_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Liên kết N-N giữa phương thức của đề án và tổ hợp môn (bổ sung thiết kế)';

-- Đội ngũ giảng viên và cán bộ quản lý được đề án công bố
CREATE TABLE IF NOT EXISTS `dats_nhan_su` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `nhom_nhan_su` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Nhóm giảng viên/cán bộ quản lý.',
  `ten_nhan_su` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên cá nhân nếu công bố; có thể NULL.',
  `chuc_danh` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Chức danh/vị trí.',
  `hoc_vi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Học vị.',
  `hoc_ham` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Học hàm.',
  `linh_vuc_chuyen_mon` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Lĩnh vực chuyên môn.',
  `so_luong` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Số lượng nếu thống kê tổng hợp.',
  `nam_thong_ke` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm thống kê.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú số liệu.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_nhan_su_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_nhan_su_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Đội ngũ giảng viên và cán bộ quản lý được đề án công bố';

-- Cơ sở vật chất phục vụ đào tạo
CREATE TABLE IF NOT EXISTS `dats_co_so_vat_chat` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `co_so_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Cơ sở sở hữu hạng mục; có thể NULL.',
  `loai_co_so_vat_chat` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Loại hạng mục.',
  `ten_hang_muc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên cơ sở vật chất/thiết bị.',
  `so_luong` DECIMAL(12,2) NULL DEFAULT NULL COMMENT 'Số lượng hoặc diện tích.',
  `don_vi_tinh` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Đơn vị đo.',
  `muc_dich_su_dung` TEXT NULL DEFAULT NULL COMMENT 'Công năng đào tạo.',
  `nam_thong_ke` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm ghi nhận.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú bổ sung.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_co_so_vat_chat_de_an_id` (`de_an_id`),
  KEY `idx_dats_co_so_vat_chat_co_so_id` (`co_so_id`),
  CONSTRAINT `fk_dats_co_so_vat_chat_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_co_so_vat_chat_co_so_id` FOREIGN KEY (`co_so_id`) REFERENCES `dats_tru_so` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cơ sở vật chất phục vụ đào tạo';

-- Quy mô người học theo năm, trình độ và hình thức đào tạo
CREATE TABLE IF NOT EXISTS `dats_quy_mo_dao_tao` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình cụ thể; NULL nếu toàn trường.',
  `trinh_do_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Trình độ đào tạo.',
  `hinh_thuc_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Hình thức đào tạo.',
  `nam_thong_ke` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm thống kê.',
  `so_luong_nguoi_hoc` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Quy mô người học.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Phạm vi/cách thống kê.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_quy_mo_dao_tao_de_an_id` (`de_an_id`),
  KEY `idx_dats_quy_mo_dao_tao_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  CONSTRAINT `fk_dats_quy_mo_dao_tao_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_mo_dao_tao_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Quy mô người học theo năm, trình độ và hình thức đào tạo';

-- Tỷ lệ việc làm của người học sau tốt nghiệp
CREATE TABLE IF NOT EXISTS `dats_ty_le_viec_lam` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án công bố số liệu.',
  `nganh_dao_tao_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Ngành thống kê; NULL nếu tổng hợp.',
  `trinh_do_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Trình độ khóa tốt nghiệp.',
  `nam_tot_nghiep` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm tốt nghiệp.',
  `thoi_diem_khao_sat_thang` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Số tháng sau tốt nghiệp khi khảo sát.',
  `so_nguoi_tot_nghiep` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổng số người tốt nghiệp trong mẫu/khóa.',
  `so_nguoi_co_viec_lam` INT UNSIGNED NULL DEFAULT NULL COMMENT 'Số người có việc làm theo khảo sát.',
  `ty_le_co_viec_lam` DECIMAL(5,2) NULL DEFAULT NULL COMMENT 'Tỷ lệ có việc làm theo %.',
  `phuong_phap_khao_sat` TEXT NULL DEFAULT NULL COMMENT 'Cách thu thập kết quả.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL nguồn công bố.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_ty_le_viec_lam_de_an_id` (`de_an_id`),
  KEY `idx_dats_ty_le_viec_lam_nganh_dao_tao_id` (`nganh_dao_tao_id`),
  CONSTRAINT `chk_dats_ty_le_viec_lam_ty_le_co_viec_lam` CHECK (ty_le_co_viec_lam IS NULL OR (ty_le_co_viec_lam BETWEEN 0 AND 100)),
  CONSTRAINT `fk_dats_ty_le_viec_lam_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_ty_le_viec_lam_nganh_dao_tao_id` FOREIGN KEY (`nganh_dao_tao_id`) REFERENCES `dm_nganh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tỷ lệ việc làm của người học sau tốt nghiệp';

-- Trình độ và hình thức đào tạo gắn với chương trình
CREATE TABLE IF NOT EXISTS `dats_trinh_do_nganh` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NOT NULL COMMENT 'Chương trình thuộc đề án.',
  `trinh_do_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Trình độ.',
  `hinh_thuc_dao_tao` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Hình thức.',
  `thoi_gian_dao_tao_nam` DECIMAL(4,1) NULL DEFAULT NULL COMMENT 'Thời lượng chương trình.',
  `ma_nganh_chuan` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Mã ngành chuẩn tại thời điểm đề án.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_trinh_do_nganh_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  CONSTRAINT `fk_dats_trinh_do_nganh_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Trình độ và hình thức đào tạo gắn với chương trình';

-- Nhóm thí sinh được phép dự tuyển
CREATE TABLE IF NOT EXISTS `dats_doi_tuong_du_tuyen` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án liên quan.',
  `ma_doi_tuong` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Mã nhóm đối tượng.',
  `ten_doi_tuong` VARCHAR(255) NOT NULL COMMENT 'Tên đối tượng dự tuyển.',
  `mo_ta` TEXT NULL DEFAULT NULL COMMENT 'Phạm vi đối tượng.',
  `nam_tot_nghiep_tu` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm tốt nghiệp tối thiểu nếu giới hạn.',
  `nam_tot_nghiep_den` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm tốt nghiệp tối đa; NULL nếu không giới hạn.',
  `pham_vi_ap_dung` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Toàn đề án hoặc một chương trình.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình áp dụng; có thể NULL.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái bản ghi.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú/ngoại lệ.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_doi_tuong_du_tuyen_de_an_id` (`de_an_id`),
  KEY `idx_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  CONSTRAINT `fk_dats_doi_tuong_du_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Nhóm thí sinh được phép dự tuyển';

-- Điều kiện cần đáp ứng để dự tuyển
CREATE TABLE IF NOT EXISTS `dats_dieu_kien_du_tuyen` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `doi_tuong_du_tuyen_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Đối tượng chịu điều kiện; có thể NULL.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình áp dụng; có thể NULL.',
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức áp dụng; có thể NULL.',
  `ma_dieu_kien` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã tiêu chí.',
  `ten_dieu_kien` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên điều kiện.',
  `loai_dieu_kien` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Nhóm điều kiện.',
  `noi_dung_dieu_kien` TEXT NULL DEFAULT NULL COMMENT 'Nội dung đầy đủ.',
  `toan_tu_so_sanh` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Toán tử điều kiện số.',
  `gia_tri_dieu_kien` JSON NULL DEFAULT NULL COMMENT 'Giá trị có cấu trúc.',
  `bat_buoc` BOOLEAN NULL DEFAULT NULL COMMENT 'Điều kiện bắt buộc hay không.',
  `minh_chung_can_nop` TEXT NULL DEFAULT NULL COMMENT 'Giấy tờ chứng minh.',
  `thu_tu_kiem_tra` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự kiểm tra.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL nguồn quy định.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_dieu_kien_du_tuyen_de_an_id` (`de_an_id`),
  KEY `idx_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  KEY `idx_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id` (`doi_tuong_du_tuyen_id`),
  CONSTRAINT `chk_dats_dieu_kien_du_tuyen_bat_buoc` CHECK (bat_buoc IS NULL OR bat_buoc IN (0,1)),
  CONSTRAINT `fk_dats_dieu_kien_du_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id` FOREIGN KEY (`doi_tuong_du_tuyen_id`) REFERENCES `dats_doi_tuong_du_tuyen` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Điều kiện cần đáp ứng để dự tuyển';

-- Tiêu chí chính, tiêu chí phụ và thứ tự xét
CREATE TABLE IF NOT EXISTS `dats_tieu_chi_xet_tuyen` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình; NULL nếu chung.',
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức; NULL nếu chung.',
  `ma_tieu_chi` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã tiêu chí.',
  `ten_tieu_chi` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên tiêu chí.',
  `loai_tieu_chi` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Chính/phụ/loại trừ.',
  `thu_tu_ap_dung` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự xét tiêu chí.',
  `toan_tu_so_sanh` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Toán tử nếu có ngưỡng số.',
  `gia_tri_tieu_chi` JSON NULL DEFAULT NULL COMMENT 'Ngưỡng/giá trị tiêu chí.',
  `noi_dung_tieu_chi` TEXT NULL DEFAULT NULL COMMENT 'Mô tả đầy đủ tiêu chí.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL nguồn.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_tieu_chi_xet_tuyen_de_an_id` (`de_an_id`),
  KEY `idx_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  CONSTRAINT `fk_dats_tieu_chi_xet_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Tiêu chí chính, tiêu chí phụ và thứ tự xét';

-- Điểm thưởng, điểm xét thưởng và điểm khuyến khích
CREATE TABLE IF NOT EXISTS `dats_diem_cong` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình; NULL nếu chung.',
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức; NULL nếu chung.',
  `loai_diem_cong` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Điểm thưởng/xét thưởng/khuyến khích.',
  `ma_doi_tuong_cong` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã thành tích/chứng chỉ được cộng.',
  `doi_tuong_duoc_cong` TEXT NULL DEFAULT NULL COMMENT 'Mô tả đối tượng.',
  `dieu_kien_ap_dung` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện chi tiết.',
  `diem_cong` DECIMAL(6,3) NULL DEFAULT NULL COMMENT 'Mức điểm được cộng.',
  `thang_diem` DECIMAL(6,2) NULL DEFAULT NULL COMMENT 'Thang điểm áp dụng.',
  `muc_diem_cong_toi_da` DECIMAL(6,3) NULL DEFAULT NULL COMMENT 'Mức cộng tối đa.',
  `co_cong_don` BOOLEAN NULL DEFAULT NULL COMMENT 'Có cộng dồn quyền lợi không.',
  `quy_tac_ket_hop` TEXT NULL DEFAULT NULL COMMENT 'Xử lý nhiều diện cùng lúc.',
  `nam_tuyen_sinh` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm áp dụng.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL nguồn.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái quy tắc.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_diem_cong_de_an_id` (`de_an_id`),
  KEY `idx_dats_diem_cong_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_diem_cong_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  CONSTRAINT `chk_dats_diem_cong_co_cong_don` CHECK (co_cong_don IS NULL OR co_cong_don IN (0,1)),
  CONSTRAINT `fk_dats_diem_cong_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_diem_cong_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_diem_cong_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Điểm thưởng, điểm xét thưởng và điểm khuyến khích';

-- Quy tắc phân bổ thí sinh vào ngành/chương trình
CREATE TABLE IF NOT EXISTS `dats_quy_tac_phan_bo` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình; NULL nếu chung.',
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức; NULL nếu chung.',
  `kieu_phan_bo` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Cách phân bổ thí sinh.',
  `thu_tu_uu_tien` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Thứ tự ưu tiên.',
  `quy_tac_xu_ly_dong_diem` TEXT NULL DEFAULT NULL COMMENT 'Xử lý bằng điểm tại ranh giới chỉ tiêu.',
  `quy_tac_chuyen_chi_tieu` TEXT NULL DEFAULT NULL COMMENT 'Cách xử lý chỉ tiêu dư/điều chỉnh.',
  `noi_dung_quy_tac` TEXT NULL DEFAULT NULL COMMENT 'Nội dung quy tắc phân bổ.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL nguồn.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_quy_tac_phan_bo_de_an_id` (`de_an_id`),
  KEY `idx_dats_quy_tac_phan_bo_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_quy_tac_phan_bo_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  CONSTRAINT `fk_dats_quy_tac_phan_bo_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_tac_phan_bo_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_tac_phan_bo_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Quy tắc phân bổ thí sinh vào ngành/chương trình';

-- Giấy tờ và minh chứng thí sinh cần nộp
CREATE TABLE IF NOT EXISTS `dats_ho_so_du_tuyen` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình; có thể NULL.',
  `de_an_phuong_thuc_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức; có thể NULL.',
  `ten_giay_to` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên giấy tờ/minh chứng.',
  `doi_tuong_phai_nop` TEXT NULL DEFAULT NULL COMMENT 'Đối tượng cần nộp giấy tờ.',
  `bat_buoc` BOOLEAN NULL DEFAULT NULL COMMENT 'Có bắt buộc nộp không.',
  `hinh_thuc_nop` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Cách nộp hồ sơ.',
  `thoi_han_nop` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Hạn nộp hồ sơ.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Yêu cầu/lưu ý.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_ho_so_du_tuyen_de_an_id` (`de_an_id`),
  KEY `idx_dats_ho_so_du_tuyen_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_ho_so_du_tuyen_de_an_phuong_thuc_id` (`de_an_phuong_thuc_id`),
  CONSTRAINT `chk_dats_ho_so_du_tuyen_bat_buoc` CHECK (bat_buoc IS NULL OR bat_buoc IN (0,1)),
  CONSTRAINT `fk_dats_ho_so_du_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_ho_so_du_tuyen_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_ho_so_du_tuyen_de_an_phuong_thuc_id` FOREIGN KEY (`de_an_phuong_thuc_id`) REFERENCES `dats_phuong_thuc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Giấy tờ và minh chứng thí sinh cần nộp';

-- Quy đổi ngưỡng đầu vào giữa phương thức/tổ hợp
CREATE TABLE IF NOT EXISTS `dats_quy_doi_nguong_dau_vao` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình áp dụng.',
  `nam_tuyen_sinh` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm tuyển sinh.',
  `phuong_thuc_nguon_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức nguồn.',
  `to_hop_nguon_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổ hợp nguồn; NULL nếu không dùng.',
  `phuong_thuc_dich_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức đích.',
  `to_hop_dich_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổ hợp đích; NULL nếu không dùng.',
  `diem_moc_nguon` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Mốc ngưỡng đầu vào nguồn.',
  `diem_moc_dich` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Ngưỡng tương đương đích.',
  `do_lech_diem` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Điểm đích trừ điểm nguồn.',
  `thang_diem_nguon` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Thang điểm nguồn tối đa.',
  `thang_diem_dich` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Thang điểm đích tối đa.',
  `cong_thuc_noi_suy` TEXT NULL DEFAULT NULL COMMENT 'Công thức giữa các mốc.',
  `dieu_kien_ap_dung` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện/phạm vi áp dụng.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL bảng quy đổi gốc.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái quy tắc.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_de_an_id_nam_tuyen_sinh` (`de_an_id`, `nam_tuyen_sinh`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_phuong_thuc_nguon_id` (`phuong_thuc_nguon_id`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_phuong_thuc_dich_id` (`phuong_thuc_dich_id`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_to_hop_nguon_id` (`to_hop_nguon_id`),
  KEY `idx_dats_quy_doi_nguong_dau_vao_to_hop_dich_id` (`to_hop_dich_id`),
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_phuong_thuc_nguon_id` FOREIGN KEY (`phuong_thuc_nguon_id`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_phuong_thuc_dich_id` FOREIGN KEY (`phuong_thuc_dich_id`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_to_hop_nguon_id` FOREIGN KEY (`to_hop_nguon_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_nguong_dau_vao_to_hop_dich_id` FOREIGN KEY (`to_hop_dich_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Quy đổi ngưỡng đầu vào giữa phương thức/tổ hợp';

-- Quy đổi điểm trúng tuyển giữa phương thức/tổ hợp
CREATE TABLE IF NOT EXISTS `dats_quy_doi_diem_trung_tuyen` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính.',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án áp dụng.',
  `de_an_chuong_trinh_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Chương trình áp dụng.',
  `nam_tuyen_sinh` SMALLINT UNSIGNED NULL DEFAULT NULL COMMENT 'Năm tuyển sinh.',
  `phuong_thuc_nguon_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức nguồn.',
  `to_hop_nguon_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổ hợp nguồn; NULL nếu không dùng.',
  `phuong_thuc_dich_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Phương thức đích.',
  `to_hop_dich_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'Tổ hợp đích; NULL nếu không dùng.',
  `diem_moc_nguon` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Mốc điểm trúng tuyển nguồn.',
  `diem_moc_dich` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Mốc điểm tương đương đích.',
  `do_lech_diem` DECIMAL(7,3) NULL DEFAULT NULL COMMENT 'Điểm đích trừ điểm nguồn.',
  `thang_diem_nguon` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Thang điểm nguồn tối đa.',
  `thang_diem_dich` DECIMAL(7,2) NULL DEFAULT NULL COMMENT 'Thang điểm đích tối đa.',
  `cong_thuc_noi_suy` TEXT NULL DEFAULT NULL COMMENT 'Công thức nội suy giữa các mốc.',
  `dieu_kien_ap_dung` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện/phạm vi áp dụng.',
  `nguon_du_lieu_url` VARCHAR(1000) NULL DEFAULT NULL COMMENT 'URL bảng quy đổi gốc.',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái quy tắc.',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Ghi chú.',
  PRIMARY KEY (`id`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_de_an_id_nam_tuyen_sinh` (`de_an_id`, `nam_tuyen_sinh`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id` (`de_an_chuong_trinh_id`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id` (`phuong_thuc_nguon_id`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id` (`phuong_thuc_dich_id`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id` (`to_hop_nguon_id`),
  KEY `idx_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id` (`to_hop_dich_id`),
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id` FOREIGN KEY (`de_an_chuong_trinh_id`) REFERENCES `dats_chuong_trinh_dao_tao` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id` FOREIGN KEY (`phuong_thuc_nguon_id`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id` FOREIGN KEY (`phuong_thuc_dich_id`) REFERENCES `dm_phuong_thuc_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id` FOREIGN KEY (`to_hop_nguon_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id` FOREIGN KEY (`to_hop_dich_id`) REFERENCES `dm_to_hop_mon_hoc` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Quy đổi điểm trúng tuyển giữa phương thức/tổ hợp';

-- Chính sách xét tuyển thẳng của đề án
CREATE TABLE IF NOT EXISTS `dats_chinh_sach_xet_tuyen_thang` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính của chính sách',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án tuyển sinh áp dụng chính sách',
  `ma_chinh_sach` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã chính sách do trường quy định',
  `ten_chinh_sach` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên diện xét tuyển thẳng',
  `nhom_doi_tuong` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Nhóm đối tượng theo quy định',
  `can_cu_phap_ly` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Căn cứ điều, khoản, điểm',
  `mo_ta_doi_tuong` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện cụ thể để thuộc diện này',
  `mon_thi_linh_vuc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Môn thi, đề tài hoặc lĩnh vực thành tích',
  `cap_thi` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Cấp độ cuộc thi/thành tích',
  `muc_giai` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Giải thưởng yêu cầu',
  `thoi_han_thanh_tich_nam` SMALLINT NULL DEFAULT NULL COMMENT 'Số năm thành tích được tính đến thời điểm xét',
  `pham_vi_chuong_trinh` TEXT NULL DEFAULT NULL COMMENT 'Ngành/chương trình được áp dụng',
  `dieu_kien_phu` TEXT NULL DEFAULT NULL COMMENT 'Ngưỡng đầu vào hoặc điều kiện bổ sung của trường',
  `chi_tieu_tuyen_thang` INT NULL DEFAULT NULL COMMENT 'Số lượng tuyển theo diện này; để trống nếu không công bố riêng',
  `ho_so_minh_chung` TEXT NULL DEFAULT NULL COMMENT 'Giấy tờ thí sinh phải nộp',
  `thu_tu_tieu_chi_xet` TEXT NULL DEFAULT NULL COMMENT 'Thứ tự tiêu chí khi cần xếp hạng thí sinh',
  `tieu_chi_phu_khi_dong_diem` TEXT NULL DEFAULT NULL COMMENT 'Tiêu chí xử lý khi các thí sinh bằng điểm/đồng hạng',
  `nguyen_tac_khi_vuot_chi_tieu` TEXT NULL DEFAULT NULL COMMENT 'Cách xử lý khi số thí sinh đủ điều kiện vượt chỉ tiêu',
  `thoi_gian_nhan_ho_so` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Thời gian nhận hồ sơ',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái chính sách',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung',
  PRIMARY KEY (`id`),
  KEY `idx_dats_chinh_sach_xet_tuyen_thang_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_chinh_sach_xet_tuyen_thang_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Chính sách xét tuyển thẳng của đề án';

-- Chính sách ưu tiên xét tuyển của đề án
CREATE TABLE IF NOT EXISTS `dats_chinh_sach_uu_tien_xet_tuyen` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Khóa chính của chính sách',
  `de_an_id` BIGINT UNSIGNED NOT NULL COMMENT 'Đề án tuyển sinh áp dụng chính sách',
  `ma_chinh_sach` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Mã chính sách do trường quy định',
  `ten_chinh_sach` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Tên diện ưu tiên xét tuyển',
  `nhom_doi_tuong` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Nhóm đối tượng được ưu tiên',
  `can_cu_phap_ly` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Căn cứ điều, khoản, điểm',
  `mo_ta_doi_tuong` TEXT NULL DEFAULT NULL COMMENT 'Điều kiện cụ thể để được ưu tiên',
  `mon_thi_linh_vuc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Môn thi, đề tài hoặc lĩnh vực thành tích',
  `muc_giai` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Giải thưởng yêu cầu',
  `thoi_han_thanh_tich_nam` SMALLINT NULL DEFAULT NULL COMMENT 'Số năm thành tích được tính',
  `pham_vi_chuong_trinh` TEXT NULL DEFAULT NULL COMMENT 'Ngành/chương trình được áp dụng',
  `hinh_thuc_uu_tien` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Cách trường áp dụng ưu tiên',
  `loai_diem_cong` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Loại điểm cộng nếu áp dụng',
  `muc_diem_cong` DECIMAL(5,2) NULL DEFAULT NULL COMMENT 'Mức điểm cộng theo quy định của đề án',
  `dieu_kien_nguong_dau_vao` TEXT NULL DEFAULT NULL COMMENT 'Ngưỡng cần đạt trước khi được ưu tiên, nếu có',
  `chi_tieu_uu_tien` INT NULL DEFAULT NULL COMMENT 'Số lượng dự kiến dành cho diện này, nếu có',
  `thu_tu_tieu_chi_xet` TEXT NULL DEFAULT NULL COMMENT 'Thứ tự tiêu chí xếp hạng khi áp dụng ưu tiên',
  `tieu_chi_phu_khi_dong_diem` TEXT NULL DEFAULT NULL COMMENT 'Tiêu chí xử lý khi các thí sinh bằng điểm',
  `ho_so_minh_chung` TEXT NULL DEFAULT NULL COMMENT 'Giấy tờ thí sinh phải nộp',
  `thoi_gian_nhan_ho_so` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Thời gian nhận hồ sơ',
  `trang_thai` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Trạng thái chính sách',
  `ghi_chu` TEXT NULL DEFAULT NULL COMMENT 'Thông tin bổ sung',
  PRIMARY KEY (`id`),
  KEY `idx_dats_chinh_sach_uu_tien_xet_tuyen_de_an_id` (`de_an_id`),
  CONSTRAINT `fk_dats_chinh_sach_uu_tien_xet_tuyen_de_an_id` FOREIGN KEY (`de_an_id`) REFERENCES `dats_tuyen_sinh` (`id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Chính sách ưu tiên xét tuyển của đề án';

-- Kết thúc schema. File chỉ định nghĩa bảng, không tự thêm dữ liệu tuyển sinh.
-- Kiểm tra số bảng sau khi import:
-- SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN (...);
-- Có thể xem cấu trúc bằng: SHOW CREATE TABLE dats_tuyen_sinh;
