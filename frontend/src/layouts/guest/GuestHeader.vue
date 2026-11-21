<template>
  <nav
    class="navbar navbar-expand-lg landing-nav sticky-top"
    :class="{ 'is-scrolled': scrolled }"
    aria-label="Điều hướng chính"
  >
    <div class="container-fluid landing-nav__inner">
      <RouterLink class="landing-nav__brand" to="/">
        <span class="landing-nav__mark" aria-hidden="true">ĐH</span>
        <span>Định hướng nghề</span>
      </RouterLink>

      <button
        class="navbar-toggler landing-nav__toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#guestNav"
        aria-controls="guestNav"
        aria-expanded="false"
        aria-label="Mở menu"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="guestNav" class="collapse navbar-collapse">
        <ul class="navbar-nav landing-nav__links mx-lg-auto my-3 my-lg-0">
          <li v-for="item in navLinks" :key="item.label" class="nav-item">
            <!-- moChat: mở khung chat nổi (trợ lý AI) thay vì chuyển trang. -->
            <button
              v-if="item.moChat"
              type="button"
              class="nav-link landing-nav__link landing-nav__link--nut"
              :class="{ active: chat.khungMo }"
              @click="chat.moKhungChat()"
            >
              {{ item.label }}
            </button>
            <RouterLink
              v-else
              class="nav-link landing-nav__link"
              :class="{ active: isActive(item) }"
              :to="linkTo(item)"
            >
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>

        <div class="d-grid gap-2 d-lg-flex align-items-lg-center">
          <!-- Đã đăng nhập: tên tài khoản, rê chuột (desktop) hoặc chạm (mobile) để mở menu tài khoản. -->
          <div v-if="auth.isAuthenticated" class="tai-khoan-nhom">
            <SoDuTaiKhoan v-if="!auth.isAdmin" />
            <CustomDropdown
              :trigger="moBangCham ? 'click' : 'hover'"
              placement="bottom-end"
              popper-class="tai-khoan-menu"
              @command="onCommand"
            >
              <button type="button" class="tai-khoan" aria-label="Menu tài khoản">
                <span class="tai-khoan__avatar" aria-hidden="true">{{ chuCaiDau }}</span>
                <span class="tai-khoan__ten">{{ tenHienThi }}</span>
                <CustomIcon class="tai-khoan__mui-ten"><ArrowDown /></CustomIcon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <li class="tai-khoan-menu__dau" aria-hidden="true">
                    <strong>{{ tenHienThi }}</strong>
                    <span v-if="auth.user?.email">{{ auth.user.email }}</span>
                  </li>
                  <el-dropdown-item
                    v-for="item in menuTaiKhoan"
                    :key="item.command"
                    :command="item.command"
                    :divided="item.divided"
                    :icon="item.icon"
                    :class="{ 'tai-khoan-menu__dang-xuat': item.command === 'logout' }"
                  >
                    {{ item.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </CustomDropdown>
            <DoiMatKhauDialog v-model="doiMatKhauMo" />
          </div>
          <template v-else>
            <RouterLink class="btn landing-nav__outline" to="/login">Đăng nhập</RouterLink>
            <RouterLink class="btn landing-nav__solid" to="/register">Đăng ký</RouterLink>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowDown,
  Clock,
  Lock,
  Postcard,
  Setting,
  SwitchButton,
  Tickets,
  User,
  UserFilled,
  Wallet,
} from '@element-plus/icons-vue'
import DoiMatKhauDialog from '@/components/member/DoiMatKhauDialog.vue'
import SoDuTaiKhoan from '@/components/member/SoDuTaiKhoan.vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useIsMobile } from '@/composables/useResponsiveSize'
import { navLinks } from '@/data/landing'
import 'bootstrap/js/dist/collapse'

const auth = useAuthStore()
const chat = useChatStore()
const route = useRoute()
const router = useRouter()
const scrolled = ref(false)
const doiMatKhauMo = ref(false)
// Navbar thu gọn (< lg) hoặc thiết bị không có hover: mở menu tài khoản bằng chạm/bấm.
const moBangCham = useIsMobile('(max-width: 991.98px), (hover: none)')

const tenHienThi = computed(() => auth.displayName || 'Tài khoản')
const chuCaiDau = computed(() => {
  const tu = tenHienThi.value.trim().split(/\s+/).pop() || ''
  return (tu[0] || '?').toUpperCase()
})

// command là route đích; 'logout' là đăng xuất.
const menuTaiKhoan = computed(() => [
  { command: 'member-home', label: 'Khu vực thành viên', icon: UserFilled },
  ...(auth.isAdmin ? [{ command: 'admin-home', label: 'Trang quản trị', icon: Setting }] : []),
  { command: 'thong-tin-ca-nhan', label: 'Thông tin cá nhân', icon: User, divided: true },
  { command: 'doi-mat-khau', label: 'Đổi mật khẩu', icon: Lock },
  { command: 'ho-so', label: 'Hồ sơ năng lực', icon: Postcard },
  { command: 'nap-tien', label: 'Nạp tiền', icon: Wallet },
  { command: 'lich-su-nap-tien', label: 'Lịch sử nạp tiền', icon: Tickets },
  // Quản trị viên xem lịch sử trắc nghiệm của mọi người ở trang quản trị.
  {
    command: auth.isAdmin ? 'admin-lich-su-trac-nghiem' : 'lich-su-trac-nghiem',
    label: 'Lịch sử trắc nghiệm',
    icon: Clock,
  },
  { command: 'logout', label: 'Đăng xuất', icon: SwitchButton, divided: true },
])

function onCommand(command) {
  if (command === 'doi-mat-khau') {
    doiMatKhauMo.value = true
    return
  }
  if (command !== 'logout') {
    router.push({ name: command })
    return
  }
  auth.logout()
  ElMessage.success('Đã đăng xuất')
  if (route.matched.some((record) => record.meta.requiresAuth)) router.push({ name: 'home' })
}

function onScroll() {
  scrolled.value = window.scrollY > 8
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => window.removeEventListener('scroll', onScroll))

function linkTo(item) {
  if (item.hash) return { ...item.to, hash: item.hash }
  return item.to
}

// Trang con (vd. hướng đi THPT → du học) vẫn sáng mục cha nhờ meta.doiTuong / doiTuongCha / goc;
// trang riêng của một mục trên trang chủ (vd. /tra-cuu) khai báo meta.mucMenu = hash của mục đó.
function isActive(item) {
  if (item.hash) return (route.name === 'home' && route.hash === item.hash) || route.meta.mucMenu === item.hash
  if (item.to?.name === 'home') return route.name === 'home' && !route.hash
  const ten = item.to?.name
  return route.name === ten || [route.meta.doiTuong, route.meta.doiTuongCha, route.meta.goc].includes(ten)
}
</script>

<style scoped>
.landing-nav {
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid transparent;
  backdrop-filter: blur(16px) saturate(1.4);
  z-index: 1030;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    border-color 0.3s ease;
}

.landing-nav.is-scrolled {
  background: rgba(255, 255, 255, 0.94);
  border-bottom-color: rgba(15, 23, 42, 0.06);
  box-shadow: 0 10px 30px rgba(11, 33, 18, 0.08);
}

.landing-nav__inner {
  padding-block: 0.35rem;
}

.landing-nav__brand {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  color: #0f172a;
  font-family: 'Be Vietnam Pro', sans-serif;
  font-weight: 400;
  text-decoration: none;
}

.landing-nav__mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3f9643, #2f7a33);
  color: #fff;
  font-size: 0.78rem;
  letter-spacing: 0.02em;
}

.landing-nav__toggler {
  border: 1px solid rgba(63, 150, 67, 0.2);
}

.landing-nav__links {
  gap: 0.15rem;
}

.landing-nav__link {
  position: relative;
  color: #475569 !important;
  font-weight: 500;
  /* font-size: 0.92rem; */
  border-radius: 8px;
  padding-inline: 0.9rem !important;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

/* Mục "Trợ lý tư vấn" là nút (mở khung chat), trông như các link khác. */
.landing-nav__link--nut {
  border: 0;
  background: transparent;
  font: inherit;
  text-align: left;
}

/* 7 mục menu: thu gọn khoảng cách ở màn hình laptop nhỏ để không xuống dòng. */
@media (min-width: 992px) and (max-width: 1279.98px) {
  .landing-nav__link {
    padding-inline: 0.5rem !important;
    font-size: 0.9rem;
    white-space: nowrap;
  }
}

.landing-nav__link::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 2px;
  width: 18px;
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, #3f9643, #2f7a33);
  transform: translateX(-50%) scaleX(0);
  transition: transform 0.25s ease;
}

.landing-nav__link.active::after {
  transform: translateX(-50%) scaleX(1);
}

.landing-nav__link:hover,
.landing-nav__link.active {
  color: #2f7a33 !important;
  background: rgba(63, 150, 67, 0.08);
}

.landing-nav__outline {
  border: 1px solid rgba(63, 150, 67, 0.28);
  color: #2f7a33;
  background: #fff;
  font-weight: 400;
}

.landing-nav__outline:hover {
  border-color: #3f9643;
  color: #1f5a24;
  background: rgba(63, 150, 67, 0.06);
}

.landing-nav__outline,
.landing-nav__solid {
  min-height: 42px;
  border-radius: 8px;
  padding-inline: 1.1rem;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.landing-nav__solid {
  border: 0;
  color: #fff;
  background: linear-gradient(135deg, #3f9643, #2f7a33);
  font-weight: 400;
  box-shadow: 0 10px 22px rgba(63, 150, 67, 0.22);
}

.landing-nav__solid:hover {
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(63, 150, 67, 0.3);
}

/* Nút tài khoản (đã đăng nhập) */
.tai-khoan-nhom {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.tai-khoan {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 260px;
  min-height: 42px;
  padding: 0.25rem 0.75rem 0.25rem 0.3rem;
  border: 1px solid rgba(63, 150, 67, 0.28);
  border-radius: 999px;
  background: #fff;
  color: #0f172a;
  font-size: 0.92rem;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.tai-khoan:hover,
.tai-khoan:focus-visible {
  border-color: #3f9643;
  background: rgba(63, 150, 67, 0.06);
}

.tai-khoan__avatar {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3f9643, #2f7a33);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
}

.tai-khoan__ten {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tai-khoan__mui-ten {
  flex-shrink: 0;
  color: #475569;
}

@media (prefers-reduced-motion: reduce) {
  .tai-khoan,
  .landing-nav,
  .landing-nav__link,
  .landing-nav__link::after,
  .landing-nav__outline,
  .landing-nav__solid {
    transition: none;
  }
}

@media (max-width: 991.98px) {
  .landing-nav__links {
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  }
}
</style>

<!-- Menu tài khoản teleport ra body nên không dùng scoped. -->
<style>
.tai-khoan-menu .el-dropdown-menu {
  min-width: 220px;
}

.tai-khoan-menu__dau {
  display: flex;
  flex-direction: column;
  max-width: 260px;
  padding: 6px 16px 10px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 4px;
  list-style: none;
  font-size: 13px;
  line-height: 1.4;
}

.tai-khoan-menu__dau strong,
.tai-khoan-menu__dau span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tai-khoan-menu__dau span {
  color: var(--el-text-color-secondary);
}

.tai-khoan-menu .tai-khoan-menu__dang-xuat {
  color: var(--el-color-danger);
}
</style>
