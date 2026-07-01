<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  Odometer,
  Document,
  DataAnalysis,
  Clipboard,
  Warning,
  DataBoard,
} from '@element-plus/icons-vue'

defineProps<{ collapse: boolean }>()

const router = useRouter()

interface MenuItem {
  index: string
  title: string
  icon: unknown
}

const menus: MenuItem[] = [
  { index: '/dashboard', title: '仪表盘', icon: Odometer },
  { index: '/contracts', title: '合同管理', icon: Document },
  { index: '/comparisons', title: '比对审查', icon: DataAnalysis },
  { index: '/acceptance', title: '验收管理', icon: Clipboard },
  { index: '/risks', title: '风险看板', icon: Warning },
  { index: '/reports', title: '报表中心', icon: DataBoard },
]

function handleSelect(index: string): void {
  router.push(index)
}
</script>

<template>
  <el-menu
    :collapse="collapse"
    :default-active="$route.path"
    class="side-menu"
    @select="handleSelect"
  >
    <el-menu-item v-for="m in menus" :key="m.index" :index="m.index">
      <el-icon><component :is="m.icon" /></el-icon>
      <template #title>{{ m.title }}</template>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
.side-menu {
  height: 100%;
  border-right: none;
}
</style>
