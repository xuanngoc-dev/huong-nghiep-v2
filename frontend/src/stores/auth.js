import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchMe, login as loginApi, register as registerApi } from '@/api/auth'
import menuData from '@/data/menu.json'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => Boolean(token.value))
  const displayName = computed(() => user.value?.ho_ten || user.value?.email || '')
  /** Menu sidebar — sau này lọc theo vai_tro nếu cần */
  const menuGroups = computed(() => menuData)

  function setToken(value) {
    token.value = value || ''
    if (value) {
      localStorage.setItem('token', value)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUser(value) {
    user.value = value
  }

  function applyAuth(data) {
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  async function register(payload) {
    const data = await registerApi(payload)
    return applyAuth(data)
  }

  async function login(payload) {
    const data = await loginApi(payload)
    return applyAuth(data)
  }

  async function loadMe() {
    if (!token.value) {
      user.value = null
      return null
    }
    try {
      const data = await fetchMe()
      setUser(data)
      return data
    } catch {
      logout()
      return null
    }
  }

  function logout() {
    setToken('')
    user.value = null
  }

  return {
    token,
    user,
    isAuthenticated,
    displayName,
    menuGroups,
    setToken,
    setUser,
    register,
    login,
    loadMe,
    logout,
  }
})
