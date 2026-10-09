from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    dm_dan_toc,
    dm_doi_tuong_uu_tien,
    dm_khu_vuc_uu_tien,
    dm_phuong_thuc_tuyen_sinh,
    dm_tinh_thanh,
    dm_ton_giao,
    health,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(dm_tinh_thanh.router)
api_router.include_router(dm_dan_toc.router)
api_router.include_router(dm_ton_giao.router)
api_router.include_router(dm_khu_vuc_uu_tien.router)
api_router.include_router(dm_doi_tuong_uu_tien.router)
api_router.include_router(dm_phuong_thuc_tuyen_sinh.router)
