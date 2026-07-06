<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue'
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

// ── 响应式：自动折叠 + 移动端遮罩 ──
let mqLarge: MediaQueryList | null = null
let mqMobile: MediaQueryList | null = null

function handleMQChange(): void {
  const isMobile = mqMobile?.matches ?? false
  const isLarge = mqLarge?.matches ?? true

  appStore.setMobileOverlay(isMobile)

  if (isMobile) {
    // < 768px: 强制折叠，侧栏浮动
    appStore.sidebarCollapsed = true
  } else if (!isLarge) {
    // 768-1280px: 自动折叠，但固定侧栏
    appStore.sidebarCollapsed = true
  } else {
    // > 1280px: 恢复用户偏好
    appStore.sidebarCollapsed = appStore.userCollapsed
  }
}

onMounted(() => {
  mqLarge = window.matchMedia('(min-width: 1280px)')
  mqMobile = window.matchMedia('(max-width: 768px)')
  mqLarge.addEventListener('change', handleMQChange)
  mqMobile.addEventListener('change', handleMQChange)
  handleMQChange()
})

onUnmounted(() => {
  mqLarge?.removeEventListener('change', handleMQChange)
  mqMobile?.removeEventListener('change', handleMQChange)
})
</script>

<template>
  <div class="layout-wrapper">
    <!-- 移动端遮罩 -->
    <div
      v-if="appStore.mobileOverlay && !appStore.sidebarCollapsed"
      class="layout-overlay"
      @click="appStore.closeMobileOverlay()"
    />

    <!-- 侧栏 -->
    <aside
      class="layout-sidebar"
      :class="{
        collapsed: appStore.sidebarCollapsed,
        overlay: appStore.mobileOverlay,
      }"
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

/* 移动端遮罩 */
.layout-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
}

/* 侧栏 */
.layout-sidebar {
  width: var(--color-sidebar-width);
  flex-shrink: 0;
  transition: width 0.3s ease, transform 0.3s ease;
  overflow: hidden;
  background: var(--color-sidebar-bg);
  z-index: 100;
}
.layout-sidebar.collapsed {
  width: var(--color-sidebar-width-collapsed);
}
/* 移动端浮动模式 */
.layout-sidebar.overlay {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 200;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
}
.layout-sidebar.overlay.collapsed {
  transform: translateX(-100%);
}

/* 主区域 */
.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-canvas);
  min-width: 0;
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
