// Trang con của đối tượng học sinh THCS. `meta.doiTuongCha`: đối tượng cha, dùng cho guard (đối tượng chưa mở) và breadcrumb.
// Tên route có tiền tố `hs-thcs-` để không trùng route quản trị `thcs-...`.
export const DOI_TUONG_THCS = 'hoc-sinh-thcs'

export const dinhHuongThcsRoutes = [
  {
    path: 'hoc-sinh-thcs/tu-danh-gia',
    name: 'hs-thcs-tu-danh-gia',
    component: () => import('./TuDanhGia.vue'),
    meta: { title: 'Tìm hướng đi phù hợp', public: true, doiTuongCha: DOI_TUONG_THCS },
  },
  {
    path: 'hoc-sinh-thcs/huong-di/:maHuong',
    name: 'hs-thcs-huong-di',
    component: () => import('./ChiTietHuongDi.vue'),
    meta: { title: 'Hướng đi sau THCS', public: true, doiTuongCha: DOI_TUONG_THCS },
  },
]
