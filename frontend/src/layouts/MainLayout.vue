<template>
  <el-container
    class="main-layout"
    :class="{
      'is-navbar-fixed': navbarFixed,
      'is-sidebar-fixed': sidebarFixed,
      'is-sidebar-overlay': isSidebarOverlay,
      'is-mobile': isMobile,
      'is-mobile-menu-open': isMobile && mobileMenuOpen,
    }"
  >
    <div
      :key="asideMountKey"
      class="aside-slot"
      :style="{ width: asideSlotWidth }"
    >
      <el-aside
        :width="asidePanelWidth"
        class="aside"
        :class="{
          'is-fixed': sidebarFixed || isSidebarOverlayExpanded,
          'is-collapsed': collapsed,
          'is-overlay-expanded': isSidebarOverlayExpanded,
          'is-hover-expanded': hoverExpanded,
          'is-mobile-drawer': isMobile,
          'is-mobile-open': isMobile && mobileMenuOpen,
        }"
        @mouseenter="onAsideEnter"
        @mouseleave="onAsideLeave"
      >
        <div class="brand">
          <el-button
            v-if="isMobile"
            text
            class="brand-toggle"
            aria-label="Ẩn menu"
            @click="closeMobileMenu"
          >
            <el-icon :size="20"><Fold /></el-icon>
          </el-button>
          <el-icon :size="22"><Monitor /></el-icon>
          <span class="brand-text" :class="{ 'is-hidden': collapsed && !isMobile }">
            {{ brandName }}
          </span>
        </div>

        <div class="aside-menu">
          <SideMenu :collapsed="collapsed" />
        </div>
      </el-aside>
    </div>

    <Transition name="aside-mask">
      <div
        v-if="showAsideMask"
        class="aside-mask"
        aria-hidden="true"
        @click="onAsideMaskClick"
      />
    </Transition>

    <el-container class="content-shell">
      <el-header class="header" :class="{ 'is-fixed': navbarFixed }">
        <div class="header-left">
          <el-icon
            v-if="isMobile"
            class="mobile-menu-btn"
            :size="24"
            role="button"
            tabindex="0"
            :aria-label="mobileMenuOpen ? 'Ẩn menu' : 'Hiện menu'"
            @click="toggleMobileMenu"
            @keydown.enter.space.prevent="toggleMobileMenu"
          >
            <Fold v-if="mobileMenuOpen" />
            <Expand v-else />
          </el-icon>
          <div v-if="isMobile" class="header-brand">
            <el-icon :size="20"><Monitor /></el-icon>
            <span class="header-brand__name">{{ brandName }}</span>
          </div>
          <el-button v-else text @click="togglePinnedCollapse">
            <el-icon :size="20">
              <Fold v-if="!pinnedCollapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
        </div>

        <div class="header-right">
          <div class="header-datetime" :title="nowFullLabel">
            <span class="header-datetime__weekday">{{ nowWeekday }}</span>
            <span class="header-datetime__time">{{ nowTime }}</span>
            <span class="header-datetime__date">{{ nowDate }}</span>
          </div>

          <el-tooltip content="Cài đặt" placement="bottom" :disabled="settingsOpen">
            <el-button text aria-label="Cài đặt" @click="settingsOpen = true">
              <el-icon :size="20"><Setting /></el-icon>
            </el-button>
          </el-tooltip>

          <el-switch
            v-model="isDark"
            inline-prompt
            active-text="🌙"
            inactive-text="☀️"
            @change="toggleDark"
          />

          <el-dropdown trigger="click" @command="onCommand">
            <span class="user-trigger">
              <el-avatar :size="32">{{ avatarLetter }}</el-avatar>
              <span class="user-name" :title="userFullName">
                <span class="user-name__full">{{ userFullName }}</span>
                <span class="user-name__short">{{ userShortName }}</span>
              </span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.user?.email }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  Đăng xuất
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <RouterView />
      </el-main>
    </el-container>

    <SettingsDrawer v-model="settingsOpen" />
  </el-container>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, Expand, Fold, Monitor, Setting } from '@element-plus/icons-vue'
import SettingsDrawer from '@/components/SettingsDrawer.vue'
import SideMenu from '@/components/SideMenu.vue'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'

const COLLAPSE_BREAKPOINT = 992
const WEEKDAYS = [
  'Chủ Nhật',
  'Thứ Hai',
  'Thứ Ba',
  'Thứ Tư',
  'Thứ Năm',
  'Thứ Sáu',
  'Thứ Bảy',
]

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()
const { navbarFixed, sidebarFixed, sidebarPushContent } = storeToRefs(layoutStore)

const brandName = 'Định hướng nghề'
const pinnedCollapsed = ref(false)
const hoverExpanded = ref(false)
const isMobile = ref(false)
const mobileMenuOpen = ref(false)
const isDark = ref(document.documentElement.classList.contains('dark'))
const settingsOpen = ref(false)
const now = ref(new Date())
const asideMountKey = ref(0)

const collapsed = computed(() => {
  if (isMobile.value) return false
  return pinnedCollapsed.value && !hoverExpanded.value
})

const isSidebarOverlay = computed(() => {
  if (isMobile.value) return true
  return !sidebarPushContent.value
})

const isSidebarOverlayExpanded = computed(() => {
  if (isMobile.value) return mobileMenuOpen.value
  if (hoverExpanded.value) return true
  return isSidebarOverlay.value && !pinnedCollapsed.value
})

const showAsideMask = computed(() => {
  if (isMobile.value) return mobileMenuOpen.value
  return isSidebarOverlay.value && !pinnedCollapsed.value
})

const asideSlotWidth = computed(() => {
  if (isMobile.value) return '0px'
  if (pinnedCollapsed.value) return '64px'
  if (isSidebarOverlay.value) return '64px'
  return '240px'
})

const asidePanelWidth = computed(() => {
  if (isMobile.value) return '240px'
  return collapsed.value ? '64px' : '240px'
})

const userFullName = computed(() => String(authStore.user?.ho_ten || '').trim() || 'Người dùng')
const userShortName = computed(() => {
  const parts = userFullName.value.split(/\s+/).filter(Boolean)
  return parts.length ? parts[parts.length - 1] : 'User'
})
const avatarLetter = computed(() => (userShortName.value || 'U').charAt(0).toUpperCase())

const nowWeekday = computed(() => WEEKDAYS[now.value.getDay()])
const nowTime = computed(() =>
  now.value.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }),
)
const nowDate = computed(() =>
  now.value.toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }),
)
const nowFullLabel = computed(() => `${nowWeekday.value}, ${nowTime.value} — ${nowDate.value}`)

let hoverLeaveTimer = null
let mediaQuery = null
let clockTimer = null

function clearHoverLeaveTimer() {
  if (hoverLeaveTimer != null) {
    window.clearTimeout(hoverLeaveTimer)
    hoverLeaveTimer = null
  }
}

function onAsideEnter() {
  if (isMobile.value || !pinnedCollapsed.value) return
  clearHoverLeaveTimer()
  hoverExpanded.value = true
}

function onAsideLeave() {
  if (isMobile.value || !pinnedCollapsed.value) return
  clearHoverLeaveTimer()
  hoverLeaveTimer = window.setTimeout(() => {
    hoverExpanded.value = false
    hoverLeaveTimer = null
  }, 180)
}

function togglePinnedCollapse() {
  clearHoverLeaveTimer()
  hoverExpanded.value = false
  pinnedCollapsed.value = !pinnedCollapsed.value
}

function pinCollapse() {
  clearHoverLeaveTimer()
  hoverExpanded.value = false
  pinnedCollapsed.value = true
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function onAsideMaskClick() {
  if (isMobile.value) {
    closeMobileMenu()
    return
  }
  pinCollapse()
}

function syncCollapseByViewport(e) {
  clearHoverLeaveTimer()
  hoverExpanded.value = false
  isMobile.value = e.matches
  mobileMenuOpen.value = false
  pinnedCollapsed.value = e.matches
}

function toggleDark(val) {
  document.documentElement.classList.toggle('dark', val)
  localStorage.setItem('darkMode', val ? '1' : '0')
}

async function onCommand(cmd) {
  if (cmd === 'logout') {
    authStore.logout()
    ElMessage.success('Đã đăng xuất')
    router.push({ name: 'login' })
  }
}

watch(sidebarPushContent, async () => {
  clearHoverLeaveTimer()
  hoverExpanded.value = false
  mobileMenuOpen.value = false
  asideMountKey.value += 1
  await nextTick()
})

watch(
  () => route.fullPath,
  () => {
    if (isMobile.value) closeMobileMenu()
  },
)

onMounted(() => {
  const saved = localStorage.getItem('darkMode')
  if (saved === '1') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }

  mediaQuery = window.matchMedia(`(max-width: ${COLLAPSE_BREAKPOINT - 1}px)`)
  isMobile.value = mediaQuery.matches
  mobileMenuOpen.value = false
  pinnedCollapsed.value = mediaQuery.matches
  mediaQuery.addEventListener('change', syncCollapseByViewport)

  clockTimer = window.setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  mediaQuery?.removeEventListener('change', syncCollapseByViewport)
  clearHoverLeaveTimer()
  if (clockTimer != null) window.clearInterval(clockTimer)
})
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  position: relative;
  --layout-line: color-mix(in srgb, var(--el-text-color-primary) 34%, var(--el-bg-color));
  --layout-text: var(--el-text-color-primary);
  --layout-text-muted: color-mix(in srgb, var(--el-text-color-primary) 78%, var(--el-bg-color));
  --el-border-color: var(--layout-line);
  --el-border-color-light: color-mix(in srgb, var(--el-text-color-primary) 26%, var(--el-bg-color));
  --el-border-color-lighter: color-mix(in srgb, var(--el-text-color-primary) 18%, var(--el-bg-color));
  --el-text-color-regular: var(--layout-text);
  --el-text-color-secondary: var(--layout-text-muted);
  --el-font-size-base: var(--app-font-size);
  --el-menu-text-color: var(--layout-text);
  --el-menu-item-font-size: var(--app-font-size);
  color: var(--layout-text);
  font-size: var(--app-font-size);
  text-rendering: geometricPrecision;

  &.is-navbar-fixed,
  &.is-sidebar-fixed {
    height: 100vh;
    overflow: hidden;
  }
}

.aside-slot {
  flex-shrink: 0;
  position: relative;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.aside-mask {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: var(--el-overlay-color-lighter);
}

.aside-mask-enter-active,
.aside-mask-leave-active {
  transition: opacity 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.aside-mask-enter-from,
.aside-mask-leave-to {
  opacity: 0;
}

.aside {
  border-right: 1px solid var(--layout-line);
  background: var(--el-bg-color);
  transition:
    width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.28s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;

  &.is-fixed {
    height: 100vh;
    position: sticky;
    top: 0;
    overflow: hidden;
  }

  &.is-overlay-expanded {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 100;
    overflow: hidden;
    box-shadow: var(--el-box-shadow-dark);
  }

  &.is-hover-expanded {
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
  }

  &.is-mobile-drawer {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 100;
    overflow: hidden;
    width: 240px !important;
    transform: translateX(-100%);
    pointer-events: none;
    box-shadow: none;
  }

  &.is-mobile-drawer.is-mobile-open {
    transform: translateX(0);
    pointer-events: auto;
    box-shadow: var(--el-box-shadow-dark);
  }
}

.aside-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: var(--layout-line) transparent;

  :deep(.menu-group__header),
  :deep(.menu-group__abbr) {
    font-size: calc(var(--app-font-size) * 0.8);
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--layout-text-muted);
  }

  :deep(.el-menu-item) {
    font-size: var(--app-font-size);
    font-weight: 500;
    color: var(--layout-text);
  }

  :deep(.el-menu-item.is-active) {
    font-weight: 600;
  }
}

.brand {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  font-weight: 700;
  font-size: calc(var(--app-font-size) + 1px);
  color: var(--el-color-primary);
  border-bottom: 1px solid var(--layout-line);
  overflow: hidden;
  white-space: nowrap;

  .aside.is-collapsed & {
    justify-content: center;
    padding: 0;
  }
}

.brand-toggle {
  flex-shrink: 0;
}

.brand-text {
  display: inline-block;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 1;
  transition: opacity 0.2s ease, max-width 0.28s ease;

  &.is-hidden {
    max-width: 0;
    opacity: 0;
  }
}

.content-shell {
  min-width: 0;
  min-height: 0;

  .is-navbar-fixed &,
  .is-sidebar-fixed & {
    height: 100vh;
  }

  .is-navbar-fixed & {
    overflow: hidden;
  }
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--layout-line);
  background: var(--el-bg-color);
  color: var(--layout-text);
  flex-shrink: 0;

  &.is-fixed {
    position: sticky;
    top: 0;
    z-index: 20;
  }
}

.header-datetime {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.header-datetime__weekday {
  font-size: 0.87em;
  font-weight: 700;
  color: var(--layout-text);
}

.header-datetime__time {
  font-size: 0.93em;
  font-weight: 700;
  color: var(--el-color-primary);
}

.header-datetime__date {
  font-size: 0.87em;
  font-weight: 600;
  color: var(--layout-text-muted);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.header-right {
  margin-left: auto;
  gap: 10px;
}

.mobile-menu-btn {
  cursor: pointer;
  color: var(--el-text-color-regular);
  outline: none;

  &:hover,
  &:focus-visible {
    color: var(--el-color-primary);
  }
}

.header-brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--el-color-primary);
  font-weight: 700;
  font-size: calc(var(--app-font-size) + 1px);
}

.header-brand__name {
  display: none;
}

.user-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  max-width: 220px;
}

.user-name {
  flex: 1;
  min-width: 0;
  max-width: 160px;
  font-size: 1em;
  font-weight: 600;
  color: var(--layout-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-name__full {
  display: inline;
}

.user-name__short {
  display: none;
}

.main {
  background: var(--el-bg-color-page);
  min-height: 0;

  .is-navbar-fixed & {
    overflow-y: auto;
  }
}

@media (max-width: 991px) {
  .aside-slot {
    width: 0 !important;
    overflow: visible;
  }

  .header {
    gap: 10px;
    overflow-x: auto;
  }
}

@media (max-width: 640px) {
  .header-datetime {
    display: none;
  }

  .user-name__full {
    display: none;
  }

  .user-name__short {
    display: inline;
  }
}
</style>
