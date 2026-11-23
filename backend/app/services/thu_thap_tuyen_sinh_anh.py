"""Chuẩn bị ảnh bảng tuyển sinh cho lượt nhận dạng văn bản."""

import base64
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

_DINH_DANG = {"JPEG", "PNG", "WEBP"}
_GIOI_HAN_PIXEL = 32_000_000
_CHIEU_RONG_TOI_DA = 2800
_CHIEU_CAO_MOI_PHAN = 1550
_CHONG_LAP = 145


def chuan_bi_anh(noi_dung: bytes, *, giu_anh_nho: bool = False) -> list[str]:
    """Chia ảnh dài thành các phần chồng lấn để giữ chữ nhỏ và đầy đủ hàng."""
    try:
        with Image.open(BytesIO(noi_dung)) as tep:
            if tep.format not in _DINH_DANG or tep.width * tep.height > _GIOI_HAN_PIXEL:
                raise ValueError("Ảnh không được hỗ trợ hoặc vượt giới hạn kích thước.")
            if min(tep.size) <= 1 or (not giu_anh_nho and (tep.width < 300 or tep.height < 150)):
                return []
            anh = ImageOps.exif_transpose(tep).convert("RGB")
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError) as exc:
        raise ValueError("Không đọc được ảnh bảng.") from exc

    if anh.width > _CHIEU_RONG_TOI_DA:
        cao = max(1, round(anh.height * _CHIEU_RONG_TOI_DA / anh.width))
        anh = anh.resize((_CHIEU_RONG_TOI_DA, cao), Image.Resampling.LANCZOS)

    ket_qua = []
    for dau in range(0, anh.height, _CHIEU_CAO_MOI_PHAN - _CHONG_LAP):
        cuoi = min(dau + _CHIEU_CAO_MOI_PHAN, anh.height)
        phan = anh.crop((0, dau, anh.width, cuoi))
        buffer = BytesIO()
        phan.save(buffer, format="JPEG", quality=92)
        ket_qua.append("data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"))
        if cuoi == anh.height:
            break
    return ket_qua
