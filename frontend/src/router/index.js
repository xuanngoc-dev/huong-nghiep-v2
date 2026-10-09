import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { title: 'Đăng nhập', guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue'),
      meta: { title: 'Đăng ký', guest: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: { title: 'Trang chủ', requiresAuth: true },
        },
        {
          path: 'huong-nghiep/danh-gia',
          name: 'danh-gia',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Đánh giá năng lực', requiresAuth: true },
        },
        {
          path: 'huong-nghiep/goi-y',
          name: 'goi-y',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Gợi ý nghề nghiệp', requiresAuth: true },
        },
        {
          path: 'tai-khoan/ho-so',
          name: 'ho-so',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Hồ sơ của tôi', requiresAuth: true },
        },
        {
          path: 'danh-muc/tinh-thanh',
          name: 'tinh-thanh',
          component: () => import('@/views/danh-muc/TinhThanh.vue'),
          meta: { title: 'Tỉnh thành', requiresAuth: true },
        },
        {
          path: 'danh-muc/dan-toc',
          name: 'dan-toc',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Dân tộc', requiresAuth: true },
        },
        {
          path: 'danh-muc/ton-giao',
          name: 'ton-giao',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Tôn giáo', requiresAuth: true },
        },
        {
          path: 'danh-muc/khu-vuc-uu-tien',
          name: 'khu-vuc-uu-tien',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Khu vực ưu tiên', requiresAuth: true },
        },
        {
          path: 'danh-muc/doi-tuong-uu-tien',
          name: 'doi-tuong-uu-tien',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Đối tượng ưu tiên', requiresAuth: true },
        },
        {
          path: 'danh-muc/phuong-thuc-tuyen-sinh',
          name: 'phuong-thuc-tuyen-sinh',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Phương thức tuyển sinh', requiresAuth: true },
        },
        {
          path: 'danh-muc/truong-hoc',
          name: 'truong-hoc',
          component: () => import('@/views/PagePlaceholder.vue'),
          meta: { title: 'Trường học', requiresAuth: true },
        },
      ],
    },
  ],
})

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

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
