import hashlib
import json
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.nguoi_dung import NguoiDung
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn
from app.schemas.xt_quy_tac import (
    XtBangQuyDoiPublic,
    XtChuongTrinhPublic,
    XtCongThucPublic,
    XtDiemCongPublic,
    XtDieuKienPublic,
    XtHeSoMonPublic,
    XtImportRequest,
    XtImportResult,
    XtLichSuImportPublic,
    XtNhomDieuKienPublic,
    XtPhuongAnNhomPublic,
    XtQuyTacDeAn,
    XtThanhPhanPublic,
    XtTrangThaiResult,
    XtTrangThaiWrite,
)
from app.services.xet_tuyen_ghi import nhap_quy_tac
from app.services.xet_tuyen_import import XetTuyenImportError

# Quy tắc xét tuyển (xt_*) của một đề án: xem và import file JSON chuẩn. Chỉ quản trị viên.
router = APIRouter(prefix="/de-an-tuyen-sinh", tags=["de-an-tuyen-sinh"], dependencies=[Depends(get_admin_user)])

_SO_LICH_SU = 10


def _get_or_400(db: Session, item_id: int) -> DatsTuyenSinh:
    """Lấy đề án theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DatsTuyenSinh, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy đề án tuyển sinh có id = {item_id}",
        )
    return item


def _so(value) -> float | None:
    return None if value is None else float(value)


@router.get("/{item_id}/quy-tac", response_model=XtQuyTacDeAn)
def get_quy_tac(item_id: int, db: Session = Depends(get_db)) -> XtQuyTacDeAn:
    """Quy tắc xét tuyển của đề án: công thức, phương án theo chương trình, điều kiện, điểm cộng, lịch sử import."""
    de_an = _get_or_400(db, item_id)
    cong_thuc = list(db.scalars(select(XtCongThuc).where(XtCongThuc.de_an_id == item_id).order_by(XtCongThuc.id)))
    ma_cong_thuc = {ct.id: ct.ma_cong_thuc for ct in cong_thuc}
    ct_ids = list(ma_cong_thuc)
    so_phuong_an = dict(
        db.execute(
            select(XtPhuongAn.cong_thuc_id, func.count()).where(XtPhuongAn.de_an_id == item_id).group_by(XtPhuongAn.cong_thuc_id)
        ).all()
    )
    he_so: dict[int, list[XtHeSoMonPublic]] = defaultdict(list)
    thanh_phan: dict[int, list[XtThanhPhanPublic]] = defaultdict(list)
    if ct_ids:
        for hs, ma_mon in db.execute(
            select(XtCongThucHeSoMon, DmMonHoc.ma_mon_hoc)
            .outerjoin(DmMonHoc, XtCongThucHeSoMon.mon_hoc_id == DmMonHoc.id)
            .where(XtCongThucHeSoMon.cong_thuc_id.in_(ct_ids))
            .order_by(XtCongThucHeSoMon.id)
        ):
            he_so[hs.cong_thuc_id].append(XtHeSoMonPublic(ma_mon=ma_mon, nhom_mon=hs.nhom_mon, he_so=float(hs.he_so)))
        for tp, ma_bai_thi, ma_bang, ma_mon in db.execute(
            select(XtCongThucThanhPhan, DmBaiThiDanhGia.ma_bai_thi, XtBangQuyDoi.ma_bang, DmMonHoc.ma_mon_hoc)
            .outerjoin(DmBaiThiDanhGia, XtCongThucThanhPhan.bai_thi_id == DmBaiThiDanhGia.id)
            .outerjoin(XtBangQuyDoi, XtCongThucThanhPhan.bang_quy_doi_id == XtBangQuyDoi.id)
            .outerjoin(DmMonHoc, XtCongThucThanhPhan.mon_hoc_id == DmMonHoc.id)
            .where(XtCongThucThanhPhan.cong_thuc_id.in_(ct_ids))
            .order_by(XtCongThucThanhPhan.vi_tri, XtCongThucThanhPhan.id)
        ):
            thanh_phan[tp.cong_thuc_id].append(
                XtThanhPhanPublic(
                    vi_tri=tp.vi_tri,
                    ten_thanh_phan=tp.ten_thanh_phan,
                    loai_nguon=tp.loai_nguon,
                    ma_bai_thi=ma_bai_thi,
                    ma_bang=ma_bang,
                    ma_mon=ma_mon,
                    he_so=float(tp.he_so),
                )
            )

    chuong_trinh = list(
        db.scalars(
            select(DatsChuongTrinhDaoTao)
            .where(DatsChuongTrinhDaoTao.de_an_id == item_id)
            .order_by(DatsChuongTrinhDaoTao.ma_xet_tuyen, DatsChuongTrinhDaoTao.id)
        )
    )
    ma_xet_tuyen = {ct.id: ct.ma_xet_tuyen for ct in chuong_trinh}
    # (chương trình, công thức) → danh sách tổ hợp, giữ thứ tự công thức.
    phuong_an: dict[int, dict[int, list[str]]] = defaultdict(dict)
    for ct_id, cong_thuc_id, ma_to_hop in db.execute(
        select(XtPhuongAn.de_an_chuong_trinh_id, XtPhuongAn.cong_thuc_id, DmToHopMonHoc.ma_to_hop)
        .outerjoin(DmToHopMonHoc, XtPhuongAn.to_hop_id == DmToHopMonHoc.id)
        .where(XtPhuongAn.de_an_id == item_id)
        .order_by(XtPhuongAn.de_an_chuong_trinh_id, XtPhuongAn.cong_thuc_id, XtPhuongAn.id)
    ):
        ds = phuong_an[ct_id].setdefault(cong_thuc_id, [])
        if ma_to_hop:
            ds.append(ma_to_hop)

    nhom = list(
        db.scalars(select(XtNhomDieuKien).where(XtNhomDieuKien.de_an_id == item_id).order_by(XtNhomDieuKien.id))
    )
    dieu_kien: dict[int, list[XtDieuKienPublic]] = defaultdict(list)
    if nhom:
        for dk in db.scalars(
            select(XtDieuKien).where(XtDieuKien.nhom_dieu_kien_id.in_([n.id for n in nhom])).order_by(XtDieuKien.id)
        ):
            dieu_kien[dk.nhom_dieu_kien_id].append(
                XtDieuKienPublic(
                    ma_chi_so=dk.ma_chi_so,
                    khoa=dk.khoa,
                    toan_tu=dk.toan_tu,
                    gia_tri_so=float(dk.gia_tri_so),
                    mo_ta=dk.mo_ta,
                )
            )

    so_muc = dict(
        db.execute(
            select(XtBangQuyDoiChiTiet.bang_quy_doi_id, func.count())
            .join(XtBangQuyDoi, XtBangQuyDoiChiTiet.bang_quy_doi_id == XtBangQuyDoi.id)
            .where(XtBangQuyDoi.de_an_id == item_id)
            .group_by(XtBangQuyDoiChiTiet.bang_quy_doi_id)
        ).all()
    )
    lich_su = db.execute(
        select(XtLichSuImport, NguoiDung.ho_ten)
        .outerjoin(NguoiDung, XtLichSuImport.nguoi_import_id == NguoiDung.id)
        .where(XtLichSuImport.de_an_id == item_id)
        .order_by(XtLichSuImport.tao_luc.desc(), XtLichSuImport.id.desc())
        .limit(_SO_LICH_SU)
    ).all()

    return XtQuyTacDeAn(
        de_an_id=de_an.id,
        trang_thai_xet_tuyen=de_an.trang_thai_xet_tuyen or 0,
        cong_thuc=[
            XtCongThucPublic(
                id=ct.id,
                ma_cong_thuc=ct.ma_cong_thuc,
                ten_cong_thuc=ct.ten_cong_thuc,
                ma_phuong_thuc_cua_bo=ct.ma_phuong_thuc_cua_bo,
                kieu_tinh=ct.kieu_tinh,
                nguon_diem_mon=ct.nguon_diem_mon,
                thay_ngoai_ngu=ct.thay_ngoai_ngu,
                thang_diem=float(ct.thang_diem),
                he_so_nhan=float(ct.he_so_nhan),
                diem_san=_so(ct.diem_san),
                trang_thai=bool(ct.trang_thai),
                mo_ta_cong_thuc=ct.mo_ta_cong_thuc,
                so_phuong_an=so_phuong_an.get(ct.id, 0),
                he_so_mon=he_so.get(ct.id, []),
                thanh_phan=thanh_phan.get(ct.id, []),
            )
            for ct in cong_thuc
        ],
        chuong_trinh=[
            XtChuongTrinhPublic(
                id=ct.id,
                ma_xet_tuyen=ct.ma_xet_tuyen,
                ten_chuong_trinh=ct.ten_chuong_trinh,
                phuong_an=[
                    XtPhuongAnNhomPublic(ma_cong_thuc=ma_cong_thuc.get(cong_thuc_id, ""), to_hop=to_hop)
                    for cong_thuc_id, to_hop in phuong_an.get(ct.id, {}).items()
                ],
            )
            for ct in chuong_trinh
        ],
        nhom_dieu_kien=[
            XtNhomDieuKienPublic(
                id=n.id,
                ma_nhom=n.ma_nhom,
                ten_nhom=n.ten_nhom,
                mo_ta=n.mo_ta,
                bat_buoc=bool(n.bat_buoc),
                ma_cong_thuc=ma_cong_thuc.get(n.cong_thuc_id) if n.cong_thuc_id else None,
                ma_xet_tuyen=ma_xet_tuyen.get(n.de_an_chuong_trinh_id) if n.de_an_chuong_trinh_id else None,
                dieu_kien=dieu_kien.get(n.id, []),
            )
            for n in nhom
        ],
        diem_cong=[
            XtDiemCongPublic(
                id=d.id,
                ma_cong_thuc=ma_cong_thuc.get(d.cong_thuc_id) if d.cong_thuc_id else None,
                loai_diem_cong=d.loai_diem_cong,
                nhom_cong=d.nhom_cong,
                ma_chi_so=d.ma_chi_so,
                khoa=d.khoa,
                toan_tu=d.toan_tu,
                gia_tri_so=float(d.gia_tri_so),
                diem_cong=float(d.diem_cong),
                mo_ta=d.mo_ta,
            )
            for d in db.scalars(select(XtDiemCong).where(XtDiemCong.de_an_id == item_id).order_by(XtDiemCong.id))
        ],
        bang_quy_doi=[
            XtBangQuyDoiPublic(
                id=b.id,
                ma_bang=b.ma_bang,
                ten_bang=b.ten_bang,
                thang_diem_dich=float(b.thang_diem_dich),
                so_muc=so_muc.get(b.id, 0),
            )
            for b in db.scalars(select(XtBangQuyDoi).where(XtBangQuyDoi.de_an_id == item_id).order_by(XtBangQuyDoi.id))
        ],
        lich_su=[
            XtLichSuImportPublic(
                id=ls.id,
                ten_file=ls.ten_file,
                phien_ban_chuan=ls.phien_ban_chuan,
                so_dong=ls.so_dong,
                quy_dinh_chua_mo_hinh_hoa=ls.quy_dinh_chua_mo_hinh_hoa,
                nguoi_import=ho_ten,
                tao_luc=ls.tao_luc,
            )
            for ls, ho_ten in lich_su
        ],
    )


@router.patch("/{item_id}/quy-tac/trang-thai", response_model=XtTrangThaiResult)
def doi_trang_thai_quy_tac(item_id: int, payload: XtTrangThaiWrite, db: Session = Depends(get_db)) -> XtTrangThaiResult:
    """Đổi trạng thái quy tắc xét tuyển của đề án: 0 chưa chuẩn hóa, 1 thử nghiệm, 2 đang áp dụng.

    "Đang áp dụng" thì lượt tìm trường của người dùng trong năm đó chạy bộ tính mới; chỉ được chọn khi đề án đã có
    công thức (đã import quy tắc).
    """
    de_an = _get_or_400(db, item_id)
    if payload.trang_thai_xet_tuyen == 2 and not db.scalar(
        select(func.count()).select_from(XtCongThuc).where(XtCongThuc.de_an_id == item_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đề án chưa có quy tắc xét tuyển, hãy import quy tắc trước khi chuyển sang đang áp dụng",
        )
    de_an.trang_thai_xet_tuyen = payload.trang_thai_xet_tuyen
    de_an.cap_nhat_luc = datetime.now()
    db.commit()
    return XtTrangThaiResult(de_an_id=de_an.id, trang_thai_xet_tuyen=de_an.trang_thai_xet_tuyen)


@router.post("/{item_id}/quy-tac/import", response_model=XtImportResult)
def import_quy_tac(
    item_id: int,
    payload: XtImportRequest,
    db: Session = Depends(get_db),
    user: NguoiDung = Depends(get_admin_user),
) -> XtImportResult:
    """Import file JSON chuẩn quy tắc xét tuyển, thay toàn bộ quy tắc cũ của đề án trong một transaction.

    File phải đúng trường và năm của đề án. File lỗi thì trả 400 với `detail = {thong_bao, loi, canh_bao}` và không
    ghi dòng nào.
    """
    de_an = _get_or_400(db, item_id)
    du_lieu = payload.du_lieu
    ma_truong, nam = du_lieu.get("ma_truong"), du_lieu.get("nam_tuyen_sinh")
    if (ma_truong, nam) != (de_an.ma_truong, de_an.nam_tuyen_sinh):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File là quy tắc của trường {ma_truong or '?'} năm {nam or '?'}, không khớp đề án đang chọn "
                f"(trường {de_an.ma_truong} năm {de_an.nam_tuyen_sinh})"
            ),
        )
    ma_bam = hashlib.sha256(json.dumps(du_lieu, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    try:
        ket_qua = nhap_quy_tac(db, du_lieu, ten_file=payload.ten_file, ma_bam=ma_bam, nguoi_import_id=user.id)
        db.commit()
    except XetTuyenImportError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"thong_bao": str(exc), "loi": exc.loi, "canh_bao": exc.canh_bao},
        ) from None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được quy tắc xét tuyển (dữ liệu vi phạm ràng buộc của CSDL)",
        ) from None
    return XtImportResult(
        de_an_id=ket_qua.de_an_id,
        lich_su_id=ket_qua.lich_su_id,
        so_dong=ket_qua.so_dong,
        canh_bao=ket_qua.canh_bao,
        quy_dinh_chua_mo_hinh_hoa=ket_qua.quy_dinh_chua_mo_hinh_hoa,
    )
