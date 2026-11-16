"""Tao cac bang quy tac xet tuyen tinh duoc (buoc 2.1 KE_HOACH_TRIEN_KHAI.md).

Theo docs/de-an-tuyen-sinh/01_schema.sql (phan A, C, D) va 03_du_lieu_danh_muc.sql. Khong tao thu tuc MySQL,
khong tao bang hs_* (giai doan 4) va bang ket qua danh gia (giai doan 3).

- dm_chi_so_xet_tuyen
- xt_bang_quy_doi, xt_bang_quy_doi_chi_tiet
- xt_cong_thuc, xt_cong_thuc_he_so_mon, xt_cong_thuc_thanh_phan
- xt_phuong_an, xt_nhom_dieu_kien, xt_dieu_kien, xt_diem_cong
- dats_hoc_phi
- xt_bo_tieu_chi, xt_tieu_chi_phu_hop, xt_muc_phu_hop
- xt_lich_su_import
Du lieu nen: chi so, chi tiet to hop mon (dung tu ds_mon_hoc), bo tieu chi mac dinh.

Revision ID: 20261117_0058
Revises: 20261117_0057
Create Date: 2026-11-17 14:00:00.000000
"""

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT

revision: str = "20261117_0058"
down_revision: Union[str, Sequence[str], None] = "20261117_0057"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BANG = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci", mysql_engine="InnoDB")
_TOAN_TU = sa.Enum(">=", ">", "=", "<=", "<", "!=", name="toan_tu")

# Thứ tự tạo; xóa theo thứ tự ngược lại.
_THU_TU = [
    "dm_chi_so_xet_tuyen",
    "xt_bang_quy_doi",
    "xt_bang_quy_doi_chi_tiet",
    "xt_cong_thuc",
    "xt_cong_thuc_he_so_mon",
    "xt_cong_thuc_thanh_phan",
    "xt_phuong_an",
    "xt_nhom_dieu_kien",
    "xt_dieu_kien",
    "xt_diem_cong",
    "dats_hoc_phi",
    "xt_bo_tieu_chi",
    "xt_tieu_chi_phu_hop",
    "xt_muc_phu_hop",
    "xt_lich_su_import",
]

CHI_SO = [
    ("DA_TOT_NGHIEP_THPT", "Đã tốt nghiệp THPT hoặc tương đương", None, "1 = có, 0 = chưa"),
    ("NAM_TOT_NGHIEP", "Năm tốt nghiệp THPT", None, "Năm, ví dụ 2026"),
    ("HE_CHUYEN", "Học hệ chuyên cả 3 năm THPT", None, "1 = có, 0 = không"),
    ("MON_CHUYEN", "Môn chuyên", "MON_HOC", "1 nếu đúng môn ở cột khoa"),
    ("TBC_LOP", "Điểm trung bình chung cả năm của một lớp", "LOP", "Thang 10; khoa = 10/11/12"),
    (
        "TBC_MIN_3_NAM",
        "Điểm trung bình chung thấp nhất trong 3 năm lớp 10, 11, 12",
        None,
        'Thang 10; chỉ có khi đủ cả 3 năm. Dùng cho điều kiện "từng năm đạt từ ..."',
    ),
    (
        "HOC_LUC_LOP",
        "Kết quả học tập cả năm của một lớp",
        "LOP",
        "4 = Tốt/Giỏi, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu",
    ),
    ("HOC_LUC_MIN_3_NAM", "Kết quả học tập thấp nhất trong 3 năm", None, "Như HOC_LUC_LOP; chỉ có khi đủ cả 3 năm"),
    (
        "REN_LUYEN_LOP",
        "Kết quả rèn luyện/hạnh kiểm cả năm của một lớp",
        "LOP",
        "4 = Tốt, 3 = Khá, 2 = Đạt/Trung bình, 1 = Chưa đạt/Yếu",
    ),
    (
        "REN_LUYEN_MIN_3_NAM",
        "Kết quả rèn luyện thấp nhất trong 3 năm",
        None,
        "Như REN_LUYEN_LOP; chỉ có khi đủ cả 3 năm",
    ),
    ("DIEM_THI_THPT", "Điểm thi tốt nghiệp THPT của một môn", "MON_HOC", "Thang 10"),
    (
        "DIEM_HOC_BA_TB",
        "Điểm học bạ trung bình cả năm lớp 10, 11, 12 của một môn",
        "MON_HOC",
        "Thang 10; chỉ có khi đủ cả 3 năm",
    ),
    ("DIEM_BAI_THI", "Điểm cao nhất của một bài thi ĐGNL/ĐGTD/SAT/ACT", "BAI_THI", "Theo thang gốc của bài thi"),
    (
        "DIEM_CHUNG_CHI",
        "Điểm cao nhất của một chứng chỉ còn hạn",
        "CHUNG_CHI",
        "Theo thang của chứng chỉ (VSTEP: số bậc)",
    ),
    ("CO_CHUNG_CHI", "Có chứng chỉ còn hạn (không xét điểm)", "CHUNG_CHI", "1 = có"),
    (
        "THANH_TICH",
        "Giải cao nhất của một loại thành tích",
        "THANH_TICH",
        "1 = Nhất/Vàng, 2 = Nhì/Bạc, 3 = Ba/Đồng, 4 = Khuyến khích/Tư, 9 = chỉ tham gia. "
        "Số càng nhỏ giải càng cao nên điều kiện viết dạng <=",
    ),
]

# Tổ hợp có hơn 3 môn trong ds_mon_hoc mà biết cách xếp vị trí: {mã tổ hợp: [(mã môn, vị trí, ghi chú)]}.
# Nhiều môn cùng vị trí = chọn một trong các môn đó (lấy môn điểm cao nhất).
TO_HOP_NHIEU_MON = {
    "K01": [
        ("TOAN", 1, None),
        ("VAN", 2, None),
        ("LY", 3, "Chọn một trong Lý/Hóa/Sinh/Tin"),
        ("HOA", 3, "Chọn một trong Lý/Hóa/Sinh/Tin"),
        ("SINH", 3, "Chọn một trong Lý/Hóa/Sinh/Tin"),
        ("TIN", 3, "Chọn một trong Lý/Hóa/Sinh/Tin"),
    ],
}

BO_TIEU_CHI = ("MAC_DINH_V1", "Bộ tiêu chí mặc định v1", "Điểm phù hợp = trung bình có trọng số của các tiêu chí có dữ liệu.")
TIEU_CHI = [
    ("KHA_NANG_TRUNG_TUYEN", 50, "Chênh lệch giữa điểm xét của học sinh và điểm chuẩn năm gần nhất"),
    ("NGANH", 25, "Chương trình thuộc ngành / nhóm ngành / lĩnh vực học sinh chọn"),
    ("HOC_PHI", 15, "Học phí so với ngân sách của gia đình"),
    ("VI_TRI", 10, "Cơ sở đào tạo ở tỉnh / vùng học sinh mong muốn"),
]
# (loại mốc, từ, đến, điểm, nhãn); chênh lệch = điểm xét - điểm chuẩn, cùng quy về thang 30.
MUC_PHU_HOP = [
    ("KHA_NANG_TRUNG_TUYEN", 2, None, 100, "An toàn"),
    ("KHA_NANG_TRUNG_TUYEN", 1, 2, 90, "Khả năng cao"),
    ("KHA_NANG_TRUNG_TUYEN", 0, 1, 75, "Vừa sức"),
    ("KHA_NANG_TRUNG_TUYEN", -1, 0, 50, "Cần cố gắng"),
    ("KHA_NANG_TRUNG_TUYEN", -2, -1, 25, "Thử thách"),
    ("KHA_NANG_TRUNG_TUYEN", None, -2, 5, "Rất khó"),
    ("TONG_HOP", 80, None, None, "Rất phù hợp"),
    ("TONG_HOP", 65, 80, None, "Phù hợp"),
    ("TONG_HOP", 50, 65, None, "Có thể cân nhắc"),
    ("TONG_HOP", None, 50, None, "Ít phù hợp"),
]


def _id() -> sa.Column:
    return sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True)


def _de_an_id(nullable: bool = False) -> sa.Column:
    return sa.Column("de_an_id", BIGINT(unsigned=True), nullable=nullable)


def _has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def _tao(table: str, *columns, **kwargs) -> None:
    """Tạo bảng nếu chưa có. MySQL không rollback được DDL nên chạy lại sau khi lỗi giữa chừng vẫn được."""
    if not _has_table(table):
        op.create_table(table, *columns, **kwargs)


def _tao_bang() -> None:
    _tao(
        "dm_chi_so_xet_tuyen",
        sa.Column("ma_chi_so", sa.String(50), primary_key=True, comment="Mã chỉ số, dùng trong điều kiện và điểm cộng."),
        sa.Column("ten_chi_so", sa.String(255), nullable=False),
        sa.Column(
            "kieu_khoa",
            sa.String(30),
            comment="Ý nghĩa cột khoa: MON_HOC, BAI_THI, CHUNG_CHI, THANH_TICH, LOP; NULL nếu không cần khóa.",
        ),
        sa.Column("y_nghia_gia_tri", sa.String(500), comment="Cách đọc giá trị số."),
        sa.Column("ghi_chu", sa.Text()),
        comment="Danh mục chỉ số (dữ kiện) của học sinh dùng để kiểm tra điều kiện xét tuyển",
        **_BANG,
    )

    _tao(
        "xt_bang_quy_doi",
        _id(),
        _de_an_id(),
        sa.Column("ma_bang", sa.String(50), nullable=False, comment="Mã bảng trong đề án."),
        sa.Column("ten_bang", sa.String(255), nullable=False),
        sa.Column("thang_diem_dich", sa.Numeric(6, 2), nullable=False, comment="Thang điểm sau quy đổi."),
        sa.Column("ghi_chu", sa.Text()),
        sa.UniqueConstraint("de_an_id", "ma_bang", name="uk_xt_bang_quy_doi"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_bang_quy_doi_de_an_id"),
        comment="Bảng quy đổi chứng chỉ/bài thi sang điểm xét",
        **_BANG,
    )
    _tao(
        "xt_bang_quy_doi_chi_tiet",
        _id(),
        sa.Column("bang_quy_doi_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("chung_chi_id", BIGINT(unsigned=True), comment="Chứng chỉ nguồn; FK dm_bang_cap_chung_chi.id."),
        sa.Column("bai_thi_id", BIGINT(unsigned=True), comment="Bài thi nguồn; mỗi dòng chỉ điền chứng chỉ HOẶC bài thi."),
        sa.Column("mon_hoc_id", sa.Integer(), comment="Môn ngoại ngữ mà chứng chỉ thay thế."),
        sa.Column("cap_do", sa.String(30), comment="Cấp độ phải khớp (N3, HSK4, B2...)."),
        sa.Column("diem_tu", sa.Numeric(8, 2), comment="Cận dưới (>=)."),
        sa.Column("diem_den", sa.Numeric(8, 2), comment="Cận trên (<=)."),
        sa.Column("diem_quy_doi", sa.Numeric(7, 3), nullable=False, comment="Điểm quy đổi tại diem_tu."),
        sa.Column(
            "he_so_noi_suy",
            sa.Numeric(12, 8),
            nullable=False,
            server_default="0",
            comment="Điểm quy đổi = diem_quy_doi + he_so_noi_suy * (điểm - diem_tu). 0 = bậc thang.",
        ),
        sa.Column(
            "dat_nguong",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
            comment="0: dưới ngưỡng bảo đảm chất lượng, không dùng để xét.",
        ),
        sa.Index("idx_xt_bang_quy_doi_chi_tiet_bang", "bang_quy_doi_id", "chung_chi_id"),
        sa.Index("idx_xt_bang_quy_doi_chi_tiet_bai_thi", "bang_quy_doi_id", "bai_thi_id"),
        sa.ForeignKeyConstraint(
            ["bang_quy_doi_id"], ["xt_bang_quy_doi.id"], name="fk_xt_bqd_ct_bang_quy_doi_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["chung_chi_id"], ["dm_bang_cap_chung_chi.id"], name="fk_xt_bqd_ct_chung_chi_id"),
        sa.ForeignKeyConstraint(["bai_thi_id"], ["dm_bai_thi_danh_gia.id"], name="fk_xt_bqd_ct_bai_thi_id"),
        sa.ForeignKeyConstraint(["mon_hoc_id"], ["dm_mon_hoc.id"], name="fk_xt_bqd_ct_mon_hoc_id"),
        comment="Các mức của bảng quy đổi (bậc thang hoặc nội suy tuyến tính)",
        **_BANG,
    )

    _tao(
        "xt_cong_thuc",
        _id(),
        _de_an_id(),
        sa.Column("ma_cong_thuc", sa.String(50), nullable=False, comment="Mã công thức trong đề án."),
        sa.Column("ten_cong_thuc", sa.String(255), nullable=False),
        sa.Column("ma_phuong_thuc_cua_bo", sa.String(20), nullable=False),
        sa.Column(
            "kieu_tinh",
            sa.Enum("TO_HOP_MON", "THANH_PHAN", "CHI_DIEU_KIEN", "THU_CONG", name="kieu_tinh"),
            nullable=False,
            comment="TO_HOP_MON: tổng có hệ số các môn; THANH_PHAN: tổng thành phần bài thi/chứng chỉ; "
            "CHI_DIEU_KIEN: chỉ xét điều kiện; THU_CONG: có điểm nhưng hệ thống chưa tự tính.",
        ),
        sa.Column("nguon_diem_mon", sa.Enum("THI_THPT", "HOC_BA", name="nguon_diem_mon")),
        sa.Column(
            "thay_ngoai_ngu",
            sa.Enum("KHONG", "DUOC_PHEP", "BAT_BUOC", name="thay_ngoai_ngu"),
            nullable=False,
            server_default="KHONG",
        ),
        sa.Column("bang_quy_doi_ngoai_ngu_id", BIGINT(unsigned=True)),
        sa.Column("thang_diem", sa.Numeric(6, 2), nullable=False, server_default="30"),
        sa.Column("he_so_nhan", sa.Numeric(12, 8), nullable=False, server_default="1"),
        sa.Column("nguong_tb_mon", sa.Numeric(4, 2)),
        sa.Column("nguong_thpt_to_hop", sa.Numeric(5, 2)),
        sa.Column("diem_san", sa.Numeric(7, 2), comment="Ngưỡng nhận hồ sơ tính trên điểm xét cuối cùng."),
        sa.Column("ap_dung_diem_cong", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ap_dung_uu_tien", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ty_le_diem_cong_toi_da", sa.Numeric(4, 3), nullable=False, server_default="0.1"),
        sa.Column("so_le_lam_tron", TINYINT(unsigned=True), nullable=False, server_default="2"),
        sa.Column("mo_ta_cong_thuc", sa.Text(), comment="Công thức nguyên văn để hiển thị/đối chiếu."),
        sa.Column("trang_thai", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ghi_chu", sa.Text()),
        sa.UniqueConstraint("de_an_id", "ma_cong_thuc", name="uk_xt_cong_thuc"),
        sa.Index("idx_xt_cong_thuc_ma_phuong_thuc", "ma_phuong_thuc_cua_bo"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_cong_thuc_de_an_id"),
        sa.ForeignKeyConstraint(
            ["ma_phuong_thuc_cua_bo"],
            ["dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc"],
            name="fk_xt_cong_thuc_ma_phuong_thuc",
        ),
        sa.ForeignKeyConstraint(
            ["bang_quy_doi_ngoai_ngu_id"], ["xt_bang_quy_doi.id"], name="fk_xt_cong_thuc_bang_quy_doi"
        ),
        comment="Công thức tính điểm xét tuyển của đề án",
        **_BANG,
    )
    _tao(
        "xt_cong_thuc_he_so_mon",
        _id(),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("mon_hoc_id", sa.Integer(), comment="Môn được nhân hệ số; NULL nếu áp theo nhóm môn."),
        sa.Column("nhom_mon", sa.String(50), comment="Áp cho mọi môn thuộc nhóm (ví dụ Ngoại ngữ)."),
        sa.Column("he_so", sa.Numeric(6, 3), nullable=False),
        sa.Index("idx_xt_cong_thuc_he_so_mon", "cong_thuc_id", "mon_hoc_id"),
        sa.ForeignKeyConstraint(
            ["cong_thuc_id"], ["xt_cong_thuc.id"], name="fk_xt_cthsm_cong_thuc_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["mon_hoc_id"], ["dm_mon_hoc.id"], name="fk_xt_cthsm_mon_hoc_id"),
        comment="Hệ số môn của công thức kiểu TO_HOP_MON",
        **_BANG,
    )
    _tao(
        "xt_cong_thuc_thanh_phan",
        _id(),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "vi_tri",
            TINYINT(unsigned=True),
            nullable=False,
            comment="Thứ tự thành phần; các dòng cùng vị trí thay thế nhau, lấy giá trị cao nhất.",
        ),
        sa.Column("ten_thanh_phan", sa.String(255)),
        sa.Column("loai_nguon", sa.Enum("BAI_THI", "CHUNG_CHI", name="loai_nguon"), nullable=False),
        sa.Column("bai_thi_id", BIGINT(unsigned=True)),
        sa.Column("bang_quy_doi_id", BIGINT(unsigned=True)),
        sa.Column("mon_hoc_id", sa.Integer(), comment="CHUNG_CHI: chỉ nhận chứng chỉ của ngoại ngữ này."),
        sa.Column("he_so", sa.Numeric(6, 3), nullable=False, server_default="1"),
        sa.Column("nam_thi_tu", SMALLINT(unsigned=True)),
        sa.Column("nam_thi_den", SMALLINT(unsigned=True)),
        sa.Column("yeu_cau_phan_tu_chon", sa.String(50)),
        sa.Index("idx_xt_cong_thuc_thanh_phan", "cong_thuc_id", "vi_tri"),
        sa.ForeignKeyConstraint(
            ["cong_thuc_id"], ["xt_cong_thuc.id"], name="fk_xt_cttp_cong_thuc_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["bai_thi_id"], ["dm_bai_thi_danh_gia.id"], name="fk_xt_cttp_bai_thi_id"),
        sa.ForeignKeyConstraint(["bang_quy_doi_id"], ["xt_bang_quy_doi.id"], name="fk_xt_cttp_bang_quy_doi_id"),
        sa.ForeignKeyConstraint(["mon_hoc_id"], ["dm_mon_hoc.id"], name="fk_xt_cttp_mon_hoc_id"),
        comment="Thành phần điểm của công thức kiểu THANH_PHAN",
        **_BANG,
    )

    _tao(
        "xt_phuong_an",
        _id(),
        _de_an_id(),
        sa.Column("de_an_chuong_trinh_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("de_an_phuong_thuc_id", BIGINT(unsigned=True)),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("to_hop_id", sa.Integer(), comment="Bắt buộc với công thức TO_HOP_MON."),
        sa.Column("trang_thai", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ghi_chu", sa.Text()),
        sa.UniqueConstraint("de_an_chuong_trinh_id", "cong_thuc_id", "to_hop_id", name="uk_xt_phuong_an"),
        sa.Index("idx_xt_phuong_an_de_an_id", "de_an_id"),
        sa.Index("idx_xt_phuong_an_cong_thuc_id", "cong_thuc_id"),
        sa.Index("idx_xt_phuong_an_to_hop_id", "to_hop_id"),
        sa.Index("idx_xt_phuong_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_phuong_an_de_an_id"),
        sa.ForeignKeyConstraint(
            ["de_an_chuong_trinh_id"], ["dats_chuong_trinh_dao_tao.id"], name="fk_xt_phuong_an_chuong_trinh_id"
        ),
        sa.ForeignKeyConstraint(["de_an_phuong_thuc_id"], ["dats_phuong_thuc.id"], name="fk_xt_phuong_an_phuong_thuc_id"),
        sa.ForeignKeyConstraint(["cong_thuc_id"], ["xt_cong_thuc.id"], name="fk_xt_phuong_an_cong_thuc_id"),
        sa.ForeignKeyConstraint(["to_hop_id"], ["dm_to_hop_mon_hoc.id"], name="fk_xt_phuong_an_to_hop_id"),
        comment="Phương án xét tuyển = chương trình x công thức x tổ hợp",
        **_BANG,
    )
    _tao(
        "xt_nhom_dieu_kien",
        _id(),
        _de_an_id(),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), comment="NULL = mọi công thức của đề án."),
        sa.Column("de_an_chuong_trinh_id", BIGINT(unsigned=True), comment="NULL = mọi chương trình."),
        sa.Column("ma_nhom", sa.String(50), nullable=False),
        sa.Column("ten_nhom", sa.String(255), nullable=False, comment="Tên ngắn, dùng làm lý do khi không đạt."),
        sa.Column("mo_ta", sa.Text(), comment="Nguyên văn điều kiện trong đề án."),
        sa.Column("bat_buoc", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Index("idx_xt_nhom_dieu_kien_de_an", "de_an_id", "cong_thuc_id", "de_an_chuong_trinh_id"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_ndk_de_an_id"),
        sa.ForeignKeyConstraint(["cong_thuc_id"], ["xt_cong_thuc.id"], name="fk_xt_ndk_cong_thuc_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["de_an_chuong_trinh_id"], ["dats_chuong_trinh_dao_tao.id"], name="fk_xt_ndk_chuong_trinh_id"
        ),
        comment="Nhóm điều kiện dự tuyển; các nhóm áp dụng cho một phương án phải cùng đạt (AND)",
        **_BANG,
    )
    _tao(
        "xt_dieu_kien",
        _id(),
        sa.Column("nhom_dieu_kien_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("ma_chi_so", sa.String(50), nullable=False),
        sa.Column("khoa", sa.String(50), nullable=False, server_default=""),
        sa.Column("toan_tu", _TOAN_TU, nullable=False),
        sa.Column("gia_tri_so", sa.Numeric(12, 3), nullable=False),
        sa.Column("mo_ta", sa.String(500)),
        sa.Index("idx_xt_dieu_kien_nhom", "nhom_dieu_kien_id"),
        sa.Index("idx_xt_dieu_kien_chi_so", "ma_chi_so", "khoa"),
        sa.ForeignKeyConstraint(
            ["nhom_dieu_kien_id"], ["xt_nhom_dieu_kien.id"], name="fk_xt_dk_nhom_dieu_kien_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["ma_chi_so"], ["dm_chi_so_xet_tuyen.ma_chi_so"], name="fk_xt_dk_ma_chi_so"),
        comment="Điều kiện đơn; trong một nhóm chỉ cần một điều kiện đạt (OR)",
        **_BANG,
    )
    _tao(
        "xt_diem_cong",
        _id(),
        _de_an_id(),
        sa.Column("cong_thuc_id", BIGINT(unsigned=True), comment="NULL = mọi công thức có ap_dung_diem_cong."),
        sa.Column(
            "loai_diem_cong",
            sa.Enum("DIEM_THUONG", "DIEM_XET_THUONG", "DIEM_KHUYEN_KHICH", name="loai_diem_cong"),
            nullable=False,
        ),
        sa.Column("nhom_cong", sa.String(50), nullable=False, comment="Cùng nhóm lấy mức cao nhất; khác nhóm cộng dồn."),
        sa.Column("ma_chi_so", sa.String(50), nullable=False),
        sa.Column("khoa", sa.String(50), nullable=False, server_default=""),
        sa.Column("toan_tu", _TOAN_TU, nullable=False),
        sa.Column("gia_tri_so", sa.Numeric(12, 3), nullable=False),
        sa.Column("diem_cong", sa.Numeric(5, 2), nullable=False, comment="Mức cộng trên thang 30."),
        sa.Column("mo_ta", sa.String(500)),
        sa.Index("idx_xt_diem_cong_de_an", "de_an_id", "cong_thuc_id"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_diem_cong_de_an_id"),
        sa.ForeignKeyConstraint(
            ["cong_thuc_id"], ["xt_cong_thuc.id"], name="fk_xt_diem_cong_cong_thuc_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["ma_chi_so"], ["dm_chi_so_xet_tuyen.ma_chi_so"], name="fk_xt_diem_cong_ma_chi_so"),
        comment="Quy tắc điểm cộng (thưởng, xét thưởng, khuyến khích) có cấu trúc",
        **_BANG,
    )

    _tao(
        "dats_hoc_phi",
        _id(),
        _de_an_id(),
        sa.Column("de_an_chuong_trinh_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("nam_hoc", sa.String(20), comment="Ví dụ 2026-2027."),
        sa.Column("hoc_phi_tu", sa.Numeric(15, 0), nullable=False, comment="VNĐ/năm, mức thấp."),
        sa.Column("hoc_phi_den", sa.Numeric(15, 0), comment="VNĐ/năm, mức cao."),
        sa.Column("ghi_chu", sa.Text()),
        sa.Index("idx_dats_hoc_phi_chuong_trinh", "de_an_chuong_trinh_id"),
        sa.Index("idx_dats_hoc_phi_de_an_id", "de_an_id"),
        sa.ForeignKeyConstraint(["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_dats_hoc_phi_de_an_id"),
        sa.ForeignKeyConstraint(
            ["de_an_chuong_trinh_id"], ["dats_chuong_trinh_dao_tao.id"], name="fk_dats_hoc_phi_chuong_trinh_id"
        ),
        comment="Học phí dự kiến theo chương trình",
        **_BANG,
    )

    _tao(
        "xt_bo_tieu_chi",
        _id(),
        sa.Column("ma_bo", sa.String(50), nullable=False),
        sa.Column("ten_bo", sa.String(255), nullable=False),
        sa.Column("mac_dinh", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ghi_chu", sa.Text()),
        sa.UniqueConstraint("ma_bo", name="uk_xt_bo_tieu_chi_ma_bo"),
        comment="Bộ tiêu chí chấm điểm mức độ phù hợp",
        **_BANG,
    )
    _tao(
        "xt_tieu_chi_phu_hop",
        _id(),
        sa.Column("bo_tieu_chi_id", BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "ma_tieu_chi",
            sa.Enum("KHA_NANG_TRUNG_TUYEN", "NGANH", "HOC_PHI", "VI_TRI", name="ma_tieu_chi"),
            nullable=False,
        ),
        sa.Column("trong_so", sa.Numeric(5, 2), nullable=False, comment="Tiêu chí thiếu dữ liệu bị loại khỏi mẫu số."),
        sa.Column("mo_ta", sa.String(500)),
        sa.UniqueConstraint("bo_tieu_chi_id", "ma_tieu_chi", name="uk_xt_tieu_chi_phu_hop"),
        sa.ForeignKeyConstraint(
            ["bo_tieu_chi_id"], ["xt_bo_tieu_chi.id"], name="fk_xt_tcph_bo_tieu_chi_id", ondelete="CASCADE"
        ),
        comment="Trọng số từng tiêu chí phù hợp",
        **_BANG,
    )
    _tao(
        "xt_muc_phu_hop",
        _id(),
        sa.Column("bo_tieu_chi_id", BIGINT(unsigned=True), nullable=False),
        sa.Column("loai_muc", sa.Enum("KHA_NANG_TRUNG_TUYEN", "TONG_HOP", name="loai_muc"), nullable=False),
        sa.Column("gia_tri_tu", sa.Numeric(7, 2), comment="Cận dưới (>=); NULL = âm vô cùng."),
        sa.Column("gia_tri_den", sa.Numeric(7, 2), comment="Cận trên (<); NULL = dương vô cùng."),
        sa.Column("diem", sa.Numeric(5, 2), comment="Điểm 0-100 (với KHA_NANG_TRUNG_TUYEN)."),
        sa.Column("nhan", sa.String(50), nullable=False),
        sa.Index("idx_xt_muc_phu_hop", "bo_tieu_chi_id", "loai_muc"),
        sa.ForeignKeyConstraint(
            ["bo_tieu_chi_id"], ["xt_bo_tieu_chi.id"], name="fk_xt_mph_bo_tieu_chi_id", ondelete="CASCADE"
        ),
        comment="Các mốc quy đổi thành điểm/nhãn phù hợp",
        **_BANG,
    )

    _tao(
        "xt_lich_su_import",
        _id(),
        _de_an_id(),
        sa.Column("ten_file", sa.String(255)),
        sa.Column("ma_bam", sa.String(64), comment="SHA-256 nội dung file, để biết file nào đã được nạp."),
        sa.Column("phien_ban_chuan", sa.String(20), comment="Phiên bản chuẩn JSON của file."),
        sa.Column("so_dong", sa.JSON(), comment="Số dòng đã ghi theo bảng."),
        sa.Column("quy_dinh_chua_mo_hinh_hoa", sa.JSON(), comment="Quy định chưa tính được (phương án THU_CONG)."),
        sa.Column("nguoi_import_id", sa.Integer()),
        sa.Column("tao_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("ghi_chu", sa.Text()),
        sa.Index("idx_xt_lich_su_import_de_an", "de_an_id", "tao_luc"),
        sa.ForeignKeyConstraint(
            ["de_an_id"], ["dats_tuyen_sinh.id"], name="fk_xt_lsi_de_an_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["nguoi_import_id"], ["nguoi_dung.id"], name="fk_xt_lsi_nguoi_import_id", ondelete="SET NULL"
        ),
        comment="Nhật ký mỗi lần import quy tắc xét tuyển của đề án",
        **_BANG,
    )


def vi_tri_to_hop(ma_to_hop: str, ds_mon_hoc, id_mon: dict[str, int]) -> list[tuple[int, int, str | None]]:
    """Các dòng (mon_hoc_id, thu_tu_mon, ghi_chu) của một tổ hợp; [] nếu không dựng được đủ 3 vị trí."""
    if isinstance(ds_mon_hoc, str):
        try:
            ds_mon_hoc = json.loads(ds_mon_hoc)
        except ValueError:
            return []
    if ma_to_hop in TO_HOP_NHIEU_MON:
        dong = [(id_mon.get(ma), vi_tri, ghi_chu) for ma, vi_tri, ghi_chu in TO_HOP_NHIEU_MON[ma_to_hop]]
    elif isinstance(ds_mon_hoc, list) and len(ds_mon_hoc) == 3:
        dong = [(id_mon.get(str(ma)), vi_tri, None) for vi_tri, ma in enumerate(ds_mon_hoc, start=1)]
    else:
        return []
    dong = [d for d in dong if d[0] is not None]
    if len({vi_tri for _id, vi_tri, _ghi_chu in dong}) < 3:
        return []
    return dong


def _du_lieu_nen() -> None:
    bind = op.get_bind()
    co_chi_so = set(bind.execute(sa.text("SELECT ma_chi_so FROM dm_chi_so_xet_tuyen")).scalars())
    for ma, ten, kieu_khoa, y_nghia in CHI_SO:
        tham_so = {"ma": ma, "ten": ten, "kieu_khoa": kieu_khoa, "y_nghia": y_nghia}
        if ma in co_chi_so:
            bind.execute(
                sa.text(
                    "UPDATE dm_chi_so_xet_tuyen SET ten_chi_so = :ten, kieu_khoa = :kieu_khoa, "
                    "y_nghia_gia_tri = :y_nghia WHERE ma_chi_so = :ma"
                ),
                tham_so,
            )
        else:
            bind.execute(
                sa.text(
                    "INSERT INTO dm_chi_so_xet_tuyen (ma_chi_so, ten_chi_so, kieu_khoa, y_nghia_gia_tri) "
                    "VALUES (:ma, :ten, :kieu_khoa, :y_nghia)"
                ),
                tham_so,
            )

    # Chi tiết tổ hợp: chỉ dựng cho tổ hợp chưa có dòng nào, không đụng dữ liệu đã nhập tay.
    id_mon = {ma: mid for mid, ma in bind.execute(sa.text("SELECT id, ma_mon_hoc FROM dm_mon_hoc"))}
    da_co = set(bind.execute(sa.text("SELECT DISTINCT to_hop_id FROM dm_to_hop_mon_hoc_chi_tiet")).scalars())
    for to_hop_id, ma_to_hop, ds_mon_hoc in bind.execute(
        sa.text("SELECT id, ma_to_hop, ds_mon_hoc FROM dm_to_hop_mon_hoc")
    ):
        if to_hop_id in da_co:
            continue
        for mon_hoc_id, thu_tu, ghi_chu in vi_tri_to_hop(ma_to_hop, ds_mon_hoc, id_mon):
            bind.execute(
                sa.text(
                    "INSERT INTO dm_to_hop_mon_hoc_chi_tiet (to_hop_id, mon_hoc_id, thu_tu_mon, ghi_chu) "
                    "VALUES (:to_hop_id, :mon_hoc_id, :thu_tu, :ghi_chu)"
                ),
                {"to_hop_id": to_hop_id, "mon_hoc_id": mon_hoc_id, "thu_tu": thu_tu, "ghi_chu": ghi_chu},
            )

    ma_bo, ten_bo, ghi_chu_bo = BO_TIEU_CHI
    bo_id = bind.execute(sa.text("SELECT id FROM xt_bo_tieu_chi WHERE ma_bo = :ma"), {"ma": ma_bo}).scalar()
    if bo_id is not None:
        return
    bind.execute(
        sa.text("INSERT INTO xt_bo_tieu_chi (ma_bo, ten_bo, mac_dinh, ghi_chu) VALUES (:ma, :ten, 1, :ghi_chu)"),
        {"ma": ma_bo, "ten": ten_bo, "ghi_chu": ghi_chu_bo},
    )
    bo_id = bind.execute(sa.text("SELECT id FROM xt_bo_tieu_chi WHERE ma_bo = :ma"), {"ma": ma_bo}).scalar()
    for ma, trong_so, mo_ta in TIEU_CHI:
        bind.execute(
            sa.text(
                "INSERT INTO xt_tieu_chi_phu_hop (bo_tieu_chi_id, ma_tieu_chi, trong_so, mo_ta) "
                "VALUES (:bo, :ma, :trong_so, :mo_ta)"
            ),
            {"bo": bo_id, "ma": ma, "trong_so": trong_so, "mo_ta": mo_ta},
        )
    for loai, tu, den, diem, nhan in MUC_PHU_HOP:
        bind.execute(
            sa.text(
                "INSERT INTO xt_muc_phu_hop (bo_tieu_chi_id, loai_muc, gia_tri_tu, gia_tri_den, diem, nhan) "
                "VALUES (:bo, :loai, :tu, :den, :diem, :nhan)"
            ),
            {"bo": bo_id, "loai": loai, "tu": tu, "den": den, "diem": diem, "nhan": nhan},
        )


def upgrade() -> None:
    _tao_bang()
    _du_lieu_nen()


def downgrade() -> None:
    # Chi tiết tổ hợp là dữ liệu danh mục có sẵn từ trước, không xóa khi hạ cấp.
    for table in reversed(_THU_TU):
        if _has_table(table):
            op.drop_table(table)
