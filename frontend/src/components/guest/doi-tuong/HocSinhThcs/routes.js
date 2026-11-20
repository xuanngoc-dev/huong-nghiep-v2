// Trang con hướng đi sau THCS; `path`/`name` là phần đuôi, ghép với tiền tố của từng nhánh trong taoRoutesThcs.
// Tên route nhánh học sinh có tiền tố `hs-thcs-` để không trùng route quản trị `thcs-...`.
export const DOI_TUONG_THCS = 'hoc-sinh-thcs'
export const TIEN_TO_HOC_SINH_THCS = 'hs-thcs'

const cayThcs = [
  {
    path: 'tu-danh-gia',
    name: 'tu-danh-gia',
    component: () => import('./TuDanhGia.vue'),
    meta: { title: 'Tìm hướng đi phù hợp', public: true, huongDiThcs: true },
  },
  {
    path: 'huong-di/:maHuong',
    name: 'huong-di',
    component: () => import('./ChiTietHuongDi.vue'),
    meta: { title: 'Hướng đi sau THCS', public: true, huongDiThcs: true },
  },
]

// Nhánh khác (vd. phụ huynh có con học THCS) gắn lại đúng cây này dưới đường dẫn và tiền tố tên riêng;
// component lấy tên route của nhánh đang đứng qua useTenRouteThcs (meta.tienTo, meta.goc).
export function taoRoutesThcs({ duongDan, tienTo, goc, meta = {} }) {
  return cayThcs.map((item) => ({
    ...item,
    path: `${duongDan}/${item.path}`,
    name: `${tienTo}-${item.name}`,
    meta: { ...item.meta, ...meta, tienTo, goc },
  }))
}

// `meta.doiTuongCha`: đối tượng cha, dùng cho guard (đối tượng chưa mở).
export const dinhHuongThcsRoutes = taoRoutesThcs({
  duongDan: DOI_TUONG_THCS,
  tienTo: TIEN_TO_HOC_SINH_THCS,
  goc: DOI_TUONG_THCS,
  meta: { doiTuongCha: DOI_TUONG_THCS },
})

// Đổi tên route nhánh học sinh (`hs-thcs-...`) sang tên tương ứng ở nhánh có tiền tố `tienTo`.
export function doiTenRouteThcs(ten, tienTo = TIEN_TO_HOC_SINH_THCS) {
  return ten.replace(/^hs-thcs-/, `${tienTo}-`)
}
