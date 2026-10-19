from fastapi import APIRouter

from app.schemas.kiem_tra_du_lieu import TruongTuyenSinhTomTat
from app.services.kiem_tra_du_lieu import danh_sach_truong, noi_dung_truong

router = APIRouter(prefix="/kiem-tra-du-lieu", tags=["kiem-tra-du-lieu"])


@router.get("/truong", response_model=list[TruongTuyenSinhTomTat])
def get_truong() -> list[TruongTuyenSinhTomTat]:
    """Danh sách trường đọc từ các file JSON trong TAI_LIEU_DIR."""
    return danh_sach_truong()


@router.get("/noi-dung")
def get_noi_dung(ten_tep: str) -> dict:
    """Toàn bộ JSON tuyển sinh của một file trường."""
    return noi_dung_truong(ten_tep)
