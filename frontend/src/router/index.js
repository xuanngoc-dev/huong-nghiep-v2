import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { doiTuongList } from '@/data/doiTuong'
import { dinhHuongThptRoutes } from '@/components/guest/doi-tuong/HocSinhThpt/routes'

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
      component: () => import('@/layouts/GuestLayout.vue'),
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
        ...doiTuongList.map((item) => ({
          path: item.code,
          name: item.code,
          component: () => import('@/views/guest/DoiTuong.vue'),
          meta: { title: item.name, public: true, doiTuong: item.code },
        })),
        ...dinhHuongThptRoutes,
        {
          path: 'demo-chat',
          name: 'demo-chat',
          component: () => import('@/views/guest/DemoChat.vue'),
          meta: { title: 'Demo chat', public: true, hideAssist: true },
        },
        {
          path: 'validate-data',
          name: 'validate-data',
          component: () => import('@/views/guest/ValidateData.vue'),
          meta: { title: 'Kiểm tra dữ liệu', public: true, hideAssist: true },
        },
        {
          path: ':pathMatch(.*)*',
          name: 'not-found',
          component: () => import('@/views/guest/NotFound.vue'),
          meta: { title: 'Không tìm thấy trang', public: true },
        },
      ],
    },
    {
      path: '/member',
      component: () => import('@/layouts/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'member-home',
          component: () => import('@/views/member/PagePlaceholder.vue'),
          meta: { title: 'Thành viên', requiresAuth: true },
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
          component: () => import('@/views/member/HoSo.vue'),
          meta: { title: 'Cập nhật thông tin cá nhân', requiresAuth: true },
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
          path: 'danh-muc/bang-cap-chung-chi',
          name: 'bang-cap-chung-chi',
          component: () => import('@/views/admin/danh-muc/BangCapChungChi.vue'),
          meta: { title: 'Bằng cấp chứng chỉ', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/bai-thi-danh-gia-nang-luc',
          name: 'bai-thi-danh-gia-nang-luc',
          component: () => import('@/views/admin/danh-muc/BaiThiDanhGiaNangLuc.vue'),
          meta: { title: 'Bài thi đánh giá năng lực', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/thanh-tich-hoc-tap-nghien-cuu',
          name: 'thanh-tich-hoc-tap-nghien-cuu',
          component: () => import('@/views/admin/danh-muc/ThanhTichHocTapNghienCuu.vue'),
          meta: { title: 'Thành tích học tập, nghiên cứu', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'danh-muc/truong-hoc',
          name: 'truong-hoc',
          component: () => import('@/views/admin/danh-muc/TruongHoc.vue'),
          meta: { title: 'Trường học', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/danh-sach',
          name: 'de-an-tuyen-sinh-danh-sach',
          component: () => import('@/views/admin/de-an-tuyen-sinh/DanhSach.vue'),
          meta: { title: 'Danh sách đề án tuyển sinh', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/tru-so',
          name: 'de-an-tuyen-sinh-tru-so',
          component: () => import('@/views/admin/de-an-tuyen-sinh/TruSo.vue'),
          meta: { title: 'Trụ sở', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/website',
          name: 'de-an-tuyen-sinh-website',
          component: () => import('@/views/admin/de-an-tuyen-sinh/Website.vue'),
          meta: { title: 'Website', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/lien-he',
          name: 'de-an-tuyen-sinh-lien-he',
          component: () => import('@/views/admin/de-an-tuyen-sinh/LienHeTuyenSinh.vue'),
          meta: { title: 'Liên hệ tuyển sinh', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/chuong-trinh',
          name: 'de-an-tuyen-sinh-chuong-trinh',
          component: () => import('@/views/admin/de-an-tuyen-sinh/ChuongTrinhDaoTao.vue'),
          meta: { title: 'Chương trình đào tạo', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/ke-hoach',
          name: 'de-an-tuyen-sinh-ke-hoach',
          component: () => import('@/views/admin/de-an-tuyen-sinh/KeHoachTuyenSinh.vue'),
          meta: { title: 'Kế hoạch tuyển sinh', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/phuong-thuc',
          name: 'de-an-tuyen-sinh-phuong-thuc',
          component: () => import('@/views/admin/de-an-tuyen-sinh/PhuongThuc.vue'),
          meta: { title: 'Phương thức', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/phuong-thuc-to-hop',
          name: 'de-an-tuyen-sinh-phuong-thuc-to-hop',
          component: () => import('@/views/admin/de-an-tuyen-sinh/PhuongThucToHop.vue'),
          meta: { title: 'Tổ hợp phương thức', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/nhan-su',
          name: 'de-an-tuyen-sinh-nhan-su',
          component: () => import('@/views/admin/de-an-tuyen-sinh/NhanSu.vue'),
          meta: { title: 'Nhân sự', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/co-so-vat-chat',
          name: 'de-an-tuyen-sinh-co-so-vat-chat',
          component: () => import('@/views/admin/de-an-tuyen-sinh/CoSoVatChat.vue'),
          meta: { title: 'Cơ sở vật chất', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/quy-mo-dao-tao',
          name: 'de-an-tuyen-sinh-quy-mo-dao-tao',
          component: () => import('@/views/admin/de-an-tuyen-sinh/QuyMoDaoTao.vue'),
          meta: { title: 'Quy mô đào tạo', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/ty-le-viec-lam',
          name: 'de-an-tuyen-sinh-ty-le-viec-lam',
          component: () => import('@/views/admin/de-an-tuyen-sinh/TyLeViecLam.vue'),
          meta: { title: 'Tỷ lệ việc làm', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/trinh-do-nganh',
          name: 'de-an-tuyen-sinh-trinh-do-nganh',
          component: () => import('@/views/admin/de-an-tuyen-sinh/TrinhDoNganh.vue'),
          meta: { title: 'Trình độ ngành', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/doi-tuong-du-tuyen',
          name: 'de-an-tuyen-sinh-doi-tuong-du-tuyen',
          component: () => import('@/views/admin/de-an-tuyen-sinh/DoiTuongDuTuyen.vue'),
          meta: { title: 'Đối tượng dự tuyển', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/dieu-kien-du-tuyen',
          name: 'de-an-tuyen-sinh-dieu-kien-du-tuyen',
          component: () => import('@/views/admin/de-an-tuyen-sinh/DieuKienDuTuyen.vue'),
          meta: { title: 'Điều kiện dự tuyển', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/tieu-chi-xet-tuyen',
          name: 'de-an-tuyen-sinh-tieu-chi-xet-tuyen',
          component: () => import('@/views/admin/de-an-tuyen-sinh/TieuChiXetTuyen.vue'),
          meta: { title: 'Tiêu chí xét tuyển', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/diem-cong',
          name: 'de-an-tuyen-sinh-diem-cong',
          component: () => import('@/views/admin/de-an-tuyen-sinh/DiemCong.vue'),
          meta: { title: 'Điểm cộng', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/quy-tac-phan-bo',
          name: 'de-an-tuyen-sinh-quy-tac-phan-bo',
          component: () => import('@/views/admin/de-an-tuyen-sinh/QuyTacPhanBo.vue'),
          meta: { title: 'Quy tắc phân bổ', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/ho-so-du-tuyen',
          name: 'de-an-tuyen-sinh-ho-so-du-tuyen',
          component: () => import('@/views/admin/de-an-tuyen-sinh/HoSoDuTuyen.vue'),
          meta: { title: 'Hồ sơ dự tuyển', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/quy-doi-nguong',
          name: 'de-an-tuyen-sinh-quy-doi-nguong',
          component: () => import('@/views/admin/de-an-tuyen-sinh/QuyDoiNguongDauVao.vue'),
          meta: { title: 'Quy đổi ngưỡng đầu vào', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/quy-doi-diem',
          name: 'de-an-tuyen-sinh-quy-doi-diem',
          component: () => import('@/views/admin/de-an-tuyen-sinh/QuyDoiDiemTrungTuyen.vue'),
          meta: { title: 'Quy đổi điểm trúng tuyển', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/xet-tuyen-thang',
          name: 'de-an-tuyen-sinh-xet-tuyen-thang',
          component: () => import('@/views/admin/de-an-tuyen-sinh/ChinhSachXetTuyenThang.vue'),
          meta: { title: 'Xét tuyển thẳng', requiresAuth: true, requiresAdmin: true },
        },
        {
          path: 'de-an-tuyen-sinh/uu-tien-xet-tuyen',
          name: 'de-an-tuyen-sinh-uu-tien-xet-tuyen',
          component: () => import('@/views/admin/de-an-tuyen-sinh/ChinhSachUuTienXetTuyen.vue'),
          meta: { title: 'Ưu tiên xét tuyển', requiresAuth: true, requiresAdmin: true },
        },
      ],
    },
    {
      path: '/trac-nghiem/cau-hoi-dap-an',
      redirect: '/admin/trac-nghiem/cau-hoi-dap-an',
    },
    {
      path: '/huong-nghiep/:pathMatch(.*)*',
      redirect: (to) => `/member/huong-nghiep/${joinPathMatch(to.params.pathMatch)}`,
    },
    {
      path: '/trac-nghiem/lich-su',
      redirect: '/member/trac-nghiem/lich-su',
    },
    {
      path: '/tai-khoan/:pathMatch(.*)*',
      redirect: (to) => `/member/tai-khoan/${joinPathMatch(to.params.pathMatch)}`,
    },
    {
      path: '/danh-muc/:pathMatch(.*)*',
      redirect: (to) => `/admin/danh-muc/${joinPathMatch(to.params.pathMatch)}`,
    },
    {
      path: '/de-an-tuyen-sinh/:pathMatch(.*)*',
      redirect: (to) => `/admin/de-an-tuyen-sinh/${joinPathMatch(to.params.pathMatch)}`,
    },
  ],
})

function joinPathMatch(pathMatch) {
  if (Array.isArray(pathMatch)) return pathMatch.join('/')
  return pathMatch || ''
}

function homeLocation(auth) {
  return auth.isAdmin ? { name: 'admin-home' } : { name: 'member-home' }
}

router.beforeEach(async (to) => {
  const title = to.meta?.title
  document.title = title ? `${title} | Định hướng nghề` : 'Định hướng nghề'

  const auth = useAuthStore()

  if (auth.token && !auth.user) {
    await auth.loadMe()
  }

  if (to.matched.some((record) => record.meta.requiresAuth) && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.matched.some((record) => record.meta.requiresAdmin) && !auth.isAdmin) {
    return homeLocation(auth)
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return homeLocation(auth)
  }

  return true
})

export default router
