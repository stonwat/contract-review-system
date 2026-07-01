<script setup lang="ts">
import { Fold, Expand, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{ breadcrumb: string[] }>()
const emit = defineEmits<{ toggle: []; logout: [] }>()

const authStore = useAuthStore()
</script>

<template>
  <div class="navbar">
    <el-icon class="toggle-btn" @click="emit('toggle')">
      <Fold v-if="!$attrs.collapse" />
      <Expand v-else />
    </el-icon>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item v-for="(item, idx) in breadcrumb" :key="idx">{{ item }}</el-breadcrumb-item>
    </el-breadcrumb>
    <div class="spacer" />
    <span class="admin-name">{{ authStore.adminInfo?.display_name || authStore.adminInfo?.username }}</span>
    <el-button type="danger" :icon="SwitchButton" link @click="emit('logout')">退出</el-button>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
}
.toggle-btn {
  font-size: 20px;
  cursor: pointer;
  margin-right: 16px;
}
.spacer {
  flex: 1;
}
.admin-name {
  margin-right: 12px;
  color: #606266;
}
</style>
