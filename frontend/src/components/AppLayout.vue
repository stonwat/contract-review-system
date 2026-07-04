<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import SideMenu from './SideMenu.vue'
import NavBar from './NavBar.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const breadcrumb = computed(() => {
  const matched = route.matched.filter((r) => r.meta?.title)
  return matched.length
    ? matched.map((r) => r.meta.title as string)
    : [route.meta.title as string]
})

watch(breadcrumb, (val) => {
  appStore.setBreadcrumb(val)
}, { immediate: true })

function onLogout(): void {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout-wrapper">
    <!-- 侧栏 -->
    <aside
      class="layout-sidebar"
      :class="{ collapsed: appStore.sidebarCollapsed }"
    >
      <SideMenu :collapse="appStore.sidebarCollapsed" />
    </aside>

    <!-- 主区域 -->
    <div class="layout-main">
      <!-- 顶栏 -->
      <header class="layout-header">
        <NavBar
          :breadcrumb="appStore.breadcrumb"
          :collapsed="appStore.sidebarCollapsed"
          @toggle="appStore.toggleSidebar"
          @logout="onLogout"
        />
      </header>

      <!-- 内容区 -->
      <main class="layout-content">
        <div class="content-inner">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧栏 */
.layout-sidebar {
  width: var(--color-sidebar-width);
  flex-shrink: 0;
  transition: width 0.3s ease;
  overflow: hidden;
  background: var(--color-sidebar-bg);
  z-index: 100;
}
.layout-sidebar.collapsed {
  width: var(--color-sidebar-width-collapsed);
}

/* 主区域 */
.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-bg);
}

/* 顶栏 */
.layout-header {
  height: var(--color-header-height);
  flex-shrink: 0;
  z-index: 10;
}

/* 内容区 */
.layout-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
}
.content-inner {
  min-height: 100%;
}
</style>
