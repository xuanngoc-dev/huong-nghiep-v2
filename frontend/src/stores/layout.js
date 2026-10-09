import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import {
  APPEARANCE_DEFAULTS,
  applyAppearance,
  normalizeFontFamily,
  normalizeFontSize,
  normalizeHex,
} from '@/utils/theme'

const STORAGE_KEY = 'dh-layout-settings'

const defaults = {
  menuGroupCollapsible: false,
  menuUniqueOpened: true,
  menuGroupHeaderVisible: true,
  navbarFixed: true,
  sidebarFixed: true,
  sidebarPushContent: true,
  ...APPEARANCE_DEFAULTS,
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : {}
    return {
      ...defaults,
      ...parsed,
      primaryColor: normalizeHex(parsed.primaryColor) || defaults.primaryColor,
      fontFamily: normalizeFontFamily(parsed.fontFamily),
      fontSize: normalizeFontSize(parsed.fontSize),
    }
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
  const primaryColor = ref(saved.primaryColor)
  const fontFamily = ref(saved.fontFamily)
  const fontSize = ref(saved.fontSize)

  function snapshot() {
    return {
      menuGroupCollapsible: menuGroupCollapsible.value,
      menuUniqueOpened: menuUniqueOpened.value,
      menuGroupHeaderVisible: menuGroupHeaderVisible.value,
      navbarFixed: navbarFixed.value,
      sidebarFixed: sidebarFixed.value,
      sidebarPushContent: sidebarPushContent.value,
      primaryColor: normalizeHex(primaryColor.value) || defaults.primaryColor,
      fontFamily: normalizeFontFamily(fontFamily.value),
      fontSize: normalizeFontSize(fontSize.value),
    }
  }

  function persist() {
    if (!normalizeHex(primaryColor.value)) {
      primaryColor.value = defaults.primaryColor
      return
    }
    const data = snapshot()
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    applyAppearance(data)
  }

  applyAppearance(snapshot())

  watch(
    [
      menuGroupCollapsible,
      menuUniqueOpened,
      menuGroupHeaderVisible,
      navbarFixed,
      sidebarFixed,
      sidebarPushContent,
      primaryColor,
      fontFamily,
      fontSize,
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
    primaryColor.value = defaults.primaryColor
    fontFamily.value = defaults.fontFamily
    fontSize.value = defaults.fontSize
  }

  return {
    menuGroupCollapsible,
    menuUniqueOpened,
    menuGroupHeaderVisible,
    navbarFixed,
    sidebarFixed,
    sidebarPushContent,
    primaryColor,
    fontFamily,
    fontSize,
    reset,
  }
})
