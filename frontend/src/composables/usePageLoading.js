import { ref } from 'vue'
import { useRouter } from 'vue-router'
import menuData from '@/data/menu.json'
import { dinhHuongThptRoutes } from '@/components/guest/doi-tuong/HocSinhThpt/routes'

const MIN_VISIBLE_MS = 420
const visible = ref(false)
let installed = false
let hideTimer = 0
let shownAt = 0

const loadingPaths = new Set()
for (const groups of Object.values(menuData)) {
  if (!Array.isArray(groups)) continue
  for (const group of groups) {
    for (const item of group.items || []) {
      if (item?.index) loadingPaths.add(item.index)
    }
  }
}
for (const route of dinhHuongThptRoutes) {
  if (!route.path) continue
  loadingPaths.add(route.path.startsWith('/') ? route.path : `/${route.path}`)
}

function show() {
  window.clearTimeout(hideTimer)
  if (!visible.value) shownAt = performance.now()
  visible.value = true
}

function scheduleHide() {
  const wait = Math.max(0, MIN_VISIBLE_MS - (performance.now() - shownAt))
  window.clearTimeout(hideTimer)
  hideTimer = window.setTimeout(() => {
    visible.value = false
  }, wait)
}

function isInitialNavigation(from) {
  return from.matched.length === 0
}

export function usePageLoading() {
  const router = useRouter()

  if (!installed) {
    installed = true
    router.beforeEach((to, from) => {
      if (isInitialNavigation(from)) return
      if (to.path === from.path) return
      if (!loadingPaths.has(to.path)) return
      show()
    })
    router.afterEach(() => {
      if (visible.value) scheduleHide()
    })
    router.onError(() => {
      if (visible.value) scheduleHide()
    })
  }

  return { visible }
}
