import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const breadcrumb = ref<string[]>([])
  /** 移动端遮罩模式：侧栏浮动在内容上方 */
  const mobileOverlay = ref(false)
  /** 用户主动折叠状态，用于恢复 */
  const userCollapsed = ref(false)

  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
    userCollapsed.value = sidebarCollapsed.value
  }

  function setBreadcrumb(items: string[]): void {
    breadcrumb.value = items
  }

  function setMobileOverlay(val: boolean): void {
    mobileOverlay.value = val
  }

  function closeMobileOverlay(): void {
    mobileOverlay.value = false
  }

  return { sidebarCollapsed, breadcrumb, userCollapsed, mobileOverlay, toggleSidebar, setBreadcrumb, setMobileOverlay, closeMobileOverlay }
})
