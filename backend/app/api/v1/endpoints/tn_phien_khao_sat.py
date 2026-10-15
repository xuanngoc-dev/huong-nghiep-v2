import re
import secrets
import string
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.db.session import get_db
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.nguoi_dung import NguoiDung
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat
from app.schemas.tn_phien_khao_sat import (
    TnPhienBuocPublic,
    TnPhienCauHoiPublic,
    TnPhienCauTraLoiPublic,
    TnPhienDiemHolland,
    TnPhienKetQuaPublic,
    TnPhienKhaoSatPublic,
    TnPhienLamBaiPublic,
    TnPhienTraLoiWrite,
)

router = APIRouter(prefix="/trac-nghiem/phien", tags=["trac-nghiem"])

_SSID_ALPHABET = string.ascii_letters + string.digits
_SSID_LENGTH = 20
_SO_CAU_MOI_MA = 2
_VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_MA_CAU_HOI = re.compile(r"^[A-Z]\d+_\d+:\s*")


def _new_ssid(db: Session) -> str:
    """Sinh ssid 20 ký tự, thử lại nếu trùng."""
    for _ in range(5):
        ssid = "".join(secrets.choice(_SSID_ALPHABET) for _ in range(_SSID_LENGTH))
        exists = db.scalar(select(TnPhienKhaoSat.id).where(TnPhienKhaoSat.ssid == ssid))
        if exists is None:
            return ssid
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Không tạo được mã phiên khảo sát",
    )


def _ma_giao_dich(phien_id: int) -> str:
    """Mã giao dịch dạng KS_dd/mm/yy_id theo giờ Việt Nam."""
    now = datetime.now(_VN_TZ)
    return f"KS_{now:%d/%m/%y}_{phien_id}"


def _chon_cau_hoi(db: Session) -> list[tuple[int, int]]:
    """Mỗi loại câu hỏi đang hoạt động, mỗi mã Holland đang hoạt động, lấy ngẫu nhiên 2 câu."""
    loai_list = db.scalars(
        select(DmLoaiCauHoi)
        .where(DmLoaiCauHoi.trang_thai == 1)
        .order_by(DmLoaiCauHoi.thu_tu_uu_tien.asc())
    ).all()
    holland_list = db.scalars(
        select(DmNhomTinhCachHolland)
        .where(DmNhomTinhCachHolland.trang_thai == 1)
        .order_by(DmNhomTinhCachHolland.ma_nhom.asc())
    ).all()
    if not loai_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chưa có loại câu hỏi đang hoạt động",
        )
    if not holland_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chưa có nhóm tính cách Holland đang hoạt động",
        )

    rows = db.execute(
        select(
            TnCauHoiTracNghiem.id,
            TnCauHoiTracNghiem.loai_cau_hoi_id,
            TnCauHoiTracNghiem.ma_holand,
        ).where(TnCauHoiTracNghiem.trang_thai == 1)
    ).all()
    grouped: dict[tuple[int, str], list[int]] = defaultdict(list)
    for cau_hoi_id, loai_cau_hoi_id, ma_holand in rows:
        grouped[(loai_cau_hoi_id, ma_holand)].append(cau_hoi_id)

    picked: list[tuple[int, int]] = []
    shortages: list[str] = []
    for loai in loai_list:
        for holland in holland_list:
            candidates = grouped.get((loai.id, holland.ma_nhom), [])
            if len(candidates) < _SO_CAU_MOI_MA:
                shortages.append(
                    f"{loai.ten_loai_cau_hoi} / {holland.ma_nhom} (có {len(candidates)})"
                )
                continue
            for cau_hoi_id in secrets.SystemRandom().sample(candidates, _SO_CAU_MOI_MA):
                picked.append((loai.id, cau_hoi_id))

    if shortages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không đủ 2 câu hỏi cho: " + "; ".join(shortages),
        )
    return picked


@router.post("", response_model=TnPhienKhaoSatPublic, status_code=status.HTTP_201_CREATED)
def bat_dau_holland(
    db: Session = Depends(get_db),
    current_user: NguoiDung | None = Depends(get_optional_user),
) -> TnPhienKhaoSatPublic:
    """Tạo phiên khảo sát Holland và gán danh sách câu hỏi cho phiên đó."""
    picked = _chon_cau_hoi(db)
    phien = TnPhienKhaoSat(
        ssid=_new_ssid(db),
        nguoi_khao_sat_id=current_user.id if current_user else None,
    )
    db.add(phien)
    db.flush()
    phien.ma_giao_dich = _ma_giao_dich(phien.id)
    for loai_cau_hoi_id, cau_hoi_id in picked:
        db.add(
            TnChiTietTraLoi(
                ssid=phien.ssid,
                loai_cau_hoi_id=loai_cau_hoi_id,
                cau_hoi_id=cau_hoi_id,
            )
        )
    db.commit()
    db.refresh(phien)
    return TnPhienKhaoSatPublic(
        id=phien.id,
        ssid=phien.ssid,
        nguoi_khao_sat_id=phien.nguoi_khao_sat_id,
        ma_giao_dich=phien.ma_giao_dich,
        loai_cau_hoi_id=picked[0][0],
        so_cau_hoi=len(picked),
        created_at=phien.created_at,
    )


def _noi_dung_hien_thi(text: str) -> str:
    """Bỏ mã nội bộ dạng R6_01 ở đầu câu trước khi đưa ra bài làm."""
    cleaned = _MA_CAU_HOI.sub("", text).strip()
    return cleaned or text.strip()


@router.get("/{ssid}", response_model=TnPhienLamBaiPublic)
def lay_de_bai(ssid: str, db: Session = Depends(get_db)) -> TnPhienLamBaiPublic:
    """Lấy danh sách câu hỏi đã gán cho một phiên, sắp theo thứ tự loại câu hỏi."""
    phien = db.scalar(select(TnPhienKhaoSat).where(TnPhienKhaoSat.ssid == ssid))
    if phien is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên khảo sát")

    rows = db.execute(
        select(TnChiTietTraLoi, TnCauHoiTracNghiem, DmLoaiCauHoi)
        .join(TnCauHoiTracNghiem, TnChiTietTraLoi.cau_hoi_id == TnCauHoiTracNghiem.id)
        .join(DmLoaiCauHoi, TnChiTietTraLoi.loai_cau_hoi_id == DmLoaiCauHoi.id)
        .where(TnChiTietTraLoi.ssid == ssid)
        .order_by(DmLoaiCauHoi.thu_tu_uu_tien.asc(), TnChiTietTraLoi.id.asc())
    ).all()
    question_ids = [cau_hoi.id for _chi_tiet, cau_hoi, _loai in rows]
    answers: dict[int, list[TnCauTraLoi]] = defaultdict(list)
    if question_ids:
        for answer in db.scalars(
            select(TnCauTraLoi)
            .where(TnCauTraLoi.cau_hoi_id.in_(question_ids))
            .order_by(TnCauTraLoi.diem.desc(), TnCauTraLoi.id.asc())
        ).all():
            answers[answer.cau_hoi_id].append(answer)

    return TnPhienLamBaiPublic(
        ssid=phien.ssid,
        ma_giao_dich=phien.ma_giao_dich,
        cau_hoi=[
            TnPhienCauHoiPublic(
                id=chi_tiet.id,
                loai_cau_hoi_id=loai.id,
                ten_loai_cau_hoi=loai.ten_loai_cau_hoi,
                noi_dung_cau_hoi=_noi_dung_hien_thi(cau_hoi.noi_dung_cau_hoi),
                cau_tra_loi_id=chi_tiet.cau_tra_loi_id,
                cau_tra_loi=[
                    TnPhienCauTraLoiPublic(
                        id=answer.id,
                        noi_dung_cau_tra_loi=answer.noi_dung_cau_tra_loi,
                        diem=answer.diem,
                    )
                    for answer in answers.get(cau_hoi.id, [])
                ],
            )
            for chi_tiet, cau_hoi, loai in rows
        ],
    )


def _phien_or_404(db: Session, ssid: str) -> TnPhienKhaoSat:
    phien = db.scalar(select(TnPhienKhaoSat).where(TnPhienKhaoSat.ssid == ssid))
    if phien is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phiên khảo sát")
    return phien


@router.put("/{ssid}/chi-tiet/{chi_tiet_id}", response_model=TnPhienCauHoiPublic)
def luu_tra_loi(
    ssid: str,
    chi_tiet_id: int,
    payload: TnPhienTraLoiWrite,
    db: Session = Depends(get_db),
) -> TnPhienCauHoiPublic:
    """Lưu đáp án của một câu trong phiên và điểm tương ứng."""
    _phien_or_404(db, ssid)
    chi_tiet = db.get(TnChiTietTraLoi, chi_tiet_id)
    if chi_tiet is None or chi_tiet.ssid != ssid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi trong phiên")
    answer = db.get(TnCauTraLoi, payload.cau_tra_loi_id)
    if answer is None or answer.cau_hoi_id != chi_tiet.cau_hoi_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đáp án không thuộc câu hỏi này")
    loai = db.get(DmLoaiCauHoi, chi_tiet.loai_cau_hoi_id)
    cau_hoi = db.get(TnCauHoiTracNghiem, chi_tiet.cau_hoi_id)
    if loai is None or cau_hoi is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi trong phiên")
    chi_tiet.cau_tra_loi_id = answer.id
    chi_tiet.diem_dat_duoc = answer.diem
    db.commit()
    return TnPhienCauHoiPublic(
        id=chi_tiet.id,
        loai_cau_hoi_id=loai.id,
        ten_loai_cau_hoi=loai.ten_loai_cau_hoi,
        noi_dung_cau_hoi=_noi_dung_hien_thi(cau_hoi.noi_dung_cau_hoi),
        cau_tra_loi_id=chi_tiet.cau_tra_loi_id,
        cau_tra_loi=[],
    )


@router.get("/{ssid}/ket-qua", response_model=TnPhienKetQuaPublic)
def lay_ket_qua(ssid: str, db: Session = Depends(get_db)) -> TnPhienKetQuaPublic:
    """Cộng điểm Holland của phiên theo đáp án đã lưu."""
    phien = _phien_or_404(db, ssid)
    tong = db.scalar(select(func.count()).select_from(TnChiTietTraLoi).where(TnChiTietTraLoi.ssid == ssid)) or 0
    da_tra_loi = (
        db.scalar(
            select(func.count())
            .select_from(TnChiTietTraLoi)
            .where(TnChiTietTraLoi.ssid == ssid, TnChiTietTraLoi.cau_tra_loi_id.is_not(None))
        )
        or 0
    )
    diem_rows = db.execute(
        select(TnCauHoiTracNghiem.ma_holand, func.coalesce(func.sum(TnChiTietTraLoi.diem_dat_duoc), 0))
        .join(TnCauHoiTracNghiem, TnChiTietTraLoi.cau_hoi_id == TnCauHoiTracNghiem.id)
        .where(TnChiTietTraLoi.ssid == ssid)
        .group_by(TnCauHoiTracNghiem.ma_holand)
    ).all()
    diem_theo_ma = {ma: int(diem or 0) for ma, diem in diem_rows}
    nhom = [
        TnPhienDiemHolland(ma_nhom=item.ma_nhom, ten_nhom=item.ten_nhom, diem=diem_theo_ma.get(item.ma_nhom, 0))
        for item in db.scalars(
            select(DmNhomTinhCachHolland)
            .where(DmNhomTinhCachHolland.trang_thai == 1)
            .order_by(DmNhomTinhCachHolland.ma_nhom.asc())
        ).all()
    ]
    nhom.sort(key=lambda item: (-item.diem, item.ma_nhom))
    buoc_rows = db.execute(
        select(DmLoaiCauHoi.id, DmLoaiCauHoi.ten_loai_cau_hoi)
        .join(TnChiTietTraLoi, TnChiTietTraLoi.loai_cau_hoi_id == DmLoaiCauHoi.id)
        .where(TnChiTietTraLoi.ssid == ssid)
        .group_by(DmLoaiCauHoi.id, DmLoaiCauHoi.ten_loai_cau_hoi, DmLoaiCauHoi.thu_tu_uu_tien)
        .order_by(DmLoaiCauHoi.thu_tu_uu_tien.asc())
    ).all()
    return TnPhienKetQuaPublic(
        ssid=phien.ssid,
        ma_giao_dich=phien.ma_giao_dich,
        so_cau_hoi=tong,
        so_da_tra_loi=da_tra_loi,
        ma_noi_bat="".join(item.ma_nhom for item in nhom[:3] if item.diem > 0),
        buoc=[TnPhienBuocPublic(id=loai_id, ten=ten) for loai_id, ten in buoc_rows],
        nhom=nhom,
    )
