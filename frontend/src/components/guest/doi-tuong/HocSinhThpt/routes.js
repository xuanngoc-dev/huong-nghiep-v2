// Cây route định hướng THPT; `path`/`name` là phần đuôi, ghép với tiền tố của từng nhánh trong taoRoutesDinhHuongThpt.
const cayDinhHuongThpt = [
  {
    path: 'di-lam',
    name: 'di-lam',
    component: () => import('./DiLam.vue'),
    meta: { title: 'Đi làm ngay sau khi tốt nghiệp', public: true, dinhHuong: 'di-lam' },
  },
  {
    path: 'di-lam/nhom-nghe/:maNhom',
    name: 'di-lam-nhom-nghe',
    component: () => import('./di-lam/ChiTietNhomNghe.vue'),
    meta: { title: 'Nghề cụ thể', public: true, dinhHuong: 'di-lam' },
  },
  {
    path: 'du-hoc-nghe',
    name: 'du-hoc-nghe',
    component: () => import('./DuHocNghe.vue'),
    meta: { title: 'Du học nghề', public: true, dinhHuong: 'du-hoc-nghe' },
  },
  {
    path: 'du-hoc',
    name: 'du-hoc',
    component: () => import('./DuHoc.vue'),
    meta: { title: 'Du học', public: true, dinhHuong: 'du-hoc' },
  },
  {
    path: 'thi-dai-hoc',
    name: 'thi-dai-hoc',
    component: () => import('./ThiDaiHoc.vue'),
    meta: { title: 'Thi Đại học & cao đẳng', public: true, dinhHuong: 'thi-dai-hoc' },
  },
  {
    path: 'thi-dai-hoc/lam-trac-nghiem/:ssid/nganh-phu-hop',
    name: 'thi-dai-hoc-nganh-phu-hop',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/NganhPhuHop.vue'),
    meta: {
      title: 'Ngành phù hợp',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/lam-trac-nghiem/:ssid/nganh/:maNganh',
    name: 'thi-dai-hoc-chi-tiet-nganh',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/ChiTietNganh.vue'),
    meta: {
      title: 'Chi tiết ngành',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/lam-trac-nghiem/:ssid/truong/:maTruong',
    name: 'thi-dai-hoc-chi-tiet-truong',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/ChiTietTruong.vue'),
    meta: {
      title: 'Chi tiết trường',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/lam-trac-nghiem/:ssid/ket-qua',
    name: 'thi-dai-hoc-ket-qua',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/KetQua.vue'),
    meta: {
      title: 'Kết quả trắc nghiệm Holland',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/lam-trac-nghiem/:ssid/:loaiCauHoiId(\\d+)',
    name: 'thi-dai-hoc-lam-trac-nghiem',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/LamBai.vue'),
    meta: {
      title: 'Làm trắc nghiệm Holland',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/chua-co',
    name: 'thi-dai-hoc-chua-co',
    component: () => import('./thi-dai-hoc/ChuaCo.vue'),
    meta: {
      title: 'Chưa có ngành nghề phù hợp',
      public: true,
      dinhHuong: 'thi-dai-hoc',
      giaiDoan: 'chua-co',
    },
  },
  {
    path: 'thi-dai-hoc/huong-dan-khao-sat',
    name: 'thi-dai-hoc-huong-dan-khao-sat',
    component: () => import('./thi-dai-hoc/HuongDanKhaoSat.vue'),
    meta: {
      title: 'Hướng dẫn khảo sát',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/da-co',
    name: 'thi-dai-hoc-da-co',
    component: () => import('./thi-dai-hoc/DaCo.vue'),
    meta: {
      title: 'Đã có ngành nghề mong muốn',
      public: true,
      dinhHuong: 'thi-dai-hoc',
      giaiDoan: 'da-co',
    },
  },
  {
    path: 'thi-dai-hoc/da-co/chon-truong/:maNganh',
    name: 'thi-dai-hoc-chon-truong',
    component: () => import('./thi-dai-hoc/ChonTruong.vue'),
    meta: {
      title: 'Chọn trường',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/da-co/truong-phu-hop/:maNganh',
    name: 'thi-dai-hoc-truong-phu-hop',
    component: () => import('./thi-dai-hoc/TruongPhuHop.vue'),
    meta: {
      title: 'Trường phù hợp',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'thi-dai-hoc/phan-van',
    name: 'thi-dai-hoc-phan-van',
    component: () => import('./thi-dai-hoc/PhanVan.vue'),
    meta: {
      title: 'Đang phân vân giữa vài ngành nghề',
      public: true,
      dinhHuong: 'thi-dai-hoc',
      giaiDoan: 'phan-van',
    },
  },
  {
    path: 'khoi-nghiep',
    name: 'khoi-nghiep',
    component: () => import('./KhoiNghiep.vue'),
    meta: { title: 'Khởi nghiệp', public: true, dinhHuong: 'khoi-nghiep' },
  },
  {
    path: 'xuat-khau-lao-dong',
    name: 'xuat-khau-lao-dong',
    component: () => import('./XuatKhauLaoDong.vue'),
    meta: { title: 'Xuất khẩu lao động', public: true, dinhHuong: 'xuat-khau-lao-dong' },
  },
]

// Nhánh học sinh: /hoc-sinh-thpt/..., tên route `thpt-...`.
// Nhánh khác (vd. phụ huynh có con lớp 12) gắn lại đúng cây này dưới đường dẫn và tiền tố tên riêng;
// component lấy tên route của nhánh đang đứng qua useTenRouteThpt (meta.tienTo).
export function taoRoutesDinhHuongThpt({ duongDan, tienTo, goc }) {
  return cayDinhHuongThpt.map((item) => ({
    ...item,
    path: `${duongDan}/${item.path}`,
    name: `${tienTo}-${item.name}`,
    meta: { ...item.meta, tienTo, goc },
  }))
}

export const TIEN_TO_HOC_SINH = 'thpt'

export const dinhHuongThptRoutes = taoRoutesDinhHuongThpt({
  duongDan: 'hoc-sinh-thpt',
  tienTo: TIEN_TO_HOC_SINH,
  goc: 'hoc-sinh-thpt',
})

export function routeNameDinhHuongThpt(code, tienTo = TIEN_TO_HOC_SINH) {
  const item = cayDinhHuongThpt.find((route) => route.meta?.dinhHuong === code && !route.meta?.giaiDoan)
  return item && `${tienTo}-${item.name}`
}

export function routeNameGiaiDoanThiDaiHoc(code, tienTo = TIEN_TO_HOC_SINH) {
  const item = cayDinhHuongThpt.find((route) => route.meta?.giaiDoan === code)
  return item && `${tienTo}-${item.name}`
}

// Đổi tên route gốc của nhánh học sinh (`thpt-...`) sang tên tương ứng ở nhánh có tiền tố `tienTo`.
export function doiTenRouteThpt(ten, tienTo = TIEN_TO_HOC_SINH) {
  return ten.replace(/^thpt-/, `${tienTo}-`)
}
