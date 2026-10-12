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
  return dinhHuongThptRoutes.find((item) => item.meta.dinhHuong === code)?.name
}
