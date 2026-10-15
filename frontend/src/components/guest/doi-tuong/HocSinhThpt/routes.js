export const dinhHuongThptRoutes = [
  {
    path: 'hoc-sinh-thpt/di-lam',
    name: 'thpt-di-lam',
    component: () => import('./DiLam.vue'),
    meta: { title: 'Đi làm ngay sau khi tốt nghiệp', public: true, dinhHuong: 'di-lam' },
  },
  {
    path: 'hoc-sinh-thpt/du-hoc-nghe',
    name: 'thpt-du-hoc-nghe',
    component: () => import('./DuHocNghe.vue'),
    meta: { title: 'Du học nghề', public: true, dinhHuong: 'du-hoc-nghe' },
  },
  {
    path: 'hoc-sinh-thpt/du-hoc',
    name: 'thpt-du-hoc',
    component: () => import('./DuHoc.vue'),
    meta: { title: 'Du học', public: true, dinhHuong: 'du-hoc' },
  },
  {
    path: 'hoc-sinh-thpt/thi-dai-hoc',
    name: 'thpt-thi-dai-hoc',
    component: () => import('./ThiDaiHoc.vue'),
    meta: { title: 'Thi Đại học & cao đẳng', public: true, dinhHuong: 'thi-dai-hoc' },
  },
  {
    path: 'hoc-sinh-thpt/thi-dai-hoc/lam-trac-nghiem/:ssid/nganh-phu-hop',
    name: 'thpt-thi-dai-hoc-nganh-phu-hop',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/NganhPhuHop.vue'),
    meta: {
      title: 'Ngành phù hợp',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'hoc-sinh-thpt/thi-dai-hoc/lam-trac-nghiem/:ssid/ket-qua',
    name: 'thpt-thi-dai-hoc-ket-qua',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/KetQua.vue'),
    meta: {
      title: 'Kết quả trắc nghiệm Holland',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'hoc-sinh-thpt/thi-dai-hoc/lam-trac-nghiem/:ssid/:loaiCauHoiId(\\d+)',
    name: 'thpt-thi-dai-hoc-lam-trac-nghiem',
    component: () => import('./thi-dai-hoc/lam-trac-nghiem/LamBai.vue'),
    meta: {
      title: 'Làm trắc nghiệm Holland',
      public: true,
      dinhHuong: 'thi-dai-hoc',
    },
  },
  {
    path: 'hoc-sinh-thpt/thi-dai-hoc/chua-co',
    name: 'thpt-thi-dai-hoc-chua-co',
    component: () => import('./thi-dai-hoc/ChuaCo.vue'),
    meta: {
      title: 'Chưa có ngành nghề phù hợp',
      public: true,
      dinhHuong: 'thi-dai-hoc',
      giaiDoan: 'chua-co',
    },
  },
  {
    path: 'hoc-sinh-thpt/khoi-nghiep',
    name: 'thpt-khoi-nghiep',
    component: () => import('./KhoiNghiep.vue'),
    meta: { title: 'Khởi nghiệp', public: true, dinhHuong: 'khoi-nghiep' },
  },
  {
    path: 'hoc-sinh-thpt/xuat-khau-lao-dong',
    name: 'thpt-xuat-khau-lao-dong',
    component: () => import('./XuatKhauLaoDong.vue'),
    meta: { title: 'Xuất khẩu lao động', public: true, dinhHuong: 'xuat-khau-lao-dong' },
  },
]

export function routeNameDinhHuongThpt(code) {
  return dinhHuongThptRoutes.find((item) => item.meta.dinhHuong === code && !item.meta.giaiDoan)?.name
}

export function routeNameGiaiDoanThiDaiHoc(code) {
  return dinhHuongThptRoutes.find((item) => item.meta.giaiDoan === code)?.name
}
