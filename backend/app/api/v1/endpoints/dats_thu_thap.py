import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_admin_user
from app.core.thoi_gian import bay_gio, gan_mui_gio
from app.db.session import get_db
from app.models.dats_thu_thap import DatsBanNhapThuThap, DatsNhatKyThuThap, DatsPhienThuThap
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_thu_thap import (
    BanNhapThuThapPublic,
    BoSungBanNhap,
    ChonNguon,
    ChonTatCaNguon,
    DoiChieuBanNhapPublic,
    DungTaoBanNhap,
    DuyetHangLoatRequest,
    DuyetHangLoatResult,
    LoiTaoBanNhapPublic,
    NhatKyThuThapPublic,
    NguonThuThap,
    PhienBanRequest,
    PhienDaDuyetHangLoat,
    PhienDuyetThatBai,
    PhienThuThapCreate,
    PhienThuThapDeleteResult,
    PhienThuThapDetail,
    PhienThuThapPage,
    PhienThuThapPublic,
    SuaBanNhap,
    ThemNguon,
    TinhTrangNguon,
    TomTatPhienBan,
    TrangThaiThuThap,
    TruongThuThapPublic,
)
from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.dats_ban_nhap_thu_thap import canh_bao_dan_chung, lap_muc_ban_nhap, sua_muc_ban_nhap
from app.services.dats_danh_muc_phuong_thuc import MA_PHUONG_THUC_BO_THEO_NAM
from app.services.dats_doi_chieu_diem_chuan import bao_cao_diem_ai, gop_ra_soat_diem
from app.services.dats_do_phu_thu_thap import muc_can_tim_bo_sung
from app.services.dats_hop_dong_thu_thap import hoan_thien_cau_truc_cms, kiem_tra_cau_truc_cms
from app.services.dats_lien_ket_chuong_trinh import doi_chieu_lien_ket_ai
from app.services.dats_kiem_ke_cong_thuc import gop_kiem_ke_cong_thuc
from app.services.dats_ma_tran_thu_thap import bao_cao_ma_tran, chieu_danh_muc, gop_ma_tran
from app.services.dats_projection_cong_thuc import chieu_cong_thuc_vao_ban_nhap, doi_chieu_sau_khi_noi_cong_thuc
from app.services.dats_import import DatsImportError
from app.services.thu_thap_tuyen_sinh_import import import_approved_admission, validate_admission_payload

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/de-an-tuyen-sinh/thu-thap", tags=["thu-thap-tuyen-sinh"], dependencies=[Depends(get_admin_user)]
)

THU_THAP = "thu_thap"
CHO_DUYET = "cho_duyet"
BO_SUNG = "yeu_cau_bo_sung"
DA_DUYET = "da_duyet_va_nhap"
_DANG_TAO_BAN_NHAP = "dang_tao_ban_nhap"
_TAO_BAN_NHAP_THAT_BAI = "tao_ban_nhap_that_bai"
_DA_THAY_DOI = "Phiên đã thay đổi. Hãy mở lại phiên mới nhất trước khi tiếp tục."


class _DaDungTaoBanNhap(Exception):
    """Lượt tạo đã bị dừng hoặc được thay thế."""


def _tim_truong(db: Session, ma_truong: str) -> DmTruong:
    truong = db.scalar(select(DmTruong).where(DmTruong.ma_truong == ma_truong.strip().upper()))
    if truong is None:
        raise HTTPException(400, f"Không tìm thấy trường có mã = {ma_truong}.")
    return truong


def _thong_tin_truong(truong: DmTruong) -> TruongThuThapPublic:
    return TruongThuThapPublic(
        ma_truong=truong.ma_truong, ten_truong=truong.ten_truong,
        co_so=truong.dia_chi_tru_so or truong.ten_tinh_thanh,
        website=truong.website, website_tuyen_sinh=truong.website_tuyen_sinh,
    )


def _phien(db: Session, phien_id: int, *, khoa: bool = False) -> DatsPhienThuThap:
    stmt = select(DatsPhienThuThap).where(DatsPhienThuThap.id == phien_id)
    if khoa:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    phien = db.scalar(stmt)
    if phien is None:
        raise HTTPException(400, f"Không tìm thấy phiên thu thập có id = {phien_id}.")
    return phien


def _ban_nhap(db: Session, phien_id: int, phien_ban: int, *, khoa: bool = False) -> DatsBanNhapThuThap:
    ban = db.get(DatsBanNhapThuThap, (phien_id, phien_ban), with_for_update=khoa)
    if ban is None:
        raise HTTPException(400, f"Không tìm thấy phiên bản {phien_ban} của phiên {phien_id}.")
    return ban


def _trang_thai_truoc_khi_tao(phien: DatsPhienThuThap) -> TrangThaiThuThap:
    if phien.trang_thai == _DANG_TAO_BAN_NHAP:
        return BO_SUNG if phien.yeu_cau_bo_sung is not None else THU_THAP
    return phien.trang_thai


def _dang_tao_ban_nhap(phien: DatsPhienThuThap) -> bool:
    return phien.trang_thai == _DANG_TAO_BAN_NHAP


def _chan_khi_dang_tao(phien: DatsPhienThuThap) -> None:
    if _dang_tao_ban_nhap(phien):
        raise HTTPException(409, {"message": "Phiên đang tạo bản nháp. Hãy đợi kết quả.", "dang_tao_ban_nhap": True})


def _cho_thu_thap(phien: DatsPhienThuThap) -> None:
    _chan_khi_dang_tao(phien)
    if phien.trang_thai not in (THU_THAP, BO_SUNG):
        raise HTTPException(409, "Chỉ thay đổi nguồn hoặc tạo bản nháp trong phiên thu thập hoặc được yêu cầu bổ sung.")


def _cho_duyet(phien: DatsPhienThuThap, phien_ban: int) -> None:
    if phien.phien_ban != phien_ban:
        raise HTTPException(409, _DA_THAY_DOI)
    if phien.trang_thai != CHO_DUYET:
        raise HTTPException(409, "Bản nháp hiện không ở trạng thái Chờ duyệt.")


def _nguon_hop_le(nguon: dict, nam: int) -> bool:
    return nguon["chinh_thuc"] and nguon["phu_hop"] and (
        nguon["nam_ap_dung"] == nam or bool(nguon.get("chi_diem_lich_su"))
    )


def _nguon_nam_hien_tai(nguon: dict, nam: int) -> bool:
    return nguon["nam_ap_dung"] == nam and not nguon.get("chi_diem_lich_su") and _nguon_hop_le(nguon, nam)


def _tinh_trang_nguon(phien: DatsPhienThuThap, da_tim_nguon: bool) -> TinhTrangNguon:
    nguon_hien_tai = [n for n in phien.nguon if _nguon_nam_hien_tai(n, phien.nam_tuyen_sinh)]
    if any(n["lua_chon"] == "su_dung" for n in nguon_hien_tai):
        return "san_sang_tao_nhap"
    if nguon_hien_tai:
        return "cho_chon_nguon"
    if da_tim_nguon or phien.nguon or phien.canh_bao_nguon:
        return "chua_co_nguon_phu_hop"
    return "chua_tim_nguon"


def _ghi_nhat_ky(db: Session, phien: DatsPhienThuThap, nguoi_dung: tuple[int, str], hanh_dong: str, **chi_tiet):
    phien.cap_nhat_luc = bay_gio()
    phien.sua_lan += 1
    db.add(DatsNhatKyThuThap(
        phien_id=phien.id, phien_ban=phien.phien_ban, hanh_dong=hanh_dong, nguoi_dung_id=nguoi_dung[0],
        nguoi_dung=nguoi_dung[1], tao_luc=phien.cap_nhat_luc, chi_tiet=chi_tiet,
    ))


def _dong(db: Session):
    nguoi_tao, nguoi_duyet = aliased(NguoiDung), aliased(NguoiDung)
    da_tim_nguon = select(DatsNhatKyThuThap.id).where(
        DatsNhatKyThuThap.phien_id == DatsPhienThuThap.id, DatsNhatKyThuThap.hanh_dong == "tim_nguon"
    ).exists().label("da_tim_nguon")
    nhat_ky = DatsNhatKyThuThap
    loi_tao = select(nhat_ky.chi_tiet).where(
        nhat_ky.phien_id == DatsPhienThuThap.id, nhat_ky.hanh_dong == _TAO_BAN_NHAP_THAT_BAI,
    ).order_by(nhat_ky.id.desc()).limit(1).scalar_subquery().label("loi_tao_ban_nhap")
    return db.query(DatsPhienThuThap, DmTruong, nguoi_tao.ho_ten, nguoi_duyet.ho_ten, da_tim_nguon, loi_tao).join(
        DmTruong, DatsPhienThuThap.ma_truong == DmTruong.ma_truong
    ).outerjoin(nguoi_tao, nguoi_tao.id == DatsPhienThuThap.tao_boi).outerjoin(
        nguoi_duyet, nguoi_duyet.id == DatsPhienThuThap.duyet_boi
    )


def _tom_tat(
    phien: DatsPhienThuThap, truong: DmTruong, ten_nguoi_tao, ten_nguoi_duyet, da_tim_nguon: bool, loi_tao: dict | None,
) -> PhienThuThapPublic:
    dang_tao = _dang_tao_ban_nhap(phien)
    loi_tao_ban_nhap = None
    if phien.trang_thai in (THU_THAP, BO_SUNG) and loi_tao and loi_tao.get("sua_lan") == phien.sua_lan:
        loi_tao_ban_nhap = LoiTaoBanNhapPublic(**loi_tao, xay_ra_luc=gan_mui_gio(phien.cap_nhat_luc))
    return PhienThuThapPublic(
        id=phien.id, ma_truong=phien.ma_truong, ten_truong=truong.ten_truong,
        co_so=_thong_tin_truong(truong).co_so, nam_tuyen_sinh=phien.nam_tuyen_sinh,
        trang_thai=_trang_thai_truoc_khi_tao(phien), tinh_trang_nguon=_tinh_trang_nguon(phien, da_tim_nguon),
        dang_tao_ban_nhap=dang_tao,
        luot_tao_ban_nhap=phien.sua_lan if dang_tao else None,
        bat_dau_tao_ban_nhap_luc=gan_mui_gio(phien.bat_dau_tao_ban_nhap_luc or phien.cap_nhat_luc) if dang_tao else None,
        tien_do_tao_ban_nhap=phien.tien_do_tao_ban_nhap if dang_tao else None,
        loi_tao_ban_nhap=loi_tao_ban_nhap,
        tao_boi=phien.tao_boi, ten_nguoi_tao=ten_nguoi_tao,
        tao_luc=gan_mui_gio(phien.tao_luc), cap_nhat_luc=gan_mui_gio(phien.cap_nhat_luc), phien_ban=phien.phien_ban,
        de_an_id=phien.de_an_id, duyet_boi=phien.duyet_boi, ten_nguoi_duyet=ten_nguoi_duyet,
        duyet_luc=gan_mui_gio(phien.duyet_luc),
    )


def _loi_du_lieu(du_lieu: dict, ma_truong: str, nam: int) -> list[str]:
    loi = kiem_tra_cau_truc_cms(du_lieu)
    try:
        validate_admission_payload(du_lieu, ma_truong, nam)
    except DatsImportError as exc:
        loi.extend(exc.loi)
    return list(dict.fromkeys(loi))


def _kiem_tra_ban_nhap(phien: DatsPhienThuThap, ban: DatsBanNhapThuThap) -> tuple[list[str], DoiChieuBanNhapPublic]:
    doi_chieu = ban.doi_chieu or {}
    if phien.trang_thai == DA_DUYET and phien.phien_ban == ban.phien_ban:
        return [], DoiChieuBanNhapPublic(**{**doi_chieu, "canh_bao_dan_chung": canh_bao_dan_chung(ban.du_lieu, ban.muc)})
    loi = _loi_du_lieu(ban.du_lieu, phien.ma_truong, phien.nam_tuyen_sinh)
    doi_chieu = {**doi_chieu, "canh_bao_dan_chung": canh_bao_dan_chung(ban.du_lieu, ban.muc) if not loi else []}
    return loi, DoiChieuBanNhapPublic(**doi_chieu)


def _chi_tiet(db: Session, phien_id: int, phien_ban: int | None = None) -> PhienThuThapDetail:
    dong = _dong(db).filter(DatsPhienThuThap.id == phien_id).first()
    if dong is None:
        raise HTTPException(400, f"Không tìm thấy phiên thu thập có id = {phien_id}.")
    phien = dong[0]
    ban = _ban_nhap(db, phien_id, phien_ban) if phien_ban is not None else None
    if ban is None and phien.phien_ban is not None:
        ban = _ban_nhap(db, phien_id, phien.phien_ban)
    chi_tiet_ban = None
    if ban:
        loi, doi_chieu = _kiem_tra_ban_nhap(phien, ban)
        chi_tiet_ban = BanNhapThuThapPublic(
            phien_ban=ban.phien_ban, ten_nguoi_tao=ban.ten_nguoi_tao, tao_luc=gan_mui_gio(ban.tao_luc),
            du_lieu=ban.du_lieu, muc=ban.muc, nguon=ban.nguon, ghi_chu=ban.ghi_chu, loi=loi, doi_chieu=doi_chieu,
        )
    lich_su = db.scalars(select(DatsNhatKyThuThap).where(
        DatsNhatKyThuThap.phien_id == phien_id
    ).order_by(DatsNhatKyThuThap.id.desc())).all()
    bang = DatsBanNhapThuThap
    cac_ban = db.execute(select(bang.phien_ban, bang.tao_luc, bang.ten_nguoi_tao).where(
        bang.phien_id == phien_id
    ).order_by(bang.phien_ban.desc())).all()
    return PhienThuThapDetail(
        **_tom_tat(*dong).model_dump(),
        nguon=phien.nguon if phien_ban is None or ban is None else ban.nguon,
        canh_bao_nguon=phien.canh_bao_nguon, ban_nhap=chi_tiet_ban,
        lich_su=[NhatKyThuThapPublic.model_validate(i).model_copy(update={"tao_luc": gan_mui_gio(i.tao_luc)}) for i in lich_su],
        yeu_cau_bo_sung=phien.yeu_cau_bo_sung,
        cac_phien_ban=[TomTatPhienBan(phien_ban=p, tao_luc=gan_mui_gio(t), ten_nguoi_tao=n) for p, t, n in cac_ban],
    )


def _them_ban(db: Session, phien: DatsPhienThuThap, ten: str, du_lieu, muc, ghi_chu, nguon, doi_chieu) -> None:
    phien.phien_ban = (phien.phien_ban or 0) + 1
    db.add(DatsBanNhapThuThap(
        phien_id=phien.id, phien_ban=phien.phien_ban, tao_luc=bay_gio(), ten_nguoi_tao=ten,
        du_lieu=du_lieu, muc=muc, ghi_chu=ghi_chu, nguon=nguon, doi_chieu=doi_chieu,
    ))


@router.get("/truong", response_model=TruongThuThapPublic)
def nhan_dien_truong(ma_truong: str = Query(min_length=1, max_length=20), db: Session = Depends(get_db)):
    """Nhận diện trường hoặc cơ sở theo mã tuyển sinh trước khi tìm nguồn."""
    return _thong_tin_truong(_tim_truong(db, ma_truong))


@router.post("/phien", response_model=PhienThuThapDetail, status_code=201)
def tao_phien(
    yeu_cau: PhienThuThapCreate, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
    tac_vu: BackgroundTasks = None, tu_dong: bool = False,
):
    """Tạo phiên thu thập cho một trường và một năm."""
    truong = _tim_truong(db, yeu_cau.ma_truong)
    luc = bay_gio()
    phien = DatsPhienThuThap(
        ma_truong=truong.ma_truong, nam_tuyen_sinh=yeu_cau.nam_tuyen_sinh, trang_thai=THU_THAP,
        tao_boi=user.id, tao_luc=luc, cap_nhat_luc=luc,
    )
    db.add(phien)
    db.flush()
    phien_id = phien.id
    _ghi_nhat_ky(db, phien, (user.id, user.ho_ten), "tao_phien")
    if tu_dong:
        db.flush()
        return tao_ban_nhap(phien_id, db, user, tac_vu, tu_dong=True)
    db.commit()
    return _chi_tiet(db, phien_id)


@router.get("/phien", response_model=PhienThuThapPage)
def danh_sach_phien(
    q: str | None = Query(default=None, max_length=255), ma_truong: str | None = Query(default=None, max_length=20),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100), trang_thai: TrangThaiThuThap | None = None,
    page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=200), db: Session = Depends(get_db),
):
    """Liệt kê phiên thu thập và hàng đợi xét duyệt theo bộ lọc của CMS."""
    stmt = _dong(db)
    if q and q.strip():
        tu_khoa = q.strip()
        stmt = stmt.filter(or_(DmTruong.ma_truong.contains(tu_khoa, autoescape=True),
                               DmTruong.ten_truong.contains(tu_khoa, autoescape=True)))
    if ma_truong and ma_truong.strip():
        stmt = stmt.filter(DatsPhienThuThap.ma_truong == ma_truong.strip().upper())
    if nam_tuyen_sinh is not None:
        stmt = stmt.filter(DatsPhienThuThap.nam_tuyen_sinh == nam_tuyen_sinh)
    if trang_thai is not None:
        bang = DatsPhienThuThap
        cung_trang_thai = bang.trang_thai == trang_thai
        if trang_thai in (THU_THAP, BO_SUNG):
            dang_bo_sung = bang.yeu_cau_bo_sung.is_not(None) if trang_thai == BO_SUNG else bang.yeu_cau_bo_sung.is_(None)
            cung_trang_thai = or_(cung_trang_thai, (bang.trang_thai == _DANG_TAO_BAN_NHAP) & dang_bo_sung)
        stmt = stmt.filter(cung_trang_thai)
    total = stmt.with_entities(func.count(DatsPhienThuThap.id)).scalar() or 0
    rows = stmt.order_by(DatsPhienThuThap.cap_nhat_luc.desc(), DatsPhienThuThap.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return PhienThuThapPage(items=[_tom_tat(*row) for row in rows], total=total, page=page, page_size=page_size)


@router.get("/phien/{phien_id}", response_model=PhienThuThapDetail)
def chi_tiet_phien(phien_id: int, phien_ban: int | None = Query(default=None, ge=1), db: Session = Depends(get_db)):
    """Mở phiên, nhật ký và một phiên bản nháp bất kỳ."""
    return _chi_tiet(db, phien_id, phien_ban)


@router.delete("/phien/{phien_id}", response_model=PhienThuThapDeleteResult)
def xoa_phien(phien_id: int, db: Session = Depends(get_db)) -> PhienThuThapDeleteResult:
    """Xóa phiên, bản nháp và nhật ký của phiên chưa được nhập vào hệ thống."""
    phien = _phien(db, phien_id, khoa=True)
    _chan_khi_dang_tao(phien)
    if _trang_thai_truoc_khi_tao(phien) not in (THU_THAP, CHO_DUYET, BO_SUNG) or phien.de_an_id is not None:
        raise HTTPException(409, "Phiên đã duyệt và nhập được giữ lại để đối chiếu với đề án.")
    db.delete(phien)
    db.commit()
    return PhienThuThapDeleteResult(deleted=1)


def _cap_nhat_nguon(ds: list[dict], ket_qua: list[dict], nam: int, *, tu_tim_kiem: bool = False) -> list[dict]:
    danh_sach = list(ds)
    vi_tri_theo_url = {}
    for vi_tri, nguon in enumerate(ds):
        url = nguon["url"]
        vi_tri_theo_url.setdefault(ai._url_so_sanh(url) or url, vi_tri)
    id_moi = max((n["id"] for n in ds), default=0) + 1
    for n in ket_qua:
        url = n["url"]
        vi_tri = vi_tri_theo_url.setdefault(ai._url_so_sanh(url) or url, len(danh_sach))
        if vi_tri == len(danh_sach):
            danh_sach.append(NguonThuThap.model_validate({**n, "id": id_moi}).model_dump())
            id_moi += 1
            continue
        cu = danh_sach[vi_tri]
        # Kết quả tìm kiếm có thể thiếu thông tin đã xác minh khi quản trị viên thêm nguồn.
        if tu_tim_kiem and _nguon_hop_le(cu, nam):
            continue
        moi = NguonThuThap.model_validate({**cu, **n, "url": cu["url"]}).model_dump()
        if moi["lua_chon"] == "su_dung" and not _nguon_hop_le(moi, nam):
            moi["lua_chon"] = "chua_chon"
        danh_sach[vi_tri] = moi
    return danh_sach


def _chuan_bi_ai(db: Session, phien_id: int, user: NguoiDung, *, khoa: bool = False):
    phien = _phien(db, phien_id, khoa=khoa)
    _cho_thu_thap(phien)
    truong = _thong_tin_truong(_tim_truong(db, phien.ma_truong)).model_dump()
    return phien, truong, (user.id, user.ho_ten), phien.sua_lan


def _sau_khi_goi_ai(db: Session, phien_id: int, sua_lan: int) -> DatsPhienThuThap:
    phien = _phien(db, phien_id, khoa=True)
    if phien.sua_lan != sua_lan:
        raise HTTPException(409, _DA_THAY_DOI)
    _cho_thu_thap(phien)
    return phien


@router.post("/phien/{phien_id}/tim-nguon", response_model=PhienThuThapDetail)
def tim_nguon(
    phien_id: int, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
):
    """Tìm tài liệu tuyển sinh với số lượng do AI xác định."""
    phien, truong, actor, sua_lan = _chuan_bi_ai(db, phien_id, user)
    nam = phien.nam_tuyen_sinh
    db.rollback()  # Không giữ kết nối hoặc khóa MySQL khi gọi AI.
    try:
        ds, ghi_chu = ai.search_sources(truong, nam)
    except ai.AdmissionAIError as exc:
        raise HTTPException(502, str(exc)) from exc
    phien = _sau_khi_goi_ai(db, phien_id, sua_lan)
    phien.nguon = _cap_nhat_nguon(phien.nguon, ds, nam, tu_tim_kiem=True)
    phien.canh_bao_nguon = ghi_chu
    _ghi_nhat_ky(db, phien, actor, "tim_nguon", urls=[n["url"] for n in ds])
    db.commit()
    return _chi_tiet(db, phien_id)


@router.post("/phien/{phien_id}/nguon", response_model=PhienThuThapDetail)
def them_nguon(phien_id: int, yeu_cau: ThemNguon, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user)):
    """Đọc URL do quản trị viên thêm và đối chiếu với trường, năm của phiên."""
    phien, truong, actor, sua_lan = _chuan_bi_ai(db, phien_id, user)
    nam = phien.nam_tuyen_sinh
    db.rollback()
    try:
        nguon = ai.inspect_source(truong, nam, yeu_cau.url)
    except ai.AdmissionAIError as exc:
        raise HTTPException(400, str(exc)) from exc
    phien = _sau_khi_goi_ai(db, phien_id, sua_lan)
    phien.nguon = _cap_nhat_nguon(phien.nguon, [nguon], nam)
    _ghi_nhat_ky(db, phien, actor, "them_nguon", url=nguon["url"])
    db.commit()
    return _chi_tiet(db, phien_id)


@router.patch("/phien/{phien_id}/nguon/{nguon_id}", response_model=PhienThuThapDetail)
def chon_nguon(
    phien_id: int, nguon_id: int, yeu_cau: ChonNguon, db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_admin_user),
):
    """Chọn tài liệu chính thức, loại nguồn hoặc bỏ lựa chọn."""
    phien = _phien(db, phien_id, khoa=True)
    _cho_thu_thap(phien)
    nguon = next((n for n in phien.nguon if n["id"] == nguon_id), None)
    if nguon is None:
        raise HTTPException(400, f"Không tìm thấy nguồn có id = {nguon_id}.")
    if yeu_cau.lua_chon == "su_dung" and not _nguon_hop_le(nguon, phien.nam_tuyen_sinh):
        raise HTTPException(422, nguon.get("ly_do") or "Nguồn không phù hợp với trường và năm của phiên.")
    moi = {**nguon, "lua_chon": yeu_cau.lua_chon, "ly_do_loai": (yeu_cau.ly_do or None) if yeu_cau.lua_chon == "loai" else None}
    phien.nguon = [moi if n["id"] == nguon_id else n for n in phien.nguon]
    _ghi_nhat_ky(db, phien, (user.id, user.ho_ten), "chon_nguon", nguon_id=nguon_id, url=nguon["url"],
                 truoc=nguon["lua_chon"], sau=yeu_cau.lua_chon, ly_do=yeu_cau.ly_do)
    db.commit()
    return _chi_tiet(db, phien_id)


@router.patch("/phien/{phien_id}/nguon", response_model=PhienThuThapDetail)
def chon_nhieu_nguon(
    phien_id: int, yeu_cau: ChonTatCaNguon, db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_admin_user),
):
    """Chọn tất cả nguồn chính thức phù hợp đang chờ chọn."""
    phien = _phien(db, phien_id, khoa=True)
    _cho_thu_thap(phien)
    nguon_ids = [
        n["id"] for n in phien.nguon
        if n["lua_chon"] == "chua_chon" and _nguon_hop_le(n, phien.nam_tuyen_sinh)
    ]
    if nguon_ids:
        da_chon = set(nguon_ids)
        phien.nguon = [
            {**n, "lua_chon": yeu_cau.lua_chon, "ly_do_loai": None} if n["id"] in da_chon else n
            for n in phien.nguon
        ]
        _ghi_nhat_ky(
            db, phien, (user.id, user.ho_ten), "chon_nhieu_nguon", nguon_ids=nguon_ids,
            truoc="chua_chon", sau=yeu_cau.lua_chon,
        )
    db.commit()
    return _chi_tiet(db, phien_id)


def _danh_muc_phuong_thuc(db: Session, nam: int) -> list[dict]:
    if nam in MA_PHUONG_THUC_BO_THEO_NAM:
        return [
            {"ma_phuong_thuc": ma, "ten_phuong_thuc": ten}
            for ma, ten in MA_PHUONG_THUC_BO_THEO_NAM[nam].items()
        ]
    bang = DmPhuongThucTuyenSinh
    cau_lenh = select(
        bang.ma_phuong_thuc, bang.ten_phuong_thuc, bang.giai_thich, bang.truong_hop_cu_the, bang.luu_y,
    ).where(
        bang.trang_thai == 1,
        or_(bang.pham_vi_ap_dung.is_(None), func.lower(func.trim(bang.pham_vi_ap_dung)).in_((
            "", "chung", "danh_muc_chung", "toan_quoc", "toàn quốc", "bo", "bộ", "bo_gddt", "bộ gd&đt",
        ))),
        or_(bang.nam_ap_dung_tu.is_not(None), bang.nam_ap_dung_den.is_not(None)),
        or_(bang.nam_ap_dung_tu.is_(None), bang.nam_ap_dung_tu <= nam),
        or_(bang.nam_ap_dung_den.is_(None), bang.nam_ap_dung_den >= nam),
    ).order_by(bang.ma_phuong_thuc)
    return [dict(dong) for dong in db.execute(cau_lenh).mappings()]


@dataclass
class _NoiDungBanNhap:
    du_lieu: dict
    muc: list[dict]
    ghi_chu: list[str]
    doi_chieu: dict
    nguon_ids: list[int]
    loi_nguon: dict[int, str]

    def ra_soat(self, truong, nam, nguon, muc_cu, bao_tien_do):
        da_dung = [n for n in nguon if n["id"] in self.nguon_ids]
        loi = []
        for thong_bao in _loi_du_lieu(self.du_lieu, truong["ma_truong"], nam):
            path = thong_bao.partition(":")[0]
            scope = ai._pham_vi_muc(self.du_lieu, path) if path.startswith("/") and path != "/" else {}
            ma = scope.get("ma_xet_tuyen") or scope.get("ma_cong_thuc")
            loi.append(f"{ma} — {thong_bao}" if ma else thong_bao)
        quan_sat = {
            "ghi_chu": self.ghi_chu,
            "bang_chuong_trinh": self.doi_chieu.get("nguon", []),
            "diem_chuan": self.doi_chieu.get("diem_chuan"),
            "loi_cau_truc": loi,
            "nguon_chua_doc_duoc": [{"id": n["id"], "url": n["url"], "loi": self.loi_nguon[n["id"]]}
                                    for n in nguon if n["id"] in self.loi_nguon],
        }
        ma_tran = self.doi_chieu.get("ma_tran") or {}
        cong_thuc = self.doi_chieu.get("cong_thuc") or {}
        chua_ghi = [f"{r['ma_xet_tuyen']} — {r['noi_dung']}" for r in ma_tran.get("chua_ghi", [])]
        chua_ghi.extend(f"{r['pham_vi']} · {r['ten']} — {r.get('ly_do') or 'Chưa ghi được công thức vào bản nháp'}"
                        for r in cong_thuc.get("cong_thuc", []) if r["trang_thai"] == "chua_ghi")
        chua_ghi.extend(ma_tran.get("can_lam_ro", []))
        chua_ghi.extend(cong_thuc.get("can_lam_ro", []))
        quan_sat["du_kien_nguon_chua_ghi"] = chua_ghi
        try:
            muc_moi = muc_can_tim_bo_sung(truong, nam, self.muc, da_dung, quan_sat, muc_cu, bao_tien_do)
        except ai.AdmissionAIError as exc:
            self.ghi_chu.append(f"AI chưa hoàn tất rà soát bản nháp. {exc}")
            con_thieu = list(dict.fromkeys([*muc_cu, *chua_ghi, *loi]))
            self.doi_chieu.update(muc_con_thieu=con_thieu or None, trang_thai_ra_soat_ai="chua_hoan_tat")
            return con_thieu
        muc_moi = list(dict.fromkeys([*muc_moi, *chua_ghi, *loi]))
        self.doi_chieu.update(muc_con_thieu=muc_moi, trang_thai_ra_soat_ai="da_ra_soat")
        return muc_moi


def _lap_ban_nhap(trich_xuat: dict, truong: dict, nam: int, ds: list[dict]) -> _NoiDungBanNhap:
    ket_qua = trich_xuat["du_lieu"]
    if not isinstance(ket_qua.get("dats_tuyen_sinh"), dict) or not isinstance(ket_qua.get("quy_tac_xet_tuyen"), dict):
        raise ai.AdmissionAIError("AI chưa trả đủ hai khối dữ liệu đề án và quy tắc xét tuyển.")
    du_lieu = hoan_thien_cau_truc_cms({
        "thong_tin_import": {"ma_truong": truong["ma_truong"], "nam_tuyen_sinh": nam, "xu_ly_khi_da_ton_tai": "tu_choi"},
        "dats_tuyen_sinh": {**ket_qua["dats_tuyen_sinh"], "trang_thai": "nhap", "trang_thai_xet_tuyen": 1},
        "quy_tac_xet_tuyen": ket_qua["quy_tac_xet_tuyen"],
    })
    nguon_ids = trich_xuat.get("nguon_ids", [n["id"] for n in ds])
    id_da_dung = set(nguon_ids)
    da_dung = [n for n in ds if n["id"] in id_da_dung]
    muc = lap_muc_ban_nhap(du_lieu, trich_xuat["muc"], da_dung, nam)
    doi_chieu = {"nguon": trich_xuat.get("doi_chieu_chuong_trinh", []), "xac_nhan": {}}
    if "ma_tran_goc" in trich_xuat:
        doi_chieu["ma_tran"] = bao_cao_ma_tran(trich_xuat)
        doi_chieu["ma_tran_goc"] = trich_xuat["ma_tran_goc"]
    if "cong_thuc_da_doi_chieu" in trich_xuat:
        doi_chieu["cong_thuc"] = trich_xuat["cong_thuc_da_doi_chieu"]
    if ra_soat := trich_xuat.get("ra_soat_diem_chuan"):
        doi_chieu["ra_soat_diem_chuan"] = ra_soat
        doi_chieu["diem_chuan"] = bao_cao_diem_ai(ra_soat, du_lieu, muc)
    ghi_chu = list(trich_xuat["ghi_chu"])
    return _NoiDungBanNhap(du_lieu, muc, ghi_chu, doi_chieu, nguon_ids, trich_xuat.get("loi_nguon", {}))


def _nguon_html(nguon: dict) -> bool:
    url = ai._url_cong_khai(nguon["url"])
    return not ai._la_tep_tim_nguon(url)


def _chon_nguon_tu_dong(nguon: list[dict], ket_qua: list[dict], nam: int, giu_chua_chon: set[int]) -> list[dict]:
    danh_sach = _cap_nhat_nguon(nguon, ket_qua, nam, tu_tim_kiem=True)
    return [
        {**n, "lua_chon": "su_dung"}
        if n["lua_chon"] == "chua_chon" and n["id"] not in giu_chua_chon and _nguon_hop_le(n, nam) and _nguon_html(n)
        else n for n in danh_sach
    ]


def _tim_bo_sung_ban_nhap(
    truong: dict, nam: int, nguon: list[dict], ban: _NoiDungBanNhap, ket_qua_cu: dict, phan_thieu: list[str],
    trich_xuat: Callable, bao_tien_do: Callable, luu_nguon: Callable, giu_chua_chon: set[int], *, doc_lai=False,
):
    bao_tien_do("doc_lai_nguon" if doc_lai else "tim_bo_sung")
    canh_bao = []
    try:
        if doc_lai:
            chon = [n for n in nguon if n["lua_chon"] == "su_dung" and _nguon_hop_le(n, nam) and _nguon_html(n)]
            da_doc = [n for n in chon if n["id"] in ban.nguon_ids]
            ids = set(ban.loi_nguon)
            for row in (ban.doi_chieu.get("ma_tran") or {}).get("chua_ghi", []):
                ids.update(dc["nguon_id"] for dc in row["dan_chung"])
            for row in (ban.doi_chieu.get("cong_thuc") or {}).get("cong_thuc", []):
                if row["trang_thai"] == "chua_ghi":
                    ids.update(dc["nguon_id"] for dc in row["dan_chung"])
            ids.update(r["nguon_id"] for r in (ket_qua_cu.get("kiem_ke_cong_thuc") or {}).get("phan_nguon", [])
                       if not r["da_kiem_ke"] or r["can_lam_ro"])
            ids.update(int(i) for i in (ket_qua_cu.get("ma_tran_goc") or {}).get("loi_theo_nguon", {}))
            if phan_thieu and da_doc:
                try:
                    ids.update(ai.chon_nguon_doc_lai(truong, nam, phan_thieu, da_doc, ban.ghi_chu))
                except ai.AdmissionAIError as exc:
                    canh_bao.append(f"AI chưa chọn được trang cần đọc lại. {exc}")
            bo_sung = [n for n in chon if n["id"] in ids]
        else:
            tim_duoc, canh_bao = ai.search_missing_sources(truong, nam, phan_thieu, [n["url"] for n in nguon])
            so_nguon_cu = len(nguon)
            nguon = _chon_nguon_tu_dong(nguon, tim_duoc, nam, giu_chua_chon)
            luu_nguon(nguon, canh_bao)
            bo_sung = [n for n in nguon[so_nguon_cu:] if n["lua_chon"] == "su_dung"]
            if not bo_sung:
                canh_bao.append("Chưa tìm thấy trang HTML chính thức mới cho các mục còn thiếu.")
        if not bo_sung:
            return None, nguon, canh_bao
        if not any(_nguon_nam_hien_tai(n, nam) for n in bo_sung):
            goc = next((n for n in nguon if n["id"] in ban.nguon_ids and _nguon_nam_hien_tai(n, nam)), None)
            if not goc:
                return None, nguon, [*canh_bao, "Thiếu nguồn đã xác minh đúng năm để đối chiếu điểm chuẩn lịch sử."]
            bo_sung = [goc, *bo_sung]
        def tham_chieu(khoi, ten, *khoa):
            dong = khoi.get(ten)
            if not isinstance(dong, list):
                return []
            return [{k: item.get(k) for k in khoa} for item in dong if isinstance(item, dict)]

        quy_tac = ban.du_lieu["quy_tac_xet_tuyen"]
        goi_y = {
            "muc_can_bo_sung": phan_thieu,
            "muc_diem_can_lam_ro": [
                {**q, "stt": i} for i, q in enumerate(ket_qua_cu.get("ra_soat_diem_chuan", {}).get("can_lam_ro", []), 1)
            ],
            "chuong_trinh_da_doc": tham_chieu(quy_tac, "chuong_trinh", "ma_xet_tuyen", "ma_chuong_trinh", "ten_chuong_trinh", "ma_co_so"),
            "cong_thuc_da_doc": tham_chieu(quy_tac, "cong_thuc", "ma_cong_thuc", "ten_cong_thuc", "ma_phuong_thuc_cua_bo"),
            "co_so_da_doc": tham_chieu(quy_tac, "co_so", "ma_co_so", "ten_co_so", "dia_chi"),
            "tru_so_da_doc": tham_chieu(ban.du_lieu["dats_tuyen_sinh"], "dats_tru_so", "id", "ten_co_so", "dia_chi"),
        }
        them = trich_xuat(bo_sung, goi_y)
        du_lieu, muc, doi_chieu = ai._gop_ket_qua([ket_qua_cu, them], [])
        # Hai kết quả đã được kiểm tra khi trích và mỗi kết quả có thể gồm nhiều phần tài liệu.
        ghi_chu = list(dict.fromkeys([*ket_qua_cu.get("ghi_chu", []), *them.get("ghi_chu", [])]))
        ids = list(dict.fromkeys([*ban.nguon_ids, *them.get("nguon_ids", [n["id"] for n in bo_sung])]))
        # Trang đọc lại có thể trả nguyên văn cùng hàng và cùng dẫn chứng.
        def duy_nhat(dong):
            da_gap = {}
            for item in dong:
                da_gap.setdefault(json.dumps(item, ensure_ascii=False, sort_keys=True), item)
            return list(da_gap.values())

        muc = duy_nhat(muc)
        ai.doi_chieu_mau_thuan_ai(truong, nam, du_lieu, muc, [n for n in nguon if n["id"] in ids], bao_tien_do)
        loi = {**ban.loi_nguon, **them.get("loi_nguon", {})}
        tong_hop = {
            "du_lieu": du_lieu, "muc": muc, "doi_chieu_chuong_trinh": duy_nhat(doi_chieu),
            "nguon_ids": ids, "loi_nguon": {i: v for i, v in loi.items() if i not in ids}, "ghi_chu": ghi_chu,
        }
        tong_hop["ra_soat_diem_chuan"] = gop_ra_soat_diem(
            ket_qua_cu.get("ra_soat_diem_chuan"), them.get("ra_soat_diem_chuan"),
        )
        if "ma_tran_goc" in ket_qua_cu or "ma_tran_goc" in them:
            tong_hop["ma_tran_goc"] = gop_ma_tran(ket_qua_cu.get("ma_tran_goc"), them.get("ma_tran_goc"))
        if "kiem_ke_cong_thuc" in ket_qua_cu or "kiem_ke_cong_thuc" in them:
            tong_hop["kiem_ke_cong_thuc"] = gop_kiem_ke_cong_thuc(ket_qua_cu.get("kiem_ke_cong_thuc"), them.get("kiem_ke_cong_thuc"))
        return tong_hop, nguon, canh_bao
    except ai.AdmissionAIError as exc:
        nhan = "đọc lại nguồn" if doc_lai else "tìm bù"
        canh_bao.append(f"Chưa hoàn tất lượt {nhan}. {exc}")
        return None, nguon, canh_bao


def _cung_luot_tao(phien: DatsPhienThuThap | None, sua_lan: int) -> bool:
    return phien is not None and _dang_tao_ban_nhap(phien) and phien.sua_lan == sua_lan


def _phien_cua_luot_tao(db: Session, phien_id: int, sua_lan: int) -> DatsPhienThuThap:
    phien = db.get(DatsPhienThuThap, phien_id, populate_existing=True, with_for_update=True)
    if not _cung_luot_tao(phien, sua_lan):
        raise _DaDungTaoBanNhap
    return phien


def _ket_thuc_tao_ban_nhap(phien: DatsPhienThuThap, trang_thai: TrangThaiThuThap) -> None:
    phien.trang_thai = trang_thai
    phien.bat_dau_tao_ban_nhap_luc = None
    phien.tien_do_tao_ban_nhap = None


def _mo_khoa_tao_nhap_sau_loi(
    db: Session, phien_id: int, sua_lan: int, actor: tuple[int, str], exc: Exception,
) -> None:
    db.rollback()
    try:
        phien = db.get(DatsPhienThuThap, phien_id, populate_existing=True, with_for_update=True)
        if _cung_luot_tao(phien, sua_lan):
            _ket_thuc_tao_ban_nhap(phien, _trang_thai_truoc_khi_tao(phien))
            detail = exc.detail if isinstance(exc, HTTPException) else "Máy chủ gặp lỗi khi tạo bản nháp."
            thong_bao = detail if isinstance(detail, dict) else {"message": detail}
            _ghi_nhat_ky(db, phien, actor, _TAO_BAN_NHAP_THAT_BAI, sua_lan=sua_lan + 1,
                         message=thong_bao["message"], loi=thong_bao.get("loi", []), nguon_ids=thong_bao.get("nguon_ids", []))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Không thể cập nhật phiên %s sau lỗi tạo bản nháp", phien_id)


def _xu_ly_tao_ban_nhap(
    db: Session, phien_id: int, sua_lan: int, actor: tuple[int, str], truong: dict, nam: int,
    ds: list[dict], previous: dict | None, nguon_luu: list[dict], danh_muc_phuong_thuc: list[dict],
    tu_dong: bool, giu_chua_chon: set[int],
) -> bool:
    bo_nho = ai.BoNhoNguonThuThap() if tu_dong else None

    def bao_tien_do(buoc: str, da_xu_ly: int | None = None, tong: int | None = None) -> None:
        phien = _phien_cua_luot_tao(db, phien_id, sua_lan)
        phien.tien_do_tao_ban_nhap = {"buoc": buoc, "da_xu_ly": da_xu_ly, "tong": tong}
        db.commit()

    def trich_xuat(cac_nguon, goi_y):
        nam_lich_su = {
            n["nam_ap_dung"] for n in cac_nguon
            if n.get("chi_diem_lich_su") and type(n.get("nam_ap_dung")) is int and n["nam_ap_dung"] < nam
        }
        # Trang đề án có thể đăng lại điểm của hai mùa trước ngay trong cùng bảng.
        nam_lich_su.update(range(max(1990, nam - 2), nam))
        with Session(db.get_bind()) as db_danh_muc:
            danh_muc_lich_su = {nam_cu: _danh_muc_phuong_thuc(db_danh_muc, nam_cu) for nam_cu in sorted(nam_lich_su)}
        return ai.extract_draft(
            truong, nam, cac_nguon, goi_y, bao_tien_do=bao_tien_do, danh_muc_phuong_thuc=danh_muc_phuong_thuc,
            danh_muc_lich_su=danh_muc_lich_su,
            **({"chi_html": True, "bo_nho": bo_nho, "nghien_cuu_truoc": True} if tu_dong else {}),
        )

    def luu_nguon(nguon: list[dict], ghi_chu_moi: list[str]) -> None:
        if bo_nho is not None:
            bo_nho.bo_qua_url(n["url"] for n in nguon if n["lua_chon"] == "loai"
                              or (n["id"] in giu_chua_chon and n["lua_chon"] == "chua_chon"))
        phien = _phien_cua_luot_tao(db, phien_id, sua_lan)
        phien.nguon = nguon
        phien.canh_bao_nguon = list(dict.fromkeys([*canh_bao_nguon, *ghi_chu_moi]))
        db.commit()

    def lap_ban(ket_qua, nguon):
        if tu_dong:
            ids = set(ket_qua.get("nguon_ids", [n["id"] for n in nguon]))
            if "ma_tran_goc" in ket_qua:
                chieu_danh_muc(ket_qua)
            if "kiem_ke_cong_thuc" in ket_qua:
                ket_qua["cong_thuc_da_doi_chieu"] = chieu_cong_thuc_vao_ban_nhap(
                    truong, nam, ket_qua, ket_qua["kiem_ke_cong_thuc"], bao_tien_do)
            doi_chieu_lien_ket_ai(truong, nam, ket_qua, [n for n in nguon if n["id"] in ids],
                                  danh_muc_phuong_thuc, bao_tien_do)
            if "cong_thuc_da_doi_chieu" in ket_qua:
                doi_chieu_sau_khi_noi_cong_thuc(ket_qua, ket_qua["cong_thuc_da_doi_chieu"])
        return _lap_ban_nhap(ket_qua, truong, nam, nguon)

    def tim_nguon_thay_the(nguon):
        bao_tien_do("tim_bo_sung")
        try:
            moi, ghi_chu = ai.search_missing_sources(truong, nam, [
                f"Trang HTML chính thức công bố thông tin tuyển sinh {nam}, danh sách mã xét tuyển và phương thức của trường."
            ], [n["url"] for n in nguon])
            nguon = _chon_nguon_tu_dong(nguon, moi, nam, giu_chua_chon)
            canh_bao_nguon.extend(ghi_chu)
        except ai.AdmissionAIError as exc:
            canh_bao_nguon.append(str(exc))
        luu_nguon(nguon, [])
        return nguon

    def nguon_da_chon(nguon):
        return [n for n in nguon if n["lua_chon"] == "su_dung" and _nguon_hop_le(n, nam) and _nguon_html(n)]

    canh_bao_nguon = []
    loi_sau_khi_doc_lai = {}
    try:
        if tu_dong:
            bao_tien_do("tim_nguon")
            try:
                moi, canh_bao_nguon = ai.search_sources(truong, nam)
            except ai.AdmissionAIError as exc:
                moi, canh_bao_nguon = [], [str(exc)]
            nguon_luu = _chon_nguon_tu_dong(nguon_luu, moi, nam, giu_chua_chon)
            ds = nguon_da_chon(nguon_luu)
            luu_nguon(nguon_luu, [])
            if not any(_nguon_nam_hien_tai(n, nam) for n in ds):
                nguon_luu = tim_nguon_thay_the(nguon_luu)
                ds = nguon_da_chon(nguon_luu)
            if not any(_nguon_nam_hien_tai(n, nam) for n in ds):
                raise HTTPException(502, {
                    "message": "Chưa tìm được nguồn HTML chính thức đúng trường và năm để tạo bản nháp.",
                    "loi": canh_bao_nguon,
                })
        bao_tien_do("doc_nguon", 0, len(ds))
        try:
            da_trich = trich_xuat(ds, previous)
        except ai.LoiDocNguon:
            if not tu_dong:
                raise
            bao_tien_do("doc_lai_nguon")
            try:
                da_trich = trich_xuat(ds, previous)
            except ai.LoiDocNguon as exc:
                da_thu = {n["id"] for n in ds}
                nguon_luu = tim_nguon_thay_the(nguon_luu)
                ds = [n for n in nguon_da_chon(nguon_luu) if n["id"] not in da_thu]
                if not any(_nguon_nam_hien_tai(n, nam) for n in ds):
                    raise
                da_trich = trich_xuat(ds, previous)
                loi_sau_khi_doc_lai = dict(zip(exc.nguon_ids, exc.loi, strict=True))
        ban = lap_ban(da_trich, ds)
        muc_cu = (previous or {}).get("muc_con_thieu") or []
        thieu = ban.ra_soat(truong, nam, ds, muc_cu, bao_tien_do)
        if tu_dong:
            # Một lần đọc lại nguồn cũ, sau đó tối đa ba lượt khám phá HTML mới theo kết quả rà soát.
            for luot in range(4):
                doc_lai = luot == 0
                if not thieu and not (doc_lai and ban.loi_nguon):
                    break
                them, nguon_luu, canh_bao_bo_sung = _tim_bo_sung_ban_nhap(
                    truong, nam, nguon_luu, ban, da_trich, thieu, trich_xuat, bao_tien_do, luu_nguon, giu_chua_chon,
                    doc_lai=doc_lai,
                )
                canh_bao_nguon.extend(canh_bao_bo_sung)
                if them is None:
                    if doc_lai:
                        continue
                    ban.ghi_chu.extend(canh_bao_bo_sung)
                    break
                ban_cu = ban
                da_trich = them
                ban = lap_ban(da_trich, nguon_luu)
                thieu = ban.ra_soat(truong, nam, nguon_luu, thieu, bao_tien_do)
                if not doc_lai and thieu and ban.du_lieu == ban_cu.du_lieu and ban.muc == ban_cu.muc and not set(ban.nguon_ids).difference(ban_cu.nguon_ids):
                    ban.ghi_chu.append("Lượt tìm bù chưa bổ sung được dữ liệu, dẫn chứng hoặc nguồn đã đọc.")
                    break
            else:
                if thieu:
                    ban.ghi_chu.append("Đã thực hiện đủ ba lượt tìm nguồn bổ sung. Các mục còn thiếu được giữ để người duyệt đối chiếu.")
            ban.loi_nguon.update(loi_sau_khi_doc_lai)
            for n in nguon_luu:
                if n["lua_chon"] == "su_dung" and n["id"] not in ban.nguon_ids:
                    ban.loi_nguon.setdefault(n["id"], "Nguồn chưa được sử dụng trong lượt thu thập HTML này.")
        bao_tien_do("luu_ban_nhap")
        phien = _phien_cua_luot_tao(db, phien_id, sua_lan)
        so_ban_cu, ly_do_cu = phien.phien_ban, phien.yeu_cau_bo_sung
        nguon_cua_ban = [
            {**n, "lua_chon": "loai", "ly_do_loai": ban.loi_nguon[n["id"]]} if n["id"] in ban.loi_nguon else n
            for n in nguon_luu
        ]
        if tu_dong:
            phien.nguon = nguon_luu
            phien.canh_bao_nguon = list(dict.fromkeys(canh_bao_nguon))
        _them_ban(db, phien, actor[1], ban.du_lieu, ban.muc, ban.ghi_chu, nguon_cua_ban, ban.doi_chieu)
        _ket_thuc_tao_ban_nhap(phien, CHO_DUYET)
        phien.yeu_cau_bo_sung = None
        _ghi_nhat_ky(db, phien, actor, "tao_ban_nhap", nguon_ids=ban.nguon_ids, loi_nguon=ban.loi_nguon,
                     phien_ban_truoc=so_ban_cu, yeu_cau_bo_sung=ly_do_cu)
        db.commit()
        return True
    except _DaDungTaoBanNhap:
        db.rollback()
        return False
    except ai.AdmissionAIError as exc:
        detail = {"message": str(exc), "loi": exc.loi, "nguon_ids": exc.nguon_ids} if isinstance(exc, ai.LoiDocNguon) else str(exc)
        loi = HTTPException(502, detail)
        _mo_khoa_tao_nhap_sau_loi(db, phien_id, sua_lan, actor, loi)
        raise loi from exc
    except Exception as exc:
        _mo_khoa_tao_nhap_sau_loi(db, phien_id, sua_lan, actor, exc)
        raise


async def _tao_ban_nhap_nen(bind, phien_id: int, *tham_so) -> None:
    def chay() -> None:
        with Session(bind=bind, autoflush=False) as db:
            try:
                _xu_ly_tao_ban_nhap(db, phien_id, *tham_so)
            except HTTPException:
                pass  # Thông báo đã được lưu để trang thu thập hiển thị.
            except Exception:
                logger.exception("Lỗi khi tạo bản nháp cho phiên %s", phien_id)

    await asyncio.to_thread(chay)


@router.post("/phien/{phien_id}/tao-ban-nhap", response_model=PhienThuThapDetail, status_code=202)
def tao_ban_nhap(
    phien_id: int, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
    tac_vu: BackgroundTasks = None, tu_dong: bool = False,
):
    """Tạo nháp từ nguồn đã chọn hoặc tự tìm, đối chiếu và tìm bù các mục còn thiếu."""
    phien, truong, actor, sua_lan_truoc = _chuan_bi_ai(db, phien_id, user, khoa=True)
    nam = phien.nam_tuyen_sinh
    ds = [n for n in phien.nguon if n["lua_chon"] == "su_dung" and _nguon_hop_le(n, nam)]
    if not tu_dong and not any(_nguon_nam_hien_tai(n, nam) for n in ds):
        raise HTTPException(422, "Hãy chọn ít nhất một nguồn tuyển sinh chính thức đúng trường và năm trước khi tạo bản nháp.")
    danh_muc_phuong_thuc = _danh_muc_phuong_thuc(db, nam)
    so_ban_cu, ly_do_cu = phien.phien_ban, phien.yeu_cau_bo_sung
    cu = _ban_nhap(db, phien_id, so_ban_cu) if so_ban_cu else None
    previous = {"du_lieu": cu.du_lieu, "ghi_chu": cu.ghi_chu, "yeu_cau_bo_sung": ly_do_cu,
                "muc_con_thieu": (cu.doi_chieu or {}).get("muc_con_thieu")} if cu else None
    nguon_luu = phien.nguon
    giu_chua_chon = set()
    if tu_dong:
        lua_chon_cu = db.scalars(select(DatsNhatKyThuThap.chi_tiet).where(
            DatsNhatKyThuThap.phien_id == phien_id, DatsNhatKyThuThap.hanh_dong == "chon_nguon",
        ))
        giu_chua_chon = {item["nguon_id"] for item in lua_chon_cu if item.get("sau") == "chua_chon"}
    sua_lan = sua_lan_truoc + 1
    phien.trang_thai = _DANG_TAO_BAN_NHAP
    phien.sua_lan = sua_lan
    luc_bat_dau = bay_gio()
    phien.cap_nhat_luc = luc_bat_dau
    phien.bat_dau_tao_ban_nhap_luc = luc_bat_dau
    phien.tien_do_tao_ban_nhap = {"buoc": "tim_nguon" if tu_dong else "doc_nguon", "da_xu_ly": 0, "tong": None if tu_dong else len(ds)}
    db.commit()  # Công khai trạng thái và trả kết nối trước khi đọc nguồn, gọi AI.

    tham_so = (sua_lan, actor, truong, nam, ds, previous, nguon_luu, danh_muc_phuong_thuc, tu_dong, giu_chua_chon)
    if tac_vu is not None:
        try:
            ket_qua = _chi_tiet(db, phien_id)
            db.rollback()
            tac_vu.add_task(_tao_ban_nhap_nen, db.get_bind(), phien_id, *tham_so)
        except Exception as exc:
            _mo_khoa_tao_nhap_sau_loi(db, phien_id, sua_lan, actor, exc)
            raise
        return ket_qua
    if not _xu_ly_tao_ban_nhap(db, phien_id, *tham_so):
        raise HTTPException(409, _DA_THAY_DOI)
    return _chi_tiet(db, phien_id)


@router.post("/phien/{phien_id}/dung-tao-ban-nhap", response_model=PhienThuThapDetail)
def dung_tao_ban_nhap(
    phien_id: int, yeu_cau: DungTaoBanNhap, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
):
    """Dừng lượt tạo đã chọn và trả phiên về bước trước khi tạo."""
    phien = _phien(db, phien_id, khoa=True)
    if not _dang_tao_ban_nhap(phien):
        db.rollback()
        return _chi_tiet(db, phien_id)
    if phien.sua_lan != yeu_cau.luot_tao_ban_nhap:
        raise HTTPException(409, {"message": _DA_THAY_DOI, "dang_tao_ban_nhap": True})
    _ket_thuc_tao_ban_nhap(phien, _trang_thai_truoc_khi_tao(phien))
    _ghi_nhat_ky(db, phien, (user.id, user.ho_ten), "dung_tao_ban_nhap", luot_tao_ban_nhap=yeu_cau.luot_tao_ban_nhap)
    db.commit()
    return _chi_tiet(db, phien_id)


@router.patch("/phien/{phien_id}/ban-nhap", response_model=PhienThuThapDetail)
def sua_ban_nhap(phien_id: int, yeu_cau: SuaBanNhap, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user)):
    """Lưu giá trị, dẫn chứng và lý do sửa vào phiên bản mới, giữ nguyên lịch sử."""
    phien = _phien(db, phien_id, khoa=True)
    _cho_duyet(phien, yeu_cau.phien_ban)
    ban = _ban_nhap(db, phien_id, yeu_cau.phien_ban, khoa=True)
    try:
        du_lieu, muc, thay_doi = sua_muc_ban_nhap(ban.du_lieu, ban.muc, yeu_cau.thay_doi, ban.nguon)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    truoc = ban.doi_chieu or {}
    ly_do_cu = truoc.get("xac_nhan", {})
    ly_do_moi = yeu_cau.xac_nhan_doi_chieu.model_dump(exclude_unset=True) if yeu_cau.xac_nhan_doi_chieu else {}
    nguon_cua_ban = {n["id"] for n in ban.nguon}
    if any(can_cu and can_cu["nguon_id"] not in nguon_cua_ban for can_cu in ly_do_moi.values()):
        raise HTTPException(422, "Nguồn đối chiếu không thuộc phiên bản đang xét duyệt.")
    xac_nhan = {} if du_lieu != ban.du_lieu else ly_do_cu.copy()
    for khoa, ly_do in ly_do_moi.items():
        if ly_do:
            xac_nhan[khoa] = ly_do
        else:
            xac_nhan.pop(khoa, None)
    if thay_doi or du_lieu != ban.du_lieu or xac_nhan != ly_do_cu:
        doi_chieu = {**truoc, "xac_nhan": xac_nhan}
        if ra_soat := doi_chieu.get("ra_soat_diem_chuan"):
            doi_chieu["diem_chuan"] = bao_cao_diem_ai(ra_soat, du_lieu, muc)
        elif doi_chieu.get("diem_chuan") and any(
            t["duong_dan"].startswith("/quy_tac_xet_tuyen/diem_chuan") for t in thay_doi
        ):
            # Bản trước giữ nguyên số liệu kiểm kê cũ; bản vừa sửa chưa được AI rà soát.
            doi_chieu.pop("diem_chuan", None)
            doi_chieu.pop("kiem_ke_diem_chuan", None)
        if (thay_doi or du_lieu != ban.du_lieu) and (
            "trang_thai_ra_soat_ai" in truoc or truoc.get("muc_con_thieu") is not None
            or "ma_tran" in truoc or "cong_thuc" in truoc
        ):
            doi_chieu["trang_thai_ra_soat_ai"] = "da_chinh_sua"
        _them_ban(db, phien, user.ho_ten, du_lieu, muc, ban.ghi_chu, ban.nguon, doi_chieu)
        _ghi_nhat_ky(
            db, phien, (user.id, user.ho_ten), "sua_ban_nhap", phien_ban_truoc=ban.phien_ban, thay_doi=thay_doi,
            xac_nhan_doi_chieu=xac_nhan,
        )
    db.commit()
    return _chi_tiet(db, phien_id)


@router.post("/phien/{phien_id}/yeu-cau-bo-sung", response_model=PhienThuThapDetail)
def yeu_cau_bo_sung(
    phien_id: int, yeu_cau: BoSungBanNhap, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
):
    """Trả bản nháp về bước thu thập cùng các mục và lý do cần bổ sung."""
    phien = _phien(db, phien_id, khoa=True)
    _cho_duyet(phien, yeu_cau.phien_ban)
    ban = _ban_nhap(db, phien_id, yeu_cau.phien_ban, khoa=True)
    duong_dan = list(dict.fromkeys(yeu_cau.duong_dan))
    if set(duong_dan) - {m["duong_dan"] for m in ban.muc}:
        raise HTTPException(422, "Có mục yêu cầu bổ sung không thuộc bản nháp đang mở.")
    phien.yeu_cau_bo_sung = {"duong_dan": duong_dan, "ly_do": yeu_cau.ly_do}
    phien.trang_thai = BO_SUNG
    _ghi_nhat_ky(db, phien, (user.id, user.ho_ten), "yeu_cau_bo_sung", **phien.yeu_cau_bo_sung)
    db.commit()
    return _chi_tiet(db, phien_id)


def _de_an_trung(db: Session, ma: str, nam: int) -> int | None:
    return db.scalar(select(DatsTuyenSinh.id).where(DatsTuyenSinh.ma_truong == ma, DatsTuyenSinh.nam_tuyen_sinh == nam))


def _bao_trung(de_an_id: int) -> HTTPException:
    return HTTPException(409, {"message": "Đã có đề án cho cùng mã trường và năm tuyển sinh.", "de_an_id": de_an_id})


def _da_nhap(db: Session, phien: DatsPhienThuThap) -> int | None:
    de_an_id = phien.de_an_id
    db.commit()
    return de_an_id


def _duyet(db: Session, phien_id: int, phien_ban: int, actor: tuple[int, str]) -> int | None:
    phien = _phien(db, phien_id, khoa=True)
    if phien.trang_thai == DA_DUYET and phien.phien_ban == phien_ban:
        return _da_nhap(db, phien)
    _cho_duyet(phien, phien_ban)
    ban = _ban_nhap(db, phien_id, phien_ban, khoa=True)
    ma, nam = phien.ma_truong, phien.nam_tuyen_sinh
    trung = _de_an_trung(db, ma, nam)
    if trung is not None:
        raise _bao_trung(trung)
    loi, _ = _kiem_tra_ban_nhap(phien, ban)
    if loi:
        raise HTTPException(422, {"message": "Bản nháp còn mục cần xử lý trước khi duyệt.", "loi": loi})
    try:
        de_an_id, so_dong, quy_tac = import_approved_admission(db, ban.du_lieu, ma, nam, actor[0])
        phien.de_an_id = de_an_id
        phien.trang_thai = DA_DUYET
        phien.duyet_boi, phien.duyet_luc = actor[0], bay_gio()
        _ghi_nhat_ky(db, phien, actor, "duyet", de_an_id=de_an_id, so_dong=so_dong,
                     quy_tac=quy_tac.so_dong if quy_tac else {}, canh_bao=quy_tac.canh_bao if quy_tac else [])
        db.commit()
        return de_an_id
    except (DatsImportError, IntegrityError) as exc:
        db.rollback()
        trung = _de_an_trung(db, ma, nam)
        if trung is not None:
            # Kiểm tra lại phiên nếu một yêu cầu khác đã hoàn tất trong lúc rollback.
            phien = _phien(db, phien_id, khoa=True)
            if phien.trang_thai == DA_DUYET and phien.phien_ban == phien_ban:
                return _da_nhap(db, phien)
            raise _bao_trung(trung) from exc
        if isinstance(exc, DatsImportError):
            raise HTTPException(422, {"message": "Không thể nhập đề án.", "loi": exc.loi}) from exc
        logger.exception("Lỗi ràng buộc khi nhập đề án từ phiên %s phiên bản %s", phien_id, phien_ban)
        raise HTTPException(422, "Dữ liệu nhập vi phạm ràng buộc trong MySQL. Phiên vẫn đang Chờ duyệt.") from exc


def _duyet_co_thu_lai(db: Session, phien_id: int, phien_ban: int, actor: tuple[int, str]) -> int | None:
    for lan in range(3):
        try:
            return _duyet(db, phien_id, phien_ban, actor)
        except DBAPIError as exc:
            db.rollback()
            if lan < 2 and exc.orig.args and exc.orig.args[0] in (1205, 1213):
                continue
            logger.exception("Lỗi MySQL khi duyệt phiên %s", phien_id)
            raise HTTPException(503, "MySQL chưa hoàn tất việc nhập. Hãy mở lại phiên để kiểm tra kết quả.") from exc
    raise AssertionError("Vòng duyệt đã hoàn tất hoặc đã trả lỗi.")


@router.post("/phien/{phien_id}/duyet", response_model=PhienThuThapDetail)
def duyet_va_nhap(
    phien_id: int, yeu_cau: PhienBanRequest, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
):
    """Duyệt đúng phiên bản và nhập đề án cùng quy tắc trong một giao dịch."""
    _duyet_co_thu_lai(db, phien_id, yeu_cau.phien_ban, (user.id, user.ho_ten))
    return _chi_tiet(db, phien_id)


@router.post("/phien/duyet-hang-loat", response_model=DuyetHangLoatResult)
def duyet_hang_loat(
    yeu_cau: DuyetHangLoatRequest, db: Session = Depends(get_db), user: NguoiDung = Depends(get_admin_user),
) -> DuyetHangLoatResult:
    """Duyệt danh sách phiên đã xác nhận và trả kết quả riêng cho từng phiên bản."""
    actor = (user.id, user.ho_ten)
    ket_qua = DuyetHangLoatResult()
    for phien in yeu_cau.phien:
        try:
            de_an_id = _duyet_co_thu_lai(db, phien.id, phien.phien_ban, actor)
            if de_an_id is None:
                raise HTTPException(409, "Phiên đã duyệt nhưng đề án liên kết hiện không còn.")
        except HTTPException as exc:
            db.rollback()
            ket_qua.that_bai.append(PhienDuyetThatBai(
                id=phien.id, phien_ban=phien.phien_ban, status=exc.status_code, detail=exc.detail,
            ))
        except Exception:
            db.rollback()
            logger.exception("Lỗi khi duyệt hàng loạt phiên %s phiên bản %s", phien.id, phien.phien_ban)
            ket_qua.that_bai.append(PhienDuyetThatBai(
                id=phien.id, phien_ban=phien.phien_ban, status=500,
                detail="Chưa xác nhận được kết quả. Hãy mở lại phiên để kiểm tra.",
            ))
        else:
            ket_qua.da_duyet.append(PhienDaDuyetHangLoat(id=phien.id, phien_ban=phien.phien_ban, de_an_id=de_an_id))
    return ket_qua


@router.get("/phien/{phien_id}/json", response_class=Response)
def tai_json(phien_id: int, db: Session = Depends(get_db)):
    """Tải JSON UTF-8 của phiên bản đã dùng để nhập."""
    phien = _phien(db, phien_id)
    if phien.trang_thai != DA_DUYET or phien.phien_ban is None:
        raise HTTPException(409, "Chỉ tải được JSON sau khi phiên đã duyệt và nhập.")
    ban = _ban_nhap(db, phien_id, phien.phien_ban)
    ma = ban.du_lieu["thong_tin_import"]["ma_truong"]
    ten_file = f"{ma}_{phien.nam_tuyen_sinh}_tuyen_sinh.json"
    return Response(
        json.dumps(ban.du_lieu, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(ten_file, safe='')}", "Cache-Control": "no-store"},
    )
