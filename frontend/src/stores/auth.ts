import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getAdminInfo, saveToken, type AdminInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const adminInfo = ref<AdminInfo | null>(getAdminInfo())

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string): Promise<void> {
    const resp = await apiLogin(username, password)
    saveToken(resp)
    token.value = resp.access_token
    adminInfo.value = resp.admin
  }

  function logout(): void {
    apiLogout()
    token.value = ''
    adminInfo.value = null
  }

  return { token, adminInfo, isLoggedIn, login, logout }
})
