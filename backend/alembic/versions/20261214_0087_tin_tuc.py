"""Tạo bảng tin tức: nhóm tin (tin_tuc_nhom_tin) và bài viết (tin_tuc_bai_viet), kèm dữ liệu mẫu.

- tin_tuc_nhom_tin: id, ma_nhom (unique), ten_nhom, slug (unique), mo_ta, thu_tu, trang_thai (0 ẩn / 1 hiển thị),
  created_at, updated_at.
- tin_tuc_bai_viet: id, nhom_tin_tuc_id (FK → tin_tuc_nhom_tin.id, RESTRICT), tieu_de, slug (unique), tom_tat,
  noi_dung (HTML, MEDIUMTEXT), anh_dai_dien, tac_gia, trang_thai (0 nháp / 1 xuất bản), is_noi_bat (0/1), luot_xem,
  created_at, updated_at.
- Dữ liệu mẫu: 3 nhóm (Tin tuyển sinh, Hướng nghiệp, Kỹ năng & học tập), mỗi nhóm 3 bài; bài đầu mỗi nhóm nổi bật.
  Nội dung mang tính tư vấn chung, không nêu mốc thời gian hay số liệu cụ thể.
- Downgrade xóa hai bảng.

Revision ID: 20261214_0087
Revises: 20261213_0086
Create Date: 2026-12-14 10:00:00.000000
"""

from datetime import datetime, timedelta
from urllib.parse import quote

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import MEDIUMTEXT, TINYINT

revision = "20261214_0087"
down_revision = "20261213_0086"
branch_labels = None
depends_on = None

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

# (id, ma_nhom, ten_nhom, slug, mo_ta, thu_tu)
NHOM_TIN = [
    (1, "TUYEN_SINH", "Tin tuyển sinh", "tin-tuyen-sinh",
     "Thông tin, hướng dẫn về kỳ thi, phương thức xét tuyển và đăng ký nguyện vọng.", 1),
    (2, "HUONG_NGHIEP", "Hướng nghiệp", "huong-nghiep",
     "Kiến thức chọn ngành, chọn nghề và tìm hiểu bản thân cho học sinh, sinh viên.", 2),
    (3, "KY_NANG_HOC_TAP", "Kỹ năng & học tập", "ky-nang-hoc-tap",
     "Phương pháp ôn thi, quản lý thời gian và các kỹ năng cần thiết khi đi học, đi làm.", 3),
]

# (nhom_tin_tuc_id, tieu_de, slug, tom_tat, noi_dung, is_noi_bat)
BAI_VIET = [
    (
        1, "Những việc cần làm trong mùa tuyển sinh đại học", "nhung-viec-can-lam-trong-mua-tuyen-sinh-dai-hoc",
        "Từ đăng ký dự thi đến xác nhận nhập học: các bước chính thí sinh cần nắm để không bỏ lỡ cơ hội.",
        "<p>Mùa tuyển sinh gồm nhiều bước nối tiếp nhau. Nắm rõ trình tự giúp thí sinh chủ động chuẩn bị và tránh"
        " bỏ lỡ thời hạn quan trọng.</p>"
        "<h2>1. Đăng ký dự thi tốt nghiệp THPT</h2>"
        "<p>Thí sinh đăng ký dự thi theo hướng dẫn của nhà trường và Bộ Giáo dục và Đào tạo, chọn bài thi tổ hợp"
        " phù hợp với khối ngành dự định xét tuyển.</p>"
        "<h2>2. Theo dõi đề án tuyển sinh của các trường</h2>"
        "<p>Mỗi trường công bố đề án riêng: chỉ tiêu, phương thức xét tuyển, tổ hợp môn và điều kiện phụ. Hãy đọc"
        " kỹ đề án của các trường mình quan tâm.</p>"
        "<h2>3. Đăng ký nguyện vọng và xác nhận nhập học</h2>"
        "<p>Sau khi có điểm, thí sinh đăng ký nguyện vọng trên hệ thống chung, theo dõi kết quả và xác nhận nhập học"
        " đúng hạn.</p>"
        "<p><em>Lưu ý: mốc thời gian cụ thể thay đổi theo từng năm, luôn kiểm tra thông báo chính thức.</em></p>",
        1,
    ),
    (
        1, "Phân biệt các phương thức xét tuyển phổ biến", "phan-biet-cac-phuong-thuc-xet-tuyen-pho-bien",
        "Xét điểm thi tốt nghiệp, học bạ, đánh giá năng lực, xét tuyển thẳng… mỗi phương thức phù hợp với ai?",
        "<p>Các trường đại học hiện sử dụng nhiều phương thức xét tuyển. Hiểu đặc điểm từng phương thức giúp thí sinh"
        " chọn chiến lược phù hợp với thế mạnh của mình.</p>"
        "<ul>"
        "<li><strong>Xét điểm thi tốt nghiệp THPT:</strong> phương thức phổ biến nhất, dựa trên tổng điểm các môn"
        " trong tổ hợp.</li>"
        "<li><strong>Xét học bạ:</strong> dựa trên kết quả học tập THPT, phù hợp với thí sinh học đều, ổn định.</li>"
        "<li><strong>Xét điểm đánh giá năng lực / tư duy:</strong> dùng kết quả các kỳ thi riêng do một số đại học"
        " tổ chức.</li>"
        "<li><strong>Xét tuyển thẳng, ưu tiên xét tuyển:</strong> dành cho thí sinh đạt giải, thuộc diện ưu tiên"
        " theo quy chế.</li>"
        "<li><strong>Kết hợp chứng chỉ:</strong> dùng chứng chỉ ngoại ngữ, chứng chỉ quốc tế kết hợp điểm học tập.</li>"
        "</ul>"
        "<p>Thí sinh có thể đăng ký nhiều phương thức để tăng cơ hội trúng tuyển.</p>",
        0,
    ),
    (
        1, "Cách sắp xếp nguyện vọng để tăng cơ hội trúng tuyển", "cach-sap-xep-nguyen-vong-de-tang-co-hoi-trung-tuyen",
        "Nguyện vọng xếp theo thứ tự ưu tiên: đặt ngành yêu thích nhất lên đầu và luôn có phương án an toàn.",
        "<p>Thứ tự nguyện vọng quyết định ngành bạn được xét trúng tuyển. Thí sinh chỉ trúng tuyển một nguyện vọng"
        " cao nhất mà mình đủ điều kiện.</p>"
        "<h2>Nguyên tắc sắp xếp</h2>"
        "<ul>"
        "<li>Đặt ngành, trường bạn mong muốn nhất ở nguyện vọng 1, kể cả khi điểm chuẩn năm trước hơi cao.</li>"
        "<li>Các nguyện vọng tiếp theo giảm dần mức độ yêu thích và mức điểm.</li>"
        "<li>Luôn có ít nhất một nguyện vọng an toàn, điểm chuẩn thấp hơn điểm dự kiến của bạn.</li>"
        "</ul>"
        "<p>Tham khảo điểm chuẩn các năm trước chỉ để ước lượng, vì điểm chuẩn thay đổi theo đề thi và số lượng"
        " thí sinh mỗi năm.</p>",
        0,
    ),
    (
        2, "Trắc nghiệm Holland giúp gì cho việc chọn ngành?", "trac-nghiem-holland-giup-gi-cho-viec-chon-nganh",
        "Mô hình Holland chia sở thích nghề nghiệp thành 6 nhóm, giúp bạn thu hẹp danh sách ngành nên tìm hiểu.",
        "<p>Lý thuyết Holland (RIASEC) chia sở thích nghề nghiệp thành 6 nhóm: Kỹ thuật (R), Nghiên cứu (I), Nghệ"
        " thuật (A), Xã hội (S), Quản lý (E) và Nghiệp vụ (C).</p>"
        "<h2>Kết quả cho biết điều gì?</h2>"
        "<p>Kết quả phản ánh sở thích của bạn tại thời điểm làm bài, không đo năng lực. Hai hoặc ba nhóm có điểm cao"
        " nhất gợi ý những lĩnh vực bạn có thể thấy hứng thú.</p>"
        "<h2>Dùng kết quả thế nào cho đúng?</h2>"
        "<ul>"
        "<li>Xem kết quả như điểm khởi đầu để tìm hiểu, không phải quyết định cuối cùng.</li>"
        "<li>Kết hợp với năng lực học tập, điều kiện gia đình và nhu cầu xã hội.</li>"
        "<li>Trải nghiệm thực tế: tham quan, trò chuyện với người trong nghề.</li>"
        "</ul>",
        1,
    ),
    (
        2, "Chọn ngành theo sở thích hay theo nhu cầu thị trường?", "chon-nganh-theo-so-thich-hay-theo-nhu-cau-thi-truong",
        "Sở thích giúp bạn bền bỉ, nhu cầu thị trường giúp bạn có việc làm. Làm sao để cân bằng hai yếu tố?",
        "<p>Đây là băn khoăn của rất nhiều học sinh và phụ huynh. Thực tế, lựa chọn tốt thường nằm ở vùng giao nhau"
        " giữa sở thích, năng lực và nhu cầu xã hội.</p>"
        "<h2>Khi chỉ theo sở thích</h2>"
        "<p>Bạn có động lực học tập, nhưng có thể gặp khó khi tìm việc nếu ngành có ít cơ hội.</p>"
        "<h2>Khi chỉ theo thị trường</h2>"
        "<p>Cơ hội việc làm rộng hơn, nhưng dễ mất động lực nếu không thực sự yêu thích công việc.</p>"
        "<h2>Gợi ý cân bằng</h2>"
        "<ul>"
        "<li>Liệt kê các ngành phù hợp sở thích, sau đó tìm hiểu triển vọng việc làm của từng ngành.</li>"
        "<li>Ưu tiên ngành có kỹ năng dễ chuyển đổi sang nhiều lĩnh vực.</li>"
        "</ul>",
        0,
    ),
    (
        2, "Học nghề sau THPT: lựa chọn đáng cân nhắc", "hoc-nghe-sau-thpt-lua-chon-dang-can-nhac",
        "Không phải ai cũng cần vào đại học. Học nghề giúp bạn có tay nghề và đi làm sớm.",
        "<p>Bên cạnh con đường đại học, học nghề tại các trường trung cấp, cao đẳng là lựa chọn phù hợp với nhiều"
        " học sinh muốn đi làm sớm và thích thực hành.</p>"
        "<h2>Ưu điểm</h2>"
        "<ul>"
        "<li>Thời gian đào tạo ngắn, chú trọng thực hành.</li>"
        "<li>Chi phí học tập thường thấp hơn.</li>"
        "<li>Có thể học liên thông lên bậc cao hơn khi có nhu cầu.</li>"
        "</ul>"
        "<h2>Cần cân nhắc</h2>"
        "<p>Chọn nghề phù hợp sức khỏe, tính cách; tìm hiểu kỹ chất lượng đào tạo và cơ hội thực tập của trường.</p>",
        0,
    ),
    (
        3, "Lập kế hoạch ôn thi hiệu quả trong giai đoạn nước rút", "lap-ke-hoach-on-thi-hieu-qua-trong-giai-doan-nuoc-rut",
        "Chia nhỏ mục tiêu, ôn theo chuyên đề và luyện đề có kế hoạch giúp bạn tiến bộ đều đặn.",
        "<p>Giai đoạn cuối trước kỳ thi là lúc cần ôn tập có hệ thống thay vì học dàn trải.</p>"
        "<h2>Các bước gợi ý</h2>"
        "<ol>"
        "<li><strong>Đánh giá hiện trạng:</strong> làm một đề thử để biết phần kiến thức còn yếu.</li>"
        "<li><strong>Ôn theo chuyên đề:</strong> ưu tiên chuyên đề hay ra và chuyên đề mình còn hổng.</li>"
        "<li><strong>Luyện đề định kỳ:</strong> bấm giờ như thi thật, rút kinh nghiệm sau mỗi đề.</li>"
        "<li><strong>Nghỉ ngơi hợp lý:</strong> ngủ đủ giấc, giữ sức khỏe ổn định.</li>"
        "</ol>",
        1,
    ),
    (
        3, "Kỹ năng quản lý thời gian cho học sinh THPT", "ky-nang-quan-ly-thoi-gian-cho-hoc-sinh-thpt",
        "Cân bằng giữa học trên lớp, học thêm và hoạt động cá nhân bằng vài nguyên tắc đơn giản.",
        "<p>Quản lý thời gian tốt giúp bạn học hiệu quả hơn mà vẫn có thời gian nghỉ ngơi, vui chơi.</p>"
        "<ul>"
        "<li><strong>Lập danh sách việc cần làm</strong> mỗi ngày và sắp xếp theo mức độ quan trọng.</li>"
        "<li><strong>Chia nhỏ thời gian học</strong> thành các phiên ngắn, xen kẽ nghỉ giải lao.</li>"
        "<li><strong>Hạn chế xao nhãng:</strong> tắt thông báo điện thoại khi học.</li>"
        "<li><strong>Xem lại cuối tuần:</strong> điều chỉnh kế hoạch cho tuần tiếp theo.</li>"
        "</ul>",
        0,
    ),
    (
        3, "Viết bài luận cá nhân ấn tượng khi ứng tuyển", "viet-bai-luan-ca-nhan-an-tuong-khi-ung-tuyen",
        "Bài luận là cơ hội thể hiện bản thân khi xét tuyển, xin học bổng. Hãy viết chân thật và có câu chuyện riêng.",
        "<p>Nhiều chương trình xét tuyển và học bổng yêu cầu bài luận cá nhân. Đây là nơi hội đồng hiểu bạn là ai"
        " ngoài điểm số.</p>"
        "<h2>Gợi ý khi viết</h2>"
        "<ul>"
        "<li>Kể một câu chuyện cụ thể thay vì liệt kê thành tích.</li>"
        "<li>Nêu rõ lý do bạn chọn ngành, trường và mục tiêu sắp tới.</li>"
        "<li>Viết chân thật, đúng giọng văn của mình.</li>"
        "<li>Nhờ thầy cô, người thân đọc góp ý và kiểm tra lỗi chính tả.</li>"
        "</ul>",
        0,
    ),
]


def _anh(tieu_de: str) -> str:
    """Ảnh đại diện mẫu (ảnh giữ chỗ có chữ), cùng kiểu ảnh mẫu của nghề cụ thể."""
    return f"https://placehold.co/800x500/eaf5eb/2f7a33/png?font=roboto&text={quote(tieu_de)}"


def upgrade() -> None:
    nhom_tin = op.create_table(
        "tin_tuc_nhom_tin",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ma_nhom", sa.String(50), nullable=False),
        sa.Column("ten_nhom", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("mo_ta", sa.Text()),
        sa.Column("thu_tu", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trang_thai", TINYINT(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("ma_nhom", name="uq_tin_tuc_nhom_tin_ma_nhom"),
        sa.UniqueConstraint("slug", name="uq_tin_tuc_nhom_tin_slug"),
        **_BANG,
    )
    bai_viet = op.create_table(
        "tin_tuc_bai_viet",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "nhom_tin_tuc_id",
            sa.Integer(),
            sa.ForeignKey("tin_tuc_nhom_tin.id", name="fk_tin_tuc_bai_viet_nhom_tin_tuc_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("tieu_de", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("tom_tat", sa.Text()),
        sa.Column("noi_dung", MEDIUMTEXT()),
        sa.Column("anh_dai_dien", sa.String(500)),
        sa.Column("tac_gia", sa.String(255)),
        sa.Column("trang_thai", TINYINT(), nullable=False, server_default="1"),
        sa.Column("is_noi_bat", TINYINT(), nullable=False, server_default="0"),
        sa.Column("luot_xem", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_tin_tuc_bai_viet_slug"),
        **_BANG,
    )
    op.create_index("ix_tin_tuc_bai_viet_nhom_tin_tuc_id", "tin_tuc_bai_viet", ["nhom_tin_tuc_id"])
    op.create_index("ix_tin_tuc_bai_viet_trang_thai_created_at", "tin_tuc_bai_viet", ["trang_thai", "created_at"])

    op.bulk_insert(
        nhom_tin,
        [
            {"id": id_, "ma_nhom": ma, "ten_nhom": ten, "slug": slug, "mo_ta": mo_ta, "thu_tu": thu_tu, "trang_thai": 1}
            for id_, ma, ten, slug, mo_ta, thu_tu in NHOM_TIN
        ],
    )
    # Ngày đăng lùi dần mỗi bài một ngày để danh sách "mới nhất" có thứ tự rõ ràng.
    bay_gio = datetime.now().replace(microsecond=0)
    op.bulk_insert(
        bai_viet,
        [
            {
                "nhom_tin_tuc_id": nhom_id, "tieu_de": tieu_de, "slug": slug, "tom_tat": tom_tat, "noi_dung": noi_dung,
                "anh_dai_dien": _anh(tieu_de), "tac_gia": "Ban biên tập", "trang_thai": 1, "is_noi_bat": noi_bat,
                "luot_xem": 0, "created_at": bay_gio - timedelta(days=i), "updated_at": bay_gio - timedelta(days=i),
            }
            for i, (nhom_id, tieu_de, slug, tom_tat, noi_dung, noi_bat) in enumerate(BAI_VIET)
        ],
    )


def downgrade() -> None:
    op.drop_table("tin_tuc_bai_viet")
    op.drop_table("tin_tuc_nhom_tin")
