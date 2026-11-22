"""Nhóm nghề / nghề cụ thể đi làm: thêm hinh_anh_mo_ta; bổ sung nghề bắt buộc đào tạo chính quy.

- dm_nhom_nghe_di_lam, dm_nghe_cu_the_di_lam: hinh_anh_mo_ta (VARCHAR 500, null) — URL hình ảnh mô tả.
- Dữ liệu mẫu:
  - 2 nhóm mới gồm chủ yếu nghề bắt buộc đào tạo chính quy: pháp luật (luật sư, thẩm phán, kiểm sát viên…),
    kỹ sư - kiến trúc sư; kèm mục giới thiệu và điểm tiêu chí gợi ý.
  - Thêm nghề bắt buộc chính quy vào nhóm đã có: y tế, công an - quân đội, giáo dục, hàng không.
  - Ảnh mẫu là ảnh placeholder (placehold.co, ghi tên nhóm / nghề) cho mọi bản ghi đang trống ảnh; quản trị thay
    ảnh thật sau.
  Không ghi đè dữ liệu quản trị đã sửa; chạy lại được. Lương tính bằng triệu đồng/tháng, mang tính tham khảo.

Revision ID: 20261211_0084
Revises: 20261210_0083
Create Date: 2026-12-11 10:00:00.000000
"""

from urllib.parse import quote

import sqlalchemy as sa
from alembic import op

revision = "20261211_0084"
down_revision = "20261210_0083"
branch_labels = None
depends_on = None

COT_GIOI_THIEU = (
    "nganh_nay_la_gi",
    "noi_lam_viec_o_dau",
    "cong_viec_hang_ngay_nhu_the_nao",
    "ap_luc_va_rui_ro",
    "xu_huong_tuong_lai",
    "ket_luan",
)

# Nhóm nghề mới. Lương: khởi điểm min/max, có kinh nghiệm tối đa (triệu đồng/tháng).
NHOM_MOI = [
    dict(
        ma_nhom="PHAP_LUAT_TU_PHAP", ten_nhom="Pháp luật, tư pháp",
        mo_ta_dac_diem="Tư vấn, bảo vệ quyền lợi hợp pháp, xét xử, kiểm sát, công chứng và thi hành án. Hầu hết"
        " nghề phải có bằng cử nhân luật, qua đào tạo nghiệp vụ tại Học viện Tư pháp và được bổ nhiệm hoặc cấp"
        " chứng chỉ hành nghề.",
        loai_hinh_dau_vao=None,
        thoi_gian_dao_tao_text="Cử nhân luật 4 năm + đào tạo nghề, tập sự 1-2 năm",
        thoi_gian_dao_tao_thang_min=48, thoi_gian_dao_tao_thang_max=72,
        dieu_kien_dau_vao="Tốt nghiệp THPT, xét tuyển ngành Luật (thường khối C00, A00, D01); lý lịch rõ ràng,"
        " khả năng đọc hiểu, lập luận tốt.",
        muc_luong_text="7 - 12 triệu/tháng (mới ra trường)", luong_khoi_diem_min=7, luong_khoi_diem_max=12,
        luong_kinh_nghiem_max=60,
        danh_gia_trien_vong="Nhu cầu tư vấn pháp lý của doanh nghiệp và người dân tăng; luật sư giỏi thu nhập cao",
        lo_trinh_phat_trien="Cử nhân luật → Tập sự / thư ký → Luật sư, công chứng viên, thẩm tra viên → Luật sư"
        " điều hành, thẩm phán, kiểm sát viên cao cấp.",
        nhom_muc_tieu="thu_nhap_dot_pha", ma_holland="ES",
    ),
    dict(
        ma_nhom="KY_SU_KIEN_TRUC", ten_nhom="Kỹ sư, kiến trúc sư",
        mo_ta_dac_diem="Thiết kế, tính toán, giám sát công trình xây dựng, cầu đường, hệ thống điện, máy móc."
        " Kỹ sư, kiến trúc sư phải tốt nghiệp đại học chính quy; ký hồ sơ thiết kế, giám sát cần chứng chỉ hành"
        " nghề. Họa viên, đo đạc có thể học ngắn hạn để đi làm trước.",
        loai_hinh_dau_vao=None,
        thoi_gian_dao_tao_text="Kỹ sư 4-5 năm; họa viên CAD 3-6 tháng",
        thoi_gian_dao_tao_thang_min=3, thoi_gian_dao_tao_thang_max=60,
        dieu_kien_dau_vao="Tốt nghiệp THPT, học tốt Toán, Lý; kiến trúc thi thêm môn Vẽ mỹ thuật.",
        muc_luong_text="9 - 15 triệu/tháng (kỹ sư mới ra trường)", luong_khoi_diem_min=9, luong_khoi_diem_max=15,
        luong_kinh_nghiem_max=50,
        danh_gia_trien_vong="Ổn định nhờ đầu tư hạ tầng, đô thị, năng lượng; kỹ sư có chứng chỉ hành nghề rất cần",
        lo_trinh_phat_trien="Kỹ sư mới → Kỹ sư chính (có chứng chỉ hành nghề) → Chủ nhiệm thiết kế, chỉ huy"
        " trưởng → Giám đốc dự án.",
        nhom_muc_tieu="thu_nhap_dot_pha", ma_holland="RI",
    ),
]

GIOI_THIEU = {
    "PHAP_LUAT_TU_PHAP": (
        "Là những người dùng kiến thức pháp luật để tư vấn, bảo vệ quyền lợi cho người dân, doanh nghiệp và giữ"
        " gìn công lý: luật sư, thẩm phán, kiểm sát viên, công chứng viên, chấp hành viên…",
        "Văn phòng, công ty luật; tòa án, viện kiểm sát, cơ quan thi hành án; phòng, văn phòng công chứng; phòng"
        " pháp chế của doanh nghiệp, ngân hàng.",
        "Đọc và nghiên cứu hồ sơ, tra cứu văn bản pháp luật, gặp gỡ khách hàng, soạn thảo hợp đồng, đơn từ, tham gia"
        " phiên tòa, đàm phán, hòa giải.",
        "Khối lượng đọc viết lớn, áp lực thời hạn và trách nhiệm pháp lý; thời gian học và tập sự dài trước khi có"
        " thu nhập tốt; một số vụ việc căng thẳng.",
        "Kinh tế hội nhập làm tăng nhu cầu tư vấn đầu tư, sở hữu trí tuệ, công nghệ; người giỏi ngoại ngữ và luật"
        " quốc tế có lợi thế lớn.",
        "Hợp với người thích đọc, lập luận chặt chẽ, trung thực. Không đi làm ngay được: cần xác định học đại học"
        " Luật và kiên trì qua giai đoạn tập sự.",
    ),
    "KY_SU_KIEN_TRUC": (
        "Là những người thiết kế và tổ chức thi công công trình, hệ thống kỹ thuật: kiến trúc sư, kỹ sư xây dựng,"
        " cầu đường, điện, cơ khí.",
        "Công ty tư vấn thiết kế, nhà thầu xây dựng, ban quản lý dự án, nhà máy, công ty điện lực; văn phòng và"
        " công trường.",
        "Khảo sát, tính toán, vẽ bản vẽ trên phần mềm (AutoCAD, Revit…), lập dự toán, giám sát chất lượng thi công,"
        " xử lý sự cố kỹ thuật tại công trường.",
        "Trách nhiệm cao về an toàn công trình; làm ngoài công trường nắng mưa, đi xa; dự án gấp phải tăng ca;"
        " phải liên tục cập nhật tiêu chuẩn, phần mềm.",
        "Đầu tư hạ tầng, năng lượng tái tạo, đô thị thông minh mở nhiều việc; kỹ sư biết BIM, tiếng Anh dễ vào"
        " dự án quốc tế.",
        "Hợp với người giỏi Toán, Lý, thích sáng tạo kỹ thuật. Phải học đại học; nếu chưa học ngay có thể làm họa"
        " viên CAD để tích lũy kinh nghiệm.",
    ),
}

# Nghề: (tên, mô tả ngắn, yêu cầu thêm, yêu cầu bằng cấp, bắt buộc chính quy 1/None).
NGHE = {
    "PHAP_LUAT_TU_PHAP": [
        ("Luật sư", "Tư vấn pháp luật, soạn thảo hợp đồng, bào chữa và đại diện cho khách hàng trước tòa.",
         "Lập luận, giao tiếp tốt",
         "Cử nhân luật, chứng chỉ đào tạo nghề luật sư (Học viện Tư pháp), tập sự và chứng chỉ hành nghề", 1),
        ("Thẩm phán", "Xét xử các vụ án hình sự, dân sự, hành chính tại tòa án.", "Phẩm chất đạo đức tốt",
         "Cử nhân luật, đào tạo nghiệp vụ xét xử và được bổ nhiệm thẩm phán", 1),
        ("Kiểm sát viên", "Thực hành quyền công tố, kiểm sát hoạt động điều tra, xét xử.", "Phẩm chất đạo đức tốt",
         "Cử nhân luật, đào tạo nghiệp vụ kiểm sát và được bổ nhiệm kiểm sát viên", 1),
        ("Công chứng viên", "Chứng nhận hợp đồng, giao dịch (mua bán nhà đất, thừa kế…) đúng pháp luật.", "Cẩn thận",
         "Cử nhân luật, đào tạo nghề công chứng, tập sự và được bổ nhiệm công chứng viên", 1),
        ("Chấp hành viên thi hành án", "Tổ chức thi hành bản án, quyết định của tòa án.", None,
         "Cử nhân luật, đào tạo nghiệp vụ thi hành án và được bổ nhiệm chấp hành viên", 1),
        ("Thừa phát lại", "Tống đạt giấy tờ, lập vi bằng, xác minh điều kiện thi hành án.", None,
         "Cử nhân luật, đào tạo nghề thừa phát lại, tập sự và được bổ nhiệm", 1),
        ("Chuyên viên pháp chế doanh nghiệp", "Rà soát hợp đồng, tư vấn tuân thủ pháp luật cho doanh nghiệp.",
         "Ngoại ngữ là lợi thế", "Cử nhân luật", 1),
        ("Nhân viên hành chính văn phòng luật", "Tiếp khách, sắp xếp hồ sơ, nộp giấy tờ tại cơ quan nhà nước.",
         "Cẩn thận, tin học văn phòng", None, None),
    ],
    "KY_SU_KIEN_TRUC": [
        ("Kiến trúc sư", "Thiết kế nhà ở, công trình công cộng, quy hoạch không gian.", "Năng khiếu vẽ, thẩm mỹ",
         "Bằng kiến trúc sư (đại học); chứng chỉ hành nghề kiến trúc khi ký thiết kế", 1),
        ("Kỹ sư xây dựng", "Tính toán kết cấu, lập dự toán, chỉ huy và giám sát thi công công trình.",
         "Chịu được làm công trường", "Bằng kỹ sư xây dựng; chứng chỉ hành nghề hoạt động xây dựng khi giám sát, thiết kế",
         1),
        ("Kỹ sư cầu đường", "Thiết kế, thi công, giám sát cầu, đường bộ, đường cao tốc.", "Đi công trình xa",
         "Bằng kỹ sư cầu đường; chứng chỉ hành nghề hoạt động xây dựng", 1),
        ("Kỹ sư điện", "Thiết kế, vận hành hệ thống điện công nghiệp, trạm biến áp, điện mặt trời.", None,
         "Bằng kỹ sư điện (đại học)", 1),
        ("Kỹ sư cơ khí", "Thiết kế, chế tạo, bảo trì máy móc, dây chuyền sản xuất.", None,
         "Bằng kỹ sư cơ khí (đại học)", 1),
        ("Họa viên kiến trúc, kết cấu (vẽ CAD)", "Triển khai bản vẽ chi tiết theo thiết kế của kỹ sư, kiến trúc sư.",
         "Thành thạo AutoCAD, Revit", "Chứng chỉ khóa học AutoCAD / Revit (thường được yêu cầu)", None),
        ("Nhân viên đo đạc, trắc địa công trình", "Đo đạc, định vị tim mốc, cao độ cho công trình bằng máy toàn đạc.",
         "Chịu được làm ngoài trời", "Chứng chỉ sơ cấp / trung cấp trắc địa", None),
    ],
    "Y_TE_CHAM_SOC": [
        ("Bác sĩ răng hàm mặt", "Khám, điều trị, phục hình răng miệng.", "Khéo tay, học lực tốt khối Toán, Hóa, Sinh",
         "Bằng bác sĩ răng hàm mặt (đại học 6 năm) và giấy phép hành nghề", 1),
        ("Bác sĩ y học cổ truyền", "Khám, chữa bệnh bằng thuốc đông y, châm cứu, xoa bóp bấm huyệt.", None,
         "Bằng bác sĩ y học cổ truyền (đại học 6 năm) và giấy phép hành nghề", 1),
        ("Hộ sinh", "Chăm sóc bà mẹ khi mang thai, đỡ đẻ, chăm sóc trẻ sơ sinh.", "Kiên nhẫn, cẩn thận",
         "Bằng cao đẳng hộ sinh trở lên và giấy phép hành nghề", 1),
        ("Kỹ thuật viên chẩn đoán hình ảnh", "Chụp X-quang, CT, MRI, siêu âm theo chỉ định của bác sĩ.", None,
         "Bằng cao đẳng kỹ thuật hình ảnh y học trở lên và giấy phép hành nghề", 1),
        ("Kỹ thuật viên phục hồi chức năng", "Tập vật lý trị liệu, phục hồi vận động cho người bệnh.", "Sức khỏe tốt",
         "Bằng cao đẳng phục hồi chức năng trở lên và giấy phép hành nghề", 1),
    ],
    "AN_NINH_LUC_LUONG_VU_TRANG": [
        ("Bộ đội biên phòng", "Quản lý, bảo vệ biên giới, cửa khẩu, vùng biển.", "Sơ tuyển sức khỏe, lý lịch",
         "Bằng tốt nghiệp Học viện Biên phòng hoặc trường quân đội", 1),
        ("Cảnh sát biển", "Tuần tra, kiểm soát, thực thi pháp luật trên vùng biển.", "Bơi giỏi, sức khỏe rất tốt",
         "Bằng tốt nghiệp trường quân đội đào tạo cảnh sát biển, hải quân", 1),
        ("Cảnh sát giao thông", "Tuần tra, xử lý vi phạm, điều tiết giao thông.", "Sơ tuyển tại công an địa phương",
         "Bằng tốt nghiệp trường công an nhân dân (chuyên ngành cảnh sát)", 1),
        ("Điều tra viên", "Điều tra, thu thập chứng cứ các vụ án hình sự.", "Phẩm chất đạo đức, bản lĩnh",
         "Bằng tốt nghiệp trường công an nhân dân, đào tạo nghiệp vụ điều tra và được bổ nhiệm", 1),
    ],
    "GIAO_DUC_TRO_GIANG": [
        ("Giáo viên trung học cơ sở", "Dạy một môn học bậc THCS, chủ nhiệm lớp.", None,
         "Bằng cử nhân sư phạm (đại học) trở lên", 1),
        ("Giáo viên trung học phổ thông", "Dạy một môn học bậc THPT, ôn thi tốt nghiệp.", "Giỏi môn chuyên ngành",
         "Bằng cử nhân sư phạm đúng môn dạy (đại học) trở lên", 1),
        ("Giảng viên đại học", "Giảng dạy, hướng dẫn sinh viên và nghiên cứu khoa học.", "Nghiên cứu tốt",
         "Bằng thạc sĩ trở lên và chứng chỉ bồi dưỡng nghiệp vụ sư phạm", 1),
    ],
    "HANG_KHONG_HANG_HAI": [
        ("Kiểm soát viên không lưu", "Điều hành, cấp phép bay, giữ khoảng cách an toàn giữa các máy bay.",
         "Tiếng Anh rất tốt, phản xạ nhanh",
         "Bằng đại học quản lý hoạt động bay và giấy phép kiểm soát viên không lưu", 1),
    ],
}

TIEU_CHI = {
    "PHAP_LUAT_TU_PHAP": [
        ("THICH_GIAO_TIEP", 4, None), ("TU_HOC_TOT", 5, "Đọc, nghiên cứu văn bản nhiều"),
        ("MUON_ON_DINH", 4, None), ("MUON_TU_LAM_CHU", 3, "Mở văn phòng luật"),
    ],
    "KY_SU_KIEN_TRUC": [
        ("THICH_SANG_TAO", 4, None), ("THICH_CONG_NGHE", 4, "Phần mềm thiết kế"),
        ("TU_HOC_TOT", 5, "Học đại học 4-5 năm"), ("MUON_ON_DINH", 4, None),
    ],
}

_NHOM = sa.table(
    "dm_nhom_nghe_di_lam",
    sa.column("id", sa.Integer),
    sa.column("ma_nhom", sa.String),
    sa.column("ten_nhom", sa.String),
    sa.column("trang_thai", sa.Integer),
    sa.column("hinh_anh_mo_ta", sa.String),
    *[sa.column(ten) for ten in NHOM_MOI[0] if ten not in ("ma_nhom", "ten_nhom")],
    *[sa.column(ten, sa.Text) for ten in COT_GIOI_THIEU],
)
_NGHE = sa.table(
    "dm_nghe_cu_the_di_lam",
    sa.column("id", sa.Integer),
    sa.column("nhom_nghe_di_lam_id", sa.Integer),
    sa.column("ten_nghe", sa.String),
    sa.column("mo_ta_ngan", sa.Text),
    sa.column("yeu_cau_them", sa.String),
    sa.column("yeu_cau_bang_cap", sa.String),
    sa.column("bat_buoc_dao_tao_chinh_quy", sa.Integer),
    sa.column("hinh_anh_mo_ta", sa.String),
)
_TIEU_CHI = sa.table("dm_tieu_chi_goi_y", sa.column("id", sa.Integer), sa.column("ma_tieu_chi", sa.String))
_NHOM_TIEU_CHI = sa.table(
    "dm_nhom_nghe_tieu_chi",
    sa.column("nhom_nghe_di_lam_id", sa.Integer),
    sa.column("tieu_chi_goi_y_id", sa.Integer),
    sa.column("diem_phu_hop", sa.Integer),
    sa.column("ghi_chu", sa.String),
)


def anh_placeholder(ten: str) -> str:
    """URL ảnh placeholder 800x500 ghi tên nhóm / nghề (font Roboto hiển thị được tiếng Việt)."""
    return f"https://placehold.co/800x500/eaf5eb/2f7a33/png?font=roboto&text={quote(ten)}"


def _co_cot(bang: str, cot: str) -> bool:
    return cot in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(bang)}


def _id_nhom(conn) -> dict[str, int]:
    return {ma: id_ for id_, ma in conn.execute(sa.select(_NHOM.c.id, _NHOM.c.ma_nhom))}


def upgrade() -> None:
    for bang in ("dm_nhom_nghe_di_lam", "dm_nghe_cu_the_di_lam"):
        if not _co_cot(bang, "hinh_anh_mo_ta"):
            op.add_column(bang, sa.Column("hinh_anh_mo_ta", sa.String(500), nullable=True, comment="URL hình ảnh mô tả"))

    conn = op.get_bind()

    # Nhóm mới (bỏ qua nếu mã nhóm đã có).
    co_san = _id_nhom(conn)
    for nhom in NHOM_MOI:
        if nhom["ma_nhom"] not in co_san:
            conn.execute(_NHOM.insert().values(**nhom, trang_thai=1))
    id_nhom = _id_nhom(conn)

    # Mục giới thiệu: chỉ điền ô đang trống.
    for ma_nhom, gia_tri in GIOI_THIEU.items():
        if ma_nhom not in id_nhom:
            continue
        for cot, noi_dung in zip(COT_GIOI_THIEU, gia_tri, strict=True):
            conn.execute(
                _NHOM.update()
                .where(_NHOM.c.id == id_nhom[ma_nhom], _NHOM.c[cot].is_(None))
                .values({cot: noi_dung})
            )

    # Nghề cụ thể: thêm nếu chưa có (theo nhóm + tên), nghề đã có chỉ điền yêu cầu bằng cấp / chính quy còn trống.
    for ma_nhom, ds_nghe in NGHE.items():
        nhom_id = id_nhom.get(ma_nhom)
        if nhom_id is None:
            continue
        for ten, mo_ta, yeu_cau_them, bang_cap, chinh_quy in ds_nghe:
            nghe_id = conn.scalar(
                sa.select(_NGHE.c.id).where(_NGHE.c.nhom_nghe_di_lam_id == nhom_id, _NGHE.c.ten_nghe == ten)
            )
            if nghe_id is None:
                conn.execute(_NGHE.insert().values(
                    nhom_nghe_di_lam_id=nhom_id, ten_nghe=ten, mo_ta_ngan=mo_ta, yeu_cau_them=yeu_cau_them,
                    yeu_cau_bang_cap=bang_cap, bat_buoc_dao_tao_chinh_quy=chinh_quy,
                ))
                continue
            if bang_cap:
                conn.execute(_NGHE.update().where(_NGHE.c.id == nghe_id, _NGHE.c.yeu_cau_bang_cap.is_(None))
                             .values(yeu_cau_bang_cap=bang_cap))
            if chinh_quy:
                conn.execute(_NGHE.update().where(_NGHE.c.id == nghe_id, _NGHE.c.bat_buoc_dao_tao_chinh_quy.is_(None))
                             .values(bat_buoc_dao_tao_chinh_quy=chinh_quy))

    # Điểm tiêu chí gợi ý cho nhóm mới (bỏ qua tiêu chí không tồn tại hoặc cặp đã có).
    id_tieu_chi = {ma: id_ for id_, ma in conn.execute(sa.select(_TIEU_CHI.c.id, _TIEU_CHI.c.ma_tieu_chi))}
    for ma_nhom, ds in TIEU_CHI.items():
        nhom_id = id_nhom.get(ma_nhom)
        if nhom_id is None:
            continue
        for ma_tieu_chi, diem, ghi_chu in ds:
            tieu_chi_id = id_tieu_chi.get(ma_tieu_chi)
            if tieu_chi_id is None:
                continue
            da_co = conn.scalar(sa.select(sa.func.count()).select_from(_NHOM_TIEU_CHI).where(
                _NHOM_TIEU_CHI.c.nhom_nghe_di_lam_id == nhom_id, _NHOM_TIEU_CHI.c.tieu_chi_goi_y_id == tieu_chi_id,
            ))
            if not da_co:
                conn.execute(_NHOM_TIEU_CHI.insert().values(
                    nhom_nghe_di_lam_id=nhom_id, tieu_chi_goi_y_id=tieu_chi_id, diem_phu_hop=diem, ghi_chu=ghi_chu,
                ))

    # Ảnh placeholder cho mọi nhóm / nghề đang trống ảnh (kể cả bản ghi cũ).
    for id_, ten in conn.execute(sa.select(_NHOM.c.id, _NHOM.c.ten_nhom).where(_NHOM.c.hinh_anh_mo_ta.is_(None))).all():
        conn.execute(_NHOM.update().where(_NHOM.c.id == id_).values(hinh_anh_mo_ta=anh_placeholder(ten)))
    for id_, ten in conn.execute(sa.select(_NGHE.c.id, _NGHE.c.ten_nghe).where(_NGHE.c.hinh_anh_mo_ta.is_(None))).all():
        conn.execute(_NGHE.update().where(_NGHE.c.id == id_).values(hinh_anh_mo_ta=anh_placeholder(ten)))


def downgrade() -> None:
    conn = op.get_bind()
    id_nhom = _id_nhom(conn)
    ids_moi = [id_nhom[n["ma_nhom"]] for n in NHOM_MOI if n["ma_nhom"] in id_nhom]
    if ids_moi:
        conn.execute(_NHOM_TIEU_CHI.delete().where(_NHOM_TIEU_CHI.c.nhom_nghe_di_lam_id.in_(ids_moi)))
        conn.execute(_NGHE.delete().where(_NGHE.c.nhom_nghe_di_lam_id.in_(ids_moi)))
        conn.execute(_NHOM.delete().where(_NHOM.c.id.in_(ids_moi)))
    # Nghề thêm vào các nhóm đã có.
    ma_moi = {n["ma_nhom"] for n in NHOM_MOI}
    for ma_nhom, ds_nghe in NGHE.items():
        nhom_id = id_nhom.get(ma_nhom)
        if ma_nhom in ma_moi or nhom_id is None:
            continue
        conn.execute(_NGHE.delete().where(
            _NGHE.c.nhom_nghe_di_lam_id == nhom_id, _NGHE.c.ten_nghe.in_([ten for ten, *_ in ds_nghe])
        ))

    for bang in ("dm_nghe_cu_the_di_lam", "dm_nhom_nghe_di_lam"):
        if _co_cot(bang, "hinh_anh_mo_ta"):
            op.drop_column(bang, "hinh_anh_mo_ta")
