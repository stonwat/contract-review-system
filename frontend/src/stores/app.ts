import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const breadcrumb = ref<string[]>([])

  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setBreadcrumb(items: string[]): void {
    breadcrumb.value = items
  }

  return { sidebarCollapsed, breadcrumb, toggleSidebar, setBreadcrumb }
})
