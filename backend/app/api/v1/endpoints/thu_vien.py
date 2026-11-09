from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import get_admin_user
from app.schemas.thu_vien import (
    ThuVienDat,
    ThuVienDoiTen,
    ThuVienGiaiNen,
    ThuVienItem,
    ThuVienNen,
    ThuVienSoMuc,
    ThuVienTaoThuMuc,
    ThuVienTuUrl,
    ThuVienXoaNhieu,
)
from app.services.thu_vien import (
    delete_thu_vien,
    di_chuyen,
    doi_ten,
    giai_nen,
    list_thu_vien,
    media_type_for,
    nen_muc,
    resolve_thu_vien,
    sao_chep,
    save_thu_vien,
    tai_tu_url,
    tao_thu_muc,
    xoa_nhieu,
)

router = APIRouter(prefix="/thu-vien", tags=["thu-vien"])
_admin = [Depends(get_admin_user)]


@router.get("", response_model=list[ThuVienItem], dependencies=_admin)
def get_thu_vien(thu_muc: str = Query(default="", max_length=500)) -> list[ThuVienItem]:
    """Danh sách file và thư mục trong một cấp của thư viện."""
    return list_thu_vien(thu_muc)


@router.post("", response_model=ThuVienItem, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def post_thu_vien(
    tep: UploadFile = File(...),
    thu_muc: str = Form(default=""),
) -> ThuVienItem:
    """Tải một ảnh, video hoặc file nén vào thư mục hiện tại. Không ghi database."""
    return save_thu_vien(tep.filename or "", tep.file, thu_muc)


@router.post("/tu-url", response_model=ThuVienItem, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def post_thu_vien_tu_url(payload: ThuVienTuUrl) -> ThuVienItem:
    """Tải file từ URL về thư mục hiện tại và trả đường dẫn như upload từ thiết bị."""
    return tai_tu_url(payload.url, payload.thu_muc)


@router.post("/thu-muc", response_model=ThuVienItem, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def post_thu_muc(payload: ThuVienTaoThuMuc) -> ThuVienItem:
    """Tạo thư mục con trong thư mục hiện tại."""
    return tao_thu_muc(payload.thu_muc, payload.ten)


@router.post("/doi-ten", response_model=ThuVienItem, dependencies=_admin)
def post_doi_ten(payload: ThuVienDoiTen) -> ThuVienItem:
    """Đổi tên một file hoặc thư mục."""
    return doi_ten(payload.duong_dan, payload.ten_moi)


@router.post("/nen", response_model=ThuVienItem, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def post_nen(payload: ThuVienNen) -> ThuVienItem:
    """Nén các mục đang chọn trong thư mục hiện tại thành một file ZIP."""
    return nen_muc(payload.thu_muc, payload.danh_sach, payload.ten_tep)


@router.post("/sao-chep", response_model=ThuVienSoMuc, dependencies=_admin)
def post_sao_chep(payload: ThuVienDat) -> ThuVienSoMuc:
    """Sao chép các mục đã chọn vào thư mục đích."""
    return ThuVienSoMuc(so_muc=sao_chep(payload.danh_sach, payload.thu_muc_dich))


@router.post("/di-chuyen", response_model=ThuVienSoMuc, dependencies=_admin)
def post_di_chuyen(payload: ThuVienDat) -> ThuVienSoMuc:
    """Di chuyển các mục đã chọn vào thư mục đích."""
    return ThuVienSoMuc(so_muc=di_chuyen(payload.danh_sach, payload.thu_muc_dich))


@router.post("/xoa", response_model=ThuVienSoMuc, dependencies=_admin)
def post_xoa(payload: ThuVienXoaNhieu) -> ThuVienSoMuc:
    """Xóa nhiều file hoặc thư mục. Thư mục bị xóa cùng toàn bộ nội dung bên trong."""
    return ThuVienSoMuc(so_muc=xoa_nhieu(payload.danh_sach))


@router.post("/giai-nen", response_model=ThuVienItem, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def post_giai_nen(payload: ThuVienGiaiNen) -> ThuVienItem:
    """Giải nén một file ZIP hoặc TAR vào thư mục cùng cấp."""
    return giai_nen(payload.duong_dan)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, dependencies=_admin)
def remove_thu_vien(duong_dan: str = Query(min_length=1, max_length=500)) -> None:
    """Xóa một file hoặc cả thư mục."""
    delete_thu_vien(duong_dan)


@router.get("/tep/{duong_dan:path}")
def get_tep_thu_vien(duong_dan: str) -> FileResponse:
    """Đường dẫn công khai để dùng file đã tải lên."""
    path = resolve_thu_vien(duong_dan)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file.")
    return FileResponse(
        path,
        media_type=media_type_for(path.name),
        filename=path.name,
        content_disposition_type="inline",
    )
