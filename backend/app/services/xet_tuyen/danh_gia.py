"""Chạy bộ tính xét tuyển trên dữ liệu thật và lưu kết quả (bước 3.5 KE_HOACH_TRIEN_KHAI.md).

- `tai_quy_tac(db, nam)`: nạp quy tắc của các đề án "đang áp dụng" trong năm từ các bảng xt_*, dats_*, dm_*.
  Có cache theo năm trong tiến trình; cache tự làm mới khi có lần import quy tắc mới, đề án đổi trạng thái hoặc
  điểm chuẩn thay đổi (so "dấu phiên bản" trước mỗi lần dùng).
- `chay_danh_gia(...)`: lọc chương trình theo ngành, chạy bộ tính, lưu xt_lan_danh_gia và kết quả.
Đề án chưa "đang áp dụng" không được nạp: kết quả của chúng vẫn theo thuật toán tìm trường cũ.
"""

import time
from dataclasses import asdict, dataclass, field
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.thoi_gian import hom_nay as ngay_hien_tai
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_muc_diem_uu_tien import DmMucDiemUuTien
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dm_truong import DmTruong
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_bo_tieu_chi import XtBoTieuChi, XtMucPhuHop, XtTieuChiPhuHop
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_diem_chuan import XtDiemChuan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_ket_qua import XtKetQuaChuongTrinh, XtKetQuaPhuongAn, XtLanDanhGia
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn
from app.services.xet_tuyen.bo_tinh import theo_truong, tinh_phuong_an, xep_hang
from app.services.xet_tuyen.chuyen_ho_so import KetQuaChuyenHoSo
from app.services.xet_tuyen.mo_hinh import (
    ChuongTrinhTinh,
    CongThucTinh,
    DiemChuanTinh,
    DiemCongTinh,
    DieuKienTinh,
    HeSoMonTinh,
    MonTinh,
    MucPhuHopTinh,
    MucQuyDoiTinh,
    NhomDieuKienTinh,
    PhuongAnTinh,
    QuyTacXetTuyen,
    ThanhPhanTinh,
)

PHIEN_BAN_THUAT_TOAN = "xt-v1"
DANG_AP_DUNG = 2
# Số chương trình tối đa lưu kết quả (theo thứ hạng); phương án chỉ lưu cho các chương trình này.
SO_CHUONG_TRINH_LUU = 200
# Trường có điểm trường từ mức này trở lên được tính là "phù hợp" (mốc "Phù hợp" của bộ tiêu chí mặc định).
DIEM_PHU_HOP = 65


@dataclass
class QuyTacNam:
    """Quy tắc của các đề án đang áp dụng trong một năm, kèm dữ liệu phụ để lọc và lưu kết quả."""

    nam: int
    quy_tac: QuyTacXetTuyen
    diem_chuan: list[DiemChuanTinh]
    bo_tieu_chi_id: int | None
    # chương trình id → ngành id; mã ngành chuẩn ở trình độ ngành
    nganh_chuong_trinh: dict[int, int | None] = field(default_factory=dict)
    ma_nganh_chuan: dict[int, set[str]] = field(default_factory=dict)
    to_hop_id: dict[str, int] = field(default_factory=dict)
    dau_phien_ban: tuple = ()


@dataclass
class KetQuaDanhGia:
    lan_danh_gia_id: int
    so_chuong_trinh: int
    so_truong: int
    so_truong_phu_hop: int
    thoi_gian_tinh_ms: int


_CACHE: dict[int, QuyTacNam] = {}


def _f(value) -> float | None:
    return None if value is None else float(value)


def dau_phien_ban(db: Session, nam: int) -> tuple:
    """Thay đổi khi có import quy tắc mới, đề án đổi trạng thái / cập nhật, điểm chuẩn hoặc danh mục ưu tiên, tổ hợp thay đổi."""
    de_an = db.execute(
        select(func.count(), func.max(DatsTuyenSinh.cap_nhat_luc), func.group_concat(DatsTuyenSinh.id)).where(
            DatsTuyenSinh.nam_tuyen_sinh == nam, DatsTuyenSinh.trang_thai_xet_tuyen == DANG_AP_DUNG
        )
    ).one()
    nhap = db.scalar(select(func.max(XtLichSuImport.id)))
    diem_chuan = db.execute(select(func.count(), func.max(XtDiemChuan.cap_nhat_luc), func.max(XtDiemChuan.id))).one()
    # Gắn ngành / cơ sở cho chương trình, đổi tỉnh của cơ sở (trang "Gắn ngành & cơ sở", "Trụ sở") không qua import.
    dang_ap_dung = select(DatsTuyenSinh.id).where(
        DatsTuyenSinh.nam_tuyen_sinh == nam, DatsTuyenSinh.trang_thai_xet_tuyen == DANG_AP_DUNG
    )
    chuong_trinh = db.execute(
        select(
            func.count(),
            func.sum(func.coalesce(DatsChuongTrinhDaoTao.nganh_dao_tao_id, 0)),
            func.sum(func.coalesce(DatsChuongTrinhDaoTao.co_so_id, 0)),
        ).where(DatsChuongTrinhDaoTao.de_an_id.in_(dang_ap_dung))
    ).one()
    co_so = db.scalar(
        select(func.sum(func.coalesce(DatsTruSo.tinh_thanh_id, 0))).where(DatsTruSo.de_an_id.in_(dang_ap_dung))
    )
    # Danh mục dùng chung: điểm ưu tiên (cả mức theo năm) và khoảng năm áp dụng của tổ hợp.
    danh_muc = (
        tuple(db.execute(select(func.max(DmKhuVucUuTien.updated_at), func.sum(DmKhuVucUuTien.diem_cong))).one()),
        tuple(
            db.execute(select(func.max(DmDoiTuongUuTien.updated_at), func.sum(DmDoiTuongUuTien.diem_cong))).one()
        ),
        tuple(
            db.execute(
                select(func.count(), func.max(DmMucDiemUuTien.cap_nhat_luc), func.sum(DmMucDiemUuTien.diem_cong))
            ).one()
        ),
        tuple(
            db.execute(
                select(
                    func.count(),
                    func.sum(func.coalesce(DmToHopMonHoc.nam_ap_dung_tu, 0)),
                    func.sum(func.coalesce(DmToHopMonHoc.nam_ap_dung_den, 0)),
                )
            ).one()
        ),
    )
    return (tuple(de_an), nhap, tuple(diem_chuan), tuple(chuong_trinh), co_so, danh_muc)


def muc_diem_uu_tien(db: Session, nam: int) -> tuple[dict[str, float], dict[str, float]]:
    """Điểm cộng khu vực, đối tượng ưu tiên áp dụng cho năm tuyển sinh `nam`.

    Lấy dòng dm_muc_diem_uu_tien khớp năm (nhiều dòng thì dòng có năm bắt đầu muộn nhất); mã không có dòng nào
    khớp dùng diem_cong của danh mục.
    """
    khu_vuc = {ma: float(d) for ma, d in db.execute(select(DmKhuVucUuTien.ma_khu_vuc, DmKhuVucUuTien.diem_cong))}
    doi_tuong = {ma: float(d) for ma, d in db.execute(select(DmDoiTuongUuTien.ma_doi_tuong, DmDoiTuongUuTien.diem_cong))}
    theo_loai = {"KHU_VUC": khu_vuc, "DOI_TUONG": doi_tuong}
    for loai, ma, diem in db.execute(
        select(DmMucDiemUuTien.loai, DmMucDiemUuTien.ma, DmMucDiemUuTien.diem_cong)
        .where(
            DmMucDiemUuTien.nam_ap_dung_tu <= nam,
            func.coalesce(DmMucDiemUuTien.nam_ap_dung_den, 9999) >= nam,
        )
        .order_by(DmMucDiemUuTien.nam_ap_dung_tu)
    ):
        theo_loai[loai][ma] = float(diem)
    return khu_vuc, doi_tuong


def co_de_an_dang_ap_dung(db: Session, nam: int) -> bool:
    return bool(
        db.scalar(
            select(func.count()).where(
                DatsTuyenSinh.nam_tuyen_sinh == nam, DatsTuyenSinh.trang_thai_xet_tuyen == DANG_AP_DUNG
            )
        )
    )


def tai_quy_tac(db: Session, nam: int) -> QuyTacNam:
    """Quy tắc các đề án đang áp dụng trong năm, lấy từ cache nếu dữ liệu chưa đổi."""
    dau = dau_phien_ban(db, nam)
    cu = _CACHE.get(nam)
    if cu is not None and cu.dau_phien_ban == dau:
        return cu
    moi = _nap_quy_tac(db, nam)
    moi.dau_phien_ban = dau
    _CACHE[nam] = moi
    return moi


def _nap_quy_tac(db: Session, nam: int, de_an_ids: list[int] | None = None) -> QuyTacNam:
    """Quy tắc các đề án đang áp dụng trong năm; `de_an_ids` thì nạp đúng các đề án đó, bất kể trạng thái (chạy thử)."""
    dieu_kien = (
        [DatsTuyenSinh.id.in_(de_an_ids)]
        if de_an_ids is not None
        else [DatsTuyenSinh.nam_tuyen_sinh == nam, DatsTuyenSinh.trang_thai_xet_tuyen == DANG_AP_DUNG]
    )
    de_an = {d.id: d for d in db.scalars(select(DatsTuyenSinh).where(*dieu_kien))}
    ids = list(de_an)
    qt = QuyTacXetTuyen()
    mon = {m.id: m for m in db.scalars(select(DmMonHoc))}
    ma_mon = {mid: m.ma_mon_hoc for mid, m in mon.items()}
    qt.mon = {m.ma_mon_hoc: MonTinh(ten=m.ten_mon_hoc, nhom=m.nhom_mon or "") for m in mon.values()}
    qt.khu_vuc, qt.doi_tuong = muc_diem_uu_tien(db, nam)

    bo = db.scalar(select(XtBoTieuChi).where(XtBoTieuChi.mac_dinh.is_(True)).order_by(XtBoTieuChi.id))
    if bo is not None:
        qt.trong_so = {
            t.ma_tieu_chi: float(t.trong_so)
            for t in db.scalars(select(XtTieuChiPhuHop).where(XtTieuChiPhuHop.bo_tieu_chi_id == bo.id))
        }
        qt.muc_phu_hop = [
            MucPhuHopTinh(loai=m.loai_muc, nhan=m.nhan, tu=_f(m.gia_tri_tu), den=_f(m.gia_tri_den), diem=_f(m.diem))
            for m in db.scalars(select(XtMucPhuHop).where(XtMucPhuHop.bo_tieu_chi_id == bo.id).order_by(XtMucPhuHop.id))
        ]
    for ma in ("KHA_NANG_TRUNG_TUYEN", "NGANH", "HOC_PHI", "VI_TRI"):
        qt.trong_so.setdefault(ma, 0.0)

    to_hop_id = dict(db.execute(select(DmToHopMonHoc.ma_to_hop, DmToHopMonHoc.id)).all())
    ma_to_hop = {tid: ma for ma, tid in to_hop_id.items()}
    # Tổ hợp ngoài khoảng năm áp dụng không có vị trí môn: phương án dùng tổ hợp đó không tính được điểm.
    con_hieu_luc = set(
        db.scalars(
            select(DmToHopMonHoc.id).where(
                func.coalesce(DmToHopMonHoc.nam_ap_dung_tu, 0) <= nam,
                func.coalesce(DmToHopMonHoc.nam_ap_dung_den, 9999) >= nam,
            )
        )
    )
    vi_tri: dict[str, dict[int, list[str]]] = {}
    for th_id, mon_id, thu_tu in db.execute(
        select(DmToHopMonHocChiTiet.to_hop_id, DmToHopMonHocChiTiet.mon_hoc_id, DmToHopMonHocChiTiet.thu_tu_mon)
    ):
        if thu_tu is not None and th_id in con_hieu_luc and mon_id in ma_mon:
            vi_tri.setdefault(ma_to_hop[th_id], {}).setdefault(thu_tu, []).append(ma_mon[mon_id])
    qt.to_hop = {ma: [ds for _thu_tu, ds in sorted(theo.items())] for ma, theo in vi_tri.items()}

    ket_qua = QuyTacNam(nam=nam, quy_tac=qt, diem_chuan=[], bo_tieu_chi_id=bo.id if bo else None, to_hop_id=to_hop_id)
    if not ids:
        return ket_qua

    for c in db.scalars(select(XtCongThuc).where(XtCongThuc.de_an_id.in_(ids)).order_by(XtCongThuc.id)):
        qt.cong_thuc.append(
            CongThucTinh(
                id=c.id,
                ma=c.ma_cong_thuc,
                de_an_id=c.de_an_id,
                ma_phuong_thuc=c.ma_phuong_thuc_cua_bo,
                kieu=c.kieu_tinh,
                thang=float(c.thang_diem),
                nguon=c.nguon_diem_mon,
                he_so_nhan=float(c.he_so_nhan),
                bang_ngoai_ngu_id=c.bang_quy_doi_ngoai_ngu_id,
                thay_ngoai_ngu=c.thay_ngoai_ngu,
                ap_dung_diem_cong=bool(c.ap_dung_diem_cong),
                ap_dung_uu_tien=bool(c.ap_dung_uu_tien),
                tran_diem_cong=float(c.ty_le_diem_cong_toi_da),
                so_le=c.so_le_lam_tron,
                diem_san=_f(c.diem_san),
                nguong_tb_mon=_f(c.nguong_tb_mon),
                nguong_thpt_to_hop=_f(c.nguong_thpt_to_hop),
                trang_thai=bool(c.trang_thai),
            )
        )
    ct_ids = [c.id for c in qt.cong_thuc]

    hoc_phi = dict(
        db.execute(
            select(DatsHocPhi.de_an_chuong_trinh_id, func.min(DatsHocPhi.hoc_phi_tu))
            .where(DatsHocPhi.de_an_id.in_(ids))
            .group_by(DatsHocPhi.de_an_chuong_trinh_id)
        ).all()
    )
    # Chương trình không có cơ sở (hoặc cơ sở chưa có tỉnh) lấy tỉnh của trường: theo mã tỉnh, không có thì theo tên.
    tinh_theo_ma = {ma: (ma, vung) for ma, vung in db.execute(select(DmTinhThanh.ma_tinh, DmTinhThanh.khu_vuc))}
    tinh_theo_ten = {ten: (ma, vung) for ma, ten, vung in db.execute(select(DmTinhThanh.ma_tinh, DmTinhThanh.ten_tinh, DmTinhThanh.khu_vuc))}
    tinh_truong = {}
    for ma_truong, ma_tinh_truong, ten_tinh_truong in db.execute(
        select(DmTruong.ma_truong, DmTruong.ma_tinh_thanh, DmTruong.ten_tinh_thanh).where(
            DmTruong.ma_truong.in_({d.ma_truong for d in de_an.values()})
        )
    ):
        tinh_truong[ma_truong] = tinh_theo_ma.get(ma_tinh_truong) or tinh_theo_ten.get(ten_tinh_truong)
    for ctr, ma_tinh, vung in db.execute(
        select(DatsChuongTrinhDaoTao, DmTinhThanh.ma_tinh, DmTinhThanh.khu_vuc)
        .outerjoin(DatsTruSo, DatsChuongTrinhDaoTao.co_so_id == DatsTruSo.id)
        .outerjoin(DmTinhThanh, DatsTruSo.tinh_thanh_id == DmTinhThanh.id)
        .where(DatsChuongTrinhDaoTao.de_an_id.in_(ids))
        .order_by(DatsChuongTrinhDaoTao.id)
    ):
        da = de_an[ctr.de_an_id]
        if ma_tinh is None and tinh_truong.get(da.ma_truong):
            ma_tinh, vung = tinh_truong[da.ma_truong]
        qt.chuong_trinh.append(
            ChuongTrinhTinh(
                id=ctr.id,
                de_an_id=ctr.de_an_id,
                nam=da.nam_tuyen_sinh,
                ma_truong=da.ma_truong,
                ma_xet_tuyen=ctr.ma_xet_tuyen,
                ma_tinh=ma_tinh,
                vung=vung,
                hoc_phi_tu=_f(hoc_phi.get(ctr.id)),
            )
        )
        ket_qua.nganh_chuong_trinh[ctr.id] = ctr.nganh_dao_tao_id
    ctr_ids = [c.id for c in qt.chuong_trinh]
    for ct_id, ma in db.execute(
        select(DatsTrinhDoNganh.de_an_chuong_trinh_id, DatsTrinhDoNganh.ma_nganh_chuan).where(
            DatsTrinhDoNganh.de_an_chuong_trinh_id.in_(ctr_ids), DatsTrinhDoNganh.ma_nganh_chuan.is_not(None)
        )
    ):
        ket_qua.ma_nganh_chuan.setdefault(ct_id, set()).add(ma)

    if ct_ids:
        for h in db.scalars(
            select(XtCongThucHeSoMon).where(XtCongThucHeSoMon.cong_thuc_id.in_(ct_ids)).order_by(XtCongThucHeSoMon.id)
        ):
            qt.he_so_mon.append(
                HeSoMonTinh(cong_thuc_id=h.cong_thuc_id, he_so=float(h.he_so), ma_mon=ma_mon.get(h.mon_hoc_id), nhom_mon=h.nhom_mon)
            )
        for t, ma_bai_thi in db.execute(
            select(XtCongThucThanhPhan, DmBaiThiDanhGia.ma_bai_thi)
            .outerjoin(DmBaiThiDanhGia, XtCongThucThanhPhan.bai_thi_id == DmBaiThiDanhGia.id)
            .where(XtCongThucThanhPhan.cong_thuc_id.in_(ct_ids))
            .order_by(XtCongThucThanhPhan.id)
        ):
            qt.thanh_phan.append(
                ThanhPhanTinh(
                    id=t.id,
                    cong_thuc_id=t.cong_thuc_id,
                    vi_tri=t.vi_tri,
                    loai=t.loai_nguon,
                    ten=t.ten_thanh_phan,
                    ma_bai_thi=ma_bai_thi,
                    bang_id=t.bang_quy_doi_id,
                    ma_mon=ma_mon.get(t.mon_hoc_id),
                    he_so=float(t.he_so),
                    nam_tu=t.nam_thi_tu,
                    nam_den=t.nam_thi_den,
                    phan_tu_chon=t.yeu_cau_phan_tu_chon,
                )
            )
    for q, ma_cc, ma_bt in db.execute(
        select(XtBangQuyDoiChiTiet, DmBangCapChungChi.ma_chung_chi, DmBaiThiDanhGia.ma_bai_thi)
        .join(XtBangQuyDoi, XtBangQuyDoiChiTiet.bang_quy_doi_id == XtBangQuyDoi.id)
        .outerjoin(DmBangCapChungChi, XtBangQuyDoiChiTiet.chung_chi_id == DmBangCapChungChi.id)
        .outerjoin(DmBaiThiDanhGia, XtBangQuyDoiChiTiet.bai_thi_id == DmBaiThiDanhGia.id)
        .where(XtBangQuyDoi.de_an_id.in_(ids))
        .order_by(XtBangQuyDoiChiTiet.id)
    ):
        qt.quy_doi.append(
            MucQuyDoiTinh(
                bang_id=q.bang_quy_doi_id,
                quy_doi=float(q.diem_quy_doi),
                ma_chung_chi=ma_cc,
                ma_bai_thi=ma_bt,
                ma_mon=ma_mon.get(q.mon_hoc_id),
                cap_do=q.cap_do,
                tu=_f(q.diem_tu),
                den=_f(q.diem_den),
                he_so_noi_suy=float(q.he_so_noi_suy),
                dat_nguong=bool(q.dat_nguong),
            )
        )
    for pa in db.scalars(
        select(XtPhuongAn).where(XtPhuongAn.de_an_id.in_(ids), XtPhuongAn.trang_thai.is_(True)).order_by(XtPhuongAn.id)
    ):
        qt.phuong_an.append(
            PhuongAnTinh(
                id=pa.id,
                chuong_trinh_id=pa.de_an_chuong_trinh_id,
                cong_thuc_id=pa.cong_thuc_id,
                ma_to_hop=ma_to_hop.get(pa.to_hop_id) if pa.to_hop_id else None,
            )
        )
    nhom_ids = []
    for n in db.scalars(select(XtNhomDieuKien).where(XtNhomDieuKien.de_an_id.in_(ids)).order_by(XtNhomDieuKien.id)):
        if not n.bat_buoc:
            continue  # nhóm chỉ để cảnh báo không loại phương án
        nhom_ids.append(n.id)
        qt.nhom_dieu_kien.append(
            NhomDieuKienTinh(
                id=n.id, de_an_id=n.de_an_id, ten=n.ten_nhom, cong_thuc_id=n.cong_thuc_id, chuong_trinh_id=n.de_an_chuong_trinh_id
            )
        )
    if nhom_ids:
        for d in db.scalars(select(XtDieuKien).where(XtDieuKien.nhom_dieu_kien_id.in_(nhom_ids)).order_by(XtDieuKien.id)):
            qt.dieu_kien.append(
                DieuKienTinh(
                    nhom_id=d.nhom_dieu_kien_id, chi_so=d.ma_chi_so, toan_tu=d.toan_tu, gia_tri=float(d.gia_tri_so), khoa=d.khoa
                )
            )
    for d in db.scalars(select(XtDiemCong).where(XtDiemCong.de_an_id.in_(ids)).order_by(XtDiemCong.id)):
        qt.diem_cong.append(
            DiemCongTinh(
                de_an_id=d.de_an_id,
                nhom=d.nhom_cong,
                chi_so=d.ma_chi_so,
                toan_tu=d.toan_tu,
                gia_tri=float(d.gia_tri_so),
                diem=float(d.diem_cong),
                khoa=d.khoa,
                cong_thuc_id=d.cong_thuc_id,
            )
        )
    truong = {d.ma_truong for d in de_an.values()}
    for dc in db.scalars(
        select(XtDiemChuan)
        .where(XtDiemChuan.ma_truong.in_(truong), XtDiemChuan.nam_tuyen_sinh <= nam)
        .order_by(XtDiemChuan.id)
    ):
        ket_qua.diem_chuan.append(
            DiemChuanTinh(
                ma_truong=dc.ma_truong,
                ma_xet_tuyen=dc.ma_xet_tuyen,
                nam=dc.nam_tuyen_sinh,
                diem=_f(dc.diem_chuan),
                thang=_f(dc.thang_diem),
                ma_phuong_thuc=dc.ma_phuong_thuc_cua_bo,
                ma_to_hop=ma_to_hop.get(dc.to_hop_id) if dc.to_hop_id else None,
                id=dc.id,
            )
        )
    return ket_qua


def chuong_trinh_theo_nganh(db: Session, qtn: QuyTacNam, ma_nganh: str | None) -> set[int] | None:
    """Chương trình thuộc ngành đang tìm (theo ngành đã gắn hoặc mã ngành chuẩn ở trình độ ngành); None = mọi ngành."""
    if not ma_nganh:
        return None
    nganh_id = db.scalar(select(DmNganhDaoTao.id).where(DmNganhDaoTao.ma_nganh == ma_nganh))
    return {
        ct_id
        for ct_id, nid in qtn.nganh_chuong_trinh.items()
        if (nganh_id is not None and nid == nganh_id) or ma_nganh in qtn.ma_nganh_chuan.get(ct_id, set())
    }


def chay_danh_gia(
    db: Session,
    ho_so: KetQuaChuyenHoSo,
    *,
    nam: int,
    ma_nganh: str | None = None,
    nguoi_dung_id: int | None = None,
    ma_thiet_bi: str | None = None,
    lich_su_tim_truong_id: int | None = None,
    ho_so_id: int | None = None,
    hom_nay: date | None = None,
    quy_tac: QuyTacNam | None = None,
) -> KetQuaDanhGia | None:
    """Chạy bộ tính cho một hồ sơ và lưu kết quả; None nếu năm đó chưa có đề án đang áp dụng. Không commit."""
    bat_dau = time.perf_counter()
    qtn = quy_tac or tai_quy_tac(db, nam)
    if not qtn.quy_tac.chuong_trinh or qtn.bo_tieu_chi_id is None:
        return None
    hs = ho_so.ho_so
    kq = tinh_phuong_an(
        qtn.quy_tac,
        hs,
        nam,
        (hom_nay or ngay_hien_tai()).isoformat(),
        qtn.diem_chuan,
        chuong_trinh_ids=chuong_trinh_theo_nganh(db, qtn, ma_nganh),
    )
    dong = xep_hang(qtn.quy_tac, hs, kq)
    truong = theo_truong(dong)
    thoi_gian = int((time.perf_counter() - bat_dau) * 1000)

    luu = dong[:SO_CHUONG_TRINH_LUU]
    lan = XtLanDanhGia(
        nguoi_dung_id=nguoi_dung_id,
        ma_thiet_bi=None if nguoi_dung_id else ma_thiet_bi,
        ho_so_id=ho_so_id,
        nam_tuyen_sinh=nam,
        bo_tieu_chi_id=qtn.bo_tieu_chi_id,
        lich_su_tim_truong_id=lich_su_tim_truong_id,
        phien_ban_thuat_toan=PHIEN_BAN_THUAT_TOAN,
        ho_so_xet_tuyen=asdict(hs),
        gia_dinh=ho_so.gia_dinh,
        so_phuong_an=len(kq.phuong_an),
        so_chuong_trinh=len(dong),
        thoi_gian_tinh_ms=thoi_gian,
    )
    db.add(lan)
    db.flush()
    chuong_trinh_luu = {d.chuong_trinh_id for d in luu}
    ban_ghi = []
    for p in kq.phuong_an:
        if p.chuong_trinh_id not in chuong_trinh_luu:
            continue
        r = XtKetQuaPhuongAn(
            lan_danh_gia_id=lan.id,
            phuong_an_id=p.phuong_an_id,
            de_an_chuong_trinh_id=p.chuong_trinh_id,
            cong_thuc_id=p.cong_thuc_id,
            to_hop_id=qtn.to_hop_id.get(p.ma_to_hop) if p.ma_to_hop else None,
            kieu_tinh=p.kieu,
            thang_diem=p.thang,
            diem_goc=p.diem_goc,
            tb_mon=p.tb_mon,
            tong_thpt_to_hop=p.tong_thpt,
            diem_cong=p.diem_cong,
            diem_uu_tien=p.diem_uu_tien,
            diem_xet=p.diem_xet,
            dat_nguong=p.dat_nguong,
            so_nhom_dieu_kien=p.so_nhom,
            so_nhom_dat=p.so_nhom_dat,
            du_dieu_kien=p.du_dieu_kien,
            ly_do_khong_dat=(p.ly_do or None) and p.ly_do[:1000],
            diem_chuan_id=p.diem_chuan_id,
            diem_chuan_tham_chieu=p.diem_chuan,
            thang_diem_chuan=p.thang_diem_chuan,
            nam_diem_chuan=p.nam_diem_chuan,
            chenh_lech_30=p.chenh_lech_30,
            chi_tiet=(p.chi_tiet or None) and p.chi_tiet[:500],
        )
        ban_ghi.append((p.phuong_an_id, r))
    db.add_all(r for _id, r in ban_ghi)
    db.flush()
    id_ket_qua = {pa_id: r.id for pa_id, r in ban_ghi}
    db.add_all(
        XtKetQuaChuongTrinh(
            lan_danh_gia_id=lan.id,
            de_an_chuong_trinh_id=d.chuong_trinh_id,
            ma_truong=d.ma_truong,
            ket_qua_phuong_an_id=id_ket_qua[d.phuong_an.phuong_an_id],
            la_xet_thang=d.la_xet_thang,
            diem_xet=d.phuong_an.diem_xet,
            thang_diem=d.phuong_an.thang,
            chenh_lech_30=d.phuong_an.chenh_lech_30,
            diem_kha_nang=d.diem_kha_nang,
            diem_hoc_phi=d.diem_hoc_phi,
            diem_vi_tri=d.diem_vi_tri,
            diem_phu_hop=d.diem_phu_hop,
            xep_loai=d.xep_loai,
            thu_hang=d.thu_hang,
        )
        for d in luu
    )
    db.flush()
    return KetQuaDanhGia(
        lan_danh_gia_id=lan.id,
        so_chuong_trinh=len(dong),
        so_truong=len(truong),
        so_truong_phu_hop=sum(1 for t in truong if t.diem_truong is not None and t.diem_truong >= DIEM_PHU_HOP),
        thoi_gian_tinh_ms=thoi_gian,
    )

