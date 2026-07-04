<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/SvgIcon.vue'

defineProps<{ collapse: boolean }>()
const router = useRouter()
const authStore = useAuthStore()

interface MenuItem {
  index: string
  title: string
  icon: 'dashboard' | 'project' | 'report' | 'account'
  roles?: string[]
}

const menus: MenuItem[] = [
  { index: '/dashboard', title: '仪表盘', icon: 'dashboard' },
  { index: '/projects', title: '项目管理', icon: 'project' },
  { index: '/reports', title: '报表中心', icon: 'report' },
  { index: '/admins', title: '账号管理', icon: 'account', roles: ['super_admin'] },
]

const visibleMenus = computed(() =>
  menus.filter((m) => !m.roles || m.roles.includes(authStore.role)),
)

function handleSelect(index: string): void {
  router.push(index)
}
</script>

<template>
  <div class="sidebar-wrapper">
    <!-- Logo 区域 -->
    <div class="logo-area" :class="{ collapsed: collapse }">
      <div class="logo-icon">审</div>
      <transition name="fade">
        <span v-show="!collapse" class="logo-text">合同审查系统</span>
      </transition>
    </div>

    <!-- 菜单 -->
    <el-menu
      :collapse="collapse"
      :default-active="$route.path"
      class="side-menu"
      background-color="transparent"
      text-color="var(--color-sidebar-text)"
      active-text-color="#ffffff"
      @select="handleSelect"
    >
      <el-menu-item v-for="m in visibleMenus" :key="m.index" :index="m.index">
        <SvgIcon :name="m.icon" :size="18" color="inherit" />
        <template #title>
          <span>{{ m.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>

    <!-- 底部版本号 -->
    <div v-show="!collapse" class="sidebar-footer">
      <span class="version-tag">v2.0 · 国企AI审查</span>
    </div>
  </div>
</template>

<style scoped>
.sidebar-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-sidebar-bg);
  border-right: 1px solid var(--color-sidebar-border);
  overflow: hidden;
}

/* Logo 区域 */
.logo-area {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid var(--color-sidebar-border);
  flex-shrink: 0;
  overflow: hidden;
  transition: padding 0.3s;
}
.logo-area.collapsed {
  padding: 0 12px;
  justify-content: center;
}

.logo-icon {
  width: 32px;
  height: 32px;
  min-width: 32px;
  background: var(--color-primary-gradient);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(196, 29, 52, 0.4);
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  letter-spacing: 1px;
}

/* 菜单 */
.side-menu {
  flex: 1;
  padding: 8px 0;
  border-right: none !important;
  overflow-y: auto;
}
.side-menu:not(.el-menu--collapse) {
  width: 100%;
}

/* 菜单项 */
.side-menu .el-menu-item {
  margin: 2px 8px;
  border-radius: 8px;
  height: 42px;
  line-height: 42px;
  transition: all 0.2s ease;
}
.side-menu .el-menu-item:hover {
  background: var(--color-sidebar-hover-bg) !important;
  color: var(--color-primary-light) !important;
}
.side-menu .el-menu-item.is-active {
  background: var(--color-sidebar-active-bg) !important;
  color: #fff !important;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(196, 29, 52, 0.3);
}
.side-menu .el-menu-item.is-active .el-icon {
  color: #fff !important;
}

/* 折叠模式 */
.el-menu--collapse .el-menu-item {
  margin: 2px 8px;
  border-radius: 8px;
  width: calc(100% - 16px);
}

/* 底部 */
.sidebar-footer {
  flex-shrink: 0;
  text-align: center;
  padding: 12px 16px;
  border-top: 1px solid var(--color-sidebar-border);
}
.version-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  letter-spacing: 0.5px;
}

/* 淡入淡出过渡 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
