<script setup lang="ts">
import { computed } from 'vue'
import { Expand, Fold } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/SvgIcon.vue'

defineProps<{ breadcrumb: string[]; collapsed: boolean }>()
const emit = defineEmits<{ toggle: []; logout: [] }>()

const authStore = useAuthStore()

const roleTag = computed(() => {
  switch (authStore.role) {
    case 'super_admin':
      return { type: 'danger' as const, text: '超级管理员' }
    case 'city_admin':
      return { type: 'warning' as const, text: `地市管理员（${authStore.city || ''}）` }
    default:
      return { type: 'info' as const, text: '只读用户' }
  }
})
</script>

<template>
  <div class="navbar">
    <!-- 左侧：折叠按钮 + 面包屑 -->
    <div class="navbar-left">
      <el-icon class="toggle-btn" @click="emit('toggle')">
        <Expand v-if="collapsed" />
        <Fold v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(item, idx) in breadcrumb" :key="idx">
          {{ item }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 右侧：用户信息 -->
    <div class="navbar-right">
      <!-- AI 状态指示 -->
      <div class="ai-status hide-mobile">
        <span class="ai-dot"></span>
        <span class="ai-label">AI 就绪</span>
      </div>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 角色标签 -->
      <el-tag
        :type="roleTag.type"
        size="small"
        effect="plain"
        class="role-tag"
      >
        {{ roleTag.text }}
      </el-tag>

      <!-- 用户名 -->
      <span class="admin-name">
        {{ authStore.adminInfo?.display_name || authStore.adminInfo?.username }}
      </span>

      <!-- 退出 -->
      <el-tooltip content="退出登录" placement="bottom">
        <el-button
          class="logout-btn"
          text
          @click="emit('logout')"
        >
          <SvgIcon name="logout" :size="16" color="inherit" style="margin-right: 4px" />
          退出
        </el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  background: var(--color-header-bg);
  border-bottom: 1px solid var(--color-header-border);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.toggle-btn {
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: color 0.2s;
}
.toggle-btn:hover {
  color: var(--color-primary);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* AI 状态指示 */
.ai-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--color-primary-gradient-subtle);
  border-radius: 20px;
  border: 1px solid rgba(196, 29, 52, 0.15);
}
.ai-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #67c23a;
  animation: pulse-dot 2s ease-in-out infinite;
}
.ai-label {
  font-size: 12px;
  color: var(--color-primary);
  font-weight: 500;
}

/* 分隔线 */
.divider {
  width: 1px;
  height: 20px;
  background: var(--color-border);
}

/* 角色标签 */
.role-tag {
  font-weight: 500;
}
.role-tag.el-tag--danger {
  background: rgba(196, 29, 52, 0.1);
  border-color: rgba(196, 29, 52, 0.2);
  color: var(--color-primary);
}

/* 用户名 */
.admin-name {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
}

/* 退出按钮 */
.logout-btn {
  color: var(--color-text-secondary) !important;
  transition: color 0.2s;
}
.logout-btn:hover {
  color: var(--color-primary) !important;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
