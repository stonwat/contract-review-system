import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getAdminInfo, saveToken, getRole, getCity, type AdminInfo, type Role } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const adminInfo = ref<AdminInfo | null>(getAdminInfo())
  const role = ref<Role>(getRole())
  const city = ref<string | null>(getCity())

  const isLoggedIn = computed(() => !!token.value)
  const isSuperAdmin = computed(() => role.value === 'super_admin')
  const isCityAdmin = computed(() => role.value === 'city_admin')
  const canOperate = computed(() => role.value !== 'viewer')      // 可操作/确认/修正
  const canExport = computed(() => role.value !== 'viewer')       // 可导出
  const canDelete = computed(() => role.value === 'super_admin')  // 可删除
  const canManageAdmins = computed(() => role.value === 'super_admin') // 可管理账号

  // 地市操作权限：city_admin 只能操作自己地市的项目
  function canOperateCity(projectCity: string | null | undefined): boolean {
    if (role.value === 'super_admin') return true
    if (role.value === 'city_admin') return projectCity === city.value
    return false
  }

  async function login(username: string, password: string): Promise<void> {
    const resp = await apiLogin(username, password)
    saveToken(resp)
    token.value = resp.access_token
    adminInfo.value = resp.admin
    role.value = resp.admin.role
    city.value = resp.admin.city ?? null
  }

  function logout(): void {
    apiLogout()
    token.value = ''
    adminInfo.value = null
    role.value = 'viewer'
    city.value = null
  }

  return {
    token, adminInfo, role, city,
    isLoggedIn, isSuperAdmin, isCityAdmin, canOperate, canExport, canDelete, canManageAdmins,
    canOperateCity,
    login, logout,
  }
})
