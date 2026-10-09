import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'dh-layout-settings'

const defaults = {
  menuGroupCollapsible: false,
  menuUniqueOpened: true,
  menuGroupHeaderVisible: true,
  navbarFixed: true,
  sidebarFixed: true,
  sidebarPushContent: true,
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaults }
    return { ...defaults, ...JSON.parse(raw) }
  } catch {
    return { ...defaults }
  }
}

export const useLayoutStore = defineStore('layout', () => {
  const saved = loadSettings()

  const menuGroupCollapsible = ref(saved.menuGroupCollapsible)
  const menuUniqueOpened = ref(saved.menuUniqueOpened)
  const menuGroupHeaderVisible = ref(saved.menuGroupHeaderVisible)
  const navbarFixed = ref(saved.navbarFixed)
  const sidebarFixed = ref(saved.sidebarFixed)
  const sidebarPushContent = ref(saved.sidebarPushContent)

  function persist() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        menuGroupCollapsible: menuGroupCollapsible.value,
        menuUniqueOpened: menuUniqueOpened.value,
        menuGroupHeaderVisible: menuGroupHeaderVisible.value,
        navbarFixed: navbarFixed.value,
        sidebarFixed: sidebarFixed.value,
        sidebarPushContent: sidebarPushContent.value,
      }),
    )
  }

  watch(
    [
      menuGroupCollapsible,
      menuUniqueOpened,
      menuGroupHeaderVisible,
      navbarFixed,
      sidebarFixed,
      sidebarPushContent,
    ],
    persist,
  )

  function reset() {
    menuGroupCollapsible.value = defaults.menuGroupCollapsible
    menuUniqueOpened.value = defaults.menuUniqueOpened
    menuGroupHeaderVisible.value = defaults.menuGroupHeaderVisible
    navbarFixed.value = defaults.navbarFixed
    sidebarFixed.value = defaults.sidebarFixed
    sidebarPushContent.value = defaults.sidebarPushContent
  }

  return {
    menuGroupCollapsible,
    menuUniqueOpened,
    menuGroupHeaderVisible,
    navbarFixed,
    sidebarFixed,
    sidebarPushContent,
    reset,
  }
})
