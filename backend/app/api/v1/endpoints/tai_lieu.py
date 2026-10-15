from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_admin_user
from app.core.config import settings

from app.schemas.chat import TaiLieuItem
from app.services.tai_lieu import delete_tai_lieu, list_tai_lieu, save_tai_lieu

router = APIRouter(prefix="/tai-lieu", tags=["tai-lieu"], dependencies=[Depends(get_admin_user)])


@router.get("", response_model=list[TaiLieuItem])
def get_tai_lieu() -> list[TaiLieuItem]:
    """Danh sách file json/txt trong thư mục tài liệu."""
    return list_tai_lieu()


@router.post("", response_model=TaiLieuItem, status_code=status.HTTP_201_CREATED)
def post_tai_lieu(tep: UploadFile = File(...)) -> TaiLieuItem:
    """Tải một file .json hoặc .txt vào thư mục tài liệu."""
    return save_tai_lieu(tep.filename or "", tep.file.read(settings.tai_lieu_max_bytes + 1))


@router.delete("/{ten}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tai_lieu(ten: str) -> None:
    """Xóa một file tài liệu theo tên."""
    delete_tai_lieu(ten)
