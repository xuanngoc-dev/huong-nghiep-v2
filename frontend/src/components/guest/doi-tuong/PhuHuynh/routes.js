import { taoRoutesDinhHuongThpt } from '@/components/guest/doi-tuong/HocSinhThpt/routes'

export const TIEN_TO_LOP_12 = 'ph-lop-12'

// `meta.capHoc`: route con của màn cấp học nào (dùng cho breadcrumb và nút quay lại).
export const giaiDoanConRoutes = [
  {
    path: 'phu-huynh/thcs',
    name: 'phu-huynh-thcs',
    component: () => import('./Thcs.vue'),
    meta: { title: 'Con học Trung học cơ sở', public: true, giaiDoanCon: 'thcs' },
  },
  {
    path: 'phu-huynh/thpt',
    name: 'phu-huynh-thpt',
    component: () => import('./Thpt.vue'),
    meta: { title: 'Con học Trung học phổ thông', public: true, giaiDoanCon: 'thpt' },
  },
  {
    path: 'phu-huynh/thpt/lop-10-11',
    name: 'phu-huynh-thpt-lop-10-11',
    component: () => import('./ThptLop1011.vue'),
    meta: { title: 'Con học lớp 10 và lớp 11', public: true, giaiDoanCon: 'thpt-10-11', capHoc: 'thpt' },
  },
  {
    path: 'phu-huynh/thpt/lop-12',
    name: 'phu-huynh-thpt-lop-12',
    component: () => import('./ThptLop12.vue'),
    meta: { title: 'Con học lớp 12', public: true, giaiDoanCon: 'thpt-12', capHoc: 'thpt' },
  },
  {
    path: 'phu-huynh/da-tot-nghiep',
    name: 'phu-huynh-da-tot-nghiep',
    component: () => import('./DaTotNghiep.vue'),
    meta: { title: 'Con đã tốt nghiệp THPT', public: true, giaiDoanCon: 'da-tot-nghiep' },
  },
  // Con lớp 12: dùng lại toàn bộ luồng chọn định hướng, trắc nghiệm của học sinh THPT.
  ...taoRoutesDinhHuongThpt({
    duongDan: 'phu-huynh/thpt/lop-12',
    tienTo: TIEN_TO_LOP_12,
    goc: 'phu-huynh-thpt-lop-12',
  }),
]

export function routeNameGiaiDoanCon(code) {
  return giaiDoanConRoutes.find((item) => item.meta?.giaiDoanCon === code)?.name
}
