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
            <RouterLink
              class="nav-link landing-nav__link"
              :class="{ active: isActive(item) }"
              :to="linkTo(item)"
            >
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>

        <div class="d-grid gap-2 d-lg-flex align-items-lg-center">
          <template v-if="auth.isAuthenticated">
            <RouterLink class="btn landing-nav__solid" to="/member">Khu vực thành viên</RouterLink>
            <RouterLink v-if="auth.isAdmin" class="btn landing-nav__outline" to="/admin">
              Quản trị
            </RouterLink>
          </template>
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
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { navLinks } from '@/data/landing'
import 'bootstrap/js/dist/collapse'

const auth = useAuthStore()
const route = useRoute()
const scrolled = ref(false)

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

function isActive(item) {
  if (item.hash) return route.name === 'home' && route.hash === item.hash
  if (item.to?.name === 'home') return route.name === 'home' && !route.hash
  return route.name === item.to?.name
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
  font-size: 0.92rem;
  border-radius: 8px;
  padding-inline: 0.9rem !important;
  transition:
    color 0.2s ease,
    background 0.2s ease;
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

@media (prefers-reduced-motion: reduce) {
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
