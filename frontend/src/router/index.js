import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/guest/Login.vue'),
      meta: { title: 'Đăng nhập', guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/guest/Register.vue'),
      meta: { title: 'Đăng ký', guest: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/RootLayout.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/guest/Home.vue'),
          meta: { title: 'Trang chủ', public: true },
        },
        {
          path: 'chon-doi-tuong',
          name: 'chon-doi-tuong',
          component: () => import('@/views/guest/ChonDoiTuong.vue'),
          meta: { title: 'Chọn đối tượng', public: true },
        },
        {
          path: 'huong-nghiep/danh-gia',
          name: 'danh-gia',
          component: () => import('@/views/member/PagePlaceholder.vue'),
          meta: { title: 'Đánh giá năng lực', requiresAuth: true },
        },
        {
          path: 'huong-nghiep/goi-y',
          name: 'goi-y',
          component: () => import('@/views/member/PagePlaceholder.vue'),
          meta: { title: 'Gợi ý nghề nghiệp', requiresAuth: true },
        },
        {
          path: 'trac-nghiem/lich-su',
          name: 'lich-su-trac-nghiem',
          component: () => import('@/views/member/PagePlaceholder.vue'),
          meta: { title: 'Lịch sử trắc nghiệm', requiresAuth: true },
        },
        {
          path: 'tai-khoan/ho-so',
          name: 'ho-so',
          component: () => import('@/views/member/PagePlaceholder.vue'),
          meta: { title: 'Hồ sơ của tôi', requiresAuth: true },
        },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'admin-home',
          component: () => import('@/views/admin/Home.vue'),
          meta: { title: 'Trang chủ', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'trac-nghiem/cau-hoi-dap-an',
          name: 'cau-hoi-dap-an',
          component: () => import('@/views/admin/trac-nghiem/CauHoiDapAn.vue'),
          meta: { title: 'Câu hỏi - Đáp án', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'trac-nghiem/lich-su',
          name: 'admin-lich-su-trac-nghiem',
          component: () => import('@/views/admin/PagePlaceholder.vue'),
          meta: { title: 'Lịch sử trắc nghiệm', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'tai-khoan/ho-so',
          name: 'admin-ho-so',
          component: () => import('@/views/admin/PagePlaceholder.vue'),
          meta: { title: 'Hồ sơ của tôi', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/tinh-thanh',
          name: 'tinh-thanh',
          component: () => import('@/views/admin/danh-muc/TinhThanh.vue'),
          meta: { title: 'Tỉnh thành', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/dan-toc',
          name: 'dan-toc',
          component: () => import('@/views/admin/danh-muc/DanToc.vue'),
          meta: { title: 'Dân tộc', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/ton-giao',
          name: 'ton-giao',
          component: () => import('@/views/admin/danh-muc/TonGiao.vue'),
          meta: { title: 'Tôn giáo', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/khu-vuc-uu-tien',
          name: 'khu-vuc-uu-tien',
          component: () => import('@/views/admin/danh-muc/KhuVucUuTien.vue'),
          meta: { title: 'Khu vực ưu tiên', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/doi-tuong-uu-tien',
          name: 'doi-tuong-uu-tien',
          component: () => import('@/views/admin/danh-muc/DoiTuongUuTien.vue'),
          meta: { title: 'Đối tượng ưu tiên', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/phuong-thuc-tuyen-sinh',
          name: 'phuong-thuc-tuyen-sinh',
          component: () => import('@/views/admin/danh-muc/PhuongThucTuyenSinh.vue'),
          meta: { title: 'PT tuyển sinh', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/mon-hoc',
          name: 'mon-hoc',
          component: () => import('@/views/admin/danh-muc/MonHoc.vue'),
          meta: { title: 'Môn học', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/to-hop-mon-hoc',
          name: 'to-hop-mon-hoc',
          component: () => import('@/views/admin/danh-muc/ToHopMonHoc.vue'),
          meta: { title: 'Tổ hợp môn học', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/loai-cau-hoi',
          name: 'loai-cau-hoi',
          component: () => import('@/views/admin/danh-muc/LoaiCauHoi.vue'),
          meta: { title: 'Loại câu hỏi', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/nhom-tinh-cach-holland',
          name: 'nhom-tinh-cach-holland',
          component: () => import('@/views/admin/danh-muc/NhomTinhCachHolland.vue'),
          meta: { title: 'Nhóm Holland', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/linh-vuc-dao-tao',
          name: 'linh-vuc-dao-tao',
          component: () => import('@/views/admin/danh-muc/LinhVucDaoTao.vue'),
          meta: { title: 'Lĩnh vực đào tạo', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/nhom-nganh-dao-tao',
          name: 'nhom-nganh-dao-tao',
          component: () => import('@/views/admin/danh-muc/NhomNganhDaoTao.vue'),
          meta: { title: 'Nhóm ngành', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/nganh-dao-tao',
          name: 'nganh-dao-tao',
          component: () => import('@/views/admin/danh-muc/NganhDaoTao.vue'),
          meta: { title: 'Ngành đào tạo', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/chuyen-nganh',
          name: 'chuyen-nganh',
          component: () => import('@/views/admin/danh-muc/ChuyenNganh.vue'),
          meta: { title: 'Chuyên ngành', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/truong-hoc',
          name: 'truong-hoc',
          component: () => import('@/views/admin/PagePlaceholder.vue'),
          meta: { title: 'Trường học', requiresAuth: true, requiresAdmin: true },
        },
      ],
    },
    {
      path: '/trac-nghiem/cau-hoi-dap-an',
      redirect: '/admin/trac-nghiem/cau-hoi-dap-an',
    },
    {
      path: '/danh-muc/:pathMatch(.*)*',
      redirect: (to) => {
        const rest = Array.isArray(to.params.pathMatch)
          ? to.params.pathMatch.join('/')
          : to.params.pathMatch || ''
        return `/admin/danh-muc/${rest}`
      },
    },
  ],
})

function homeLocation(auth) {
  return auth.isAdmin ? { name: 'admin-home' } : { name: 'home' }
}

router.beforeEach(async (to) => {
  const title = to.meta?.title
  document.title = title ? `${title} | Định hướng nghề` : 'Định hướng nghề'

  const auth = useAuthStore()

  if (auth.token && !auth.user) {
    await auth.loadMe()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.matched.some((record) => record.meta.requiresAdmin) && !auth.isAdmin) {
    return { name: 'home' }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return homeLocation(auth)
  }

  return true
})

export default router
