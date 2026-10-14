from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    chat,
    dm_bai_thi_danh_gia_nang_luc,
    dm_chung_chi_ngoai_ngu,
    dm_chuyen_nganh,
    dm_dan_toc,
    dm_doi_tuong_uu_tien,
    dm_khu_vuc_uu_tien,
    dm_linh_vuc_dao_tao,
    dm_loai_cau_hoi,
    dm_mon_hoc,
    dm_nganh_dao_tao,
    dm_nhom_nganh_dao_tao,
    dm_nhom_tinh_cach_holland,
    dm_phuong_thuc_tuyen_sinh,
    dm_thanh_tich_hoc_tap_nghien_cuu,
    dm_tinh_thanh,
    dm_to_hop_mon_hoc,
    dm_ton_giao,
    health,
    ho_so,
    tai_lieu,
    tn_cau_hoi,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(ho_so.router)
api_router.include_router(dm_tinh_thanh.router)
api_router.include_router(dm_dan_toc.router)
api_router.include_router(dm_ton_giao.router)
api_router.include_router(dm_khu_vuc_uu_tien.router)
api_router.include_router(dm_doi_tuong_uu_tien.router)
api_router.include_router(dm_phuong_thuc_tuyen_sinh.router)
api_router.include_router(dm_mon_hoc.router)
api_router.include_router(dm_to_hop_mon_hoc.router)
api_router.include_router(dm_loai_cau_hoi.router)
api_router.include_router(dm_nhom_tinh_cach_holland.router)
api_router.include_router(dm_linh_vuc_dao_tao.router)
api_router.include_router(dm_nhom_nganh_dao_tao.router)
api_router.include_router(dm_nganh_dao_tao.router)
api_router.include_router(dm_chuyen_nganh.router)
api_router.include_router(dm_chung_chi_ngoai_ngu.router)
api_router.include_router(dm_bai_thi_danh_gia_nang_luc.router)
api_router.include_router(dm_thanh_tich_hoc_tap_nghien_cuu.router)
api_router.include_router(tn_cau_hoi.router)
api_router.include_router(tai_lieu.router)
api_router.include_router(chat.router)
