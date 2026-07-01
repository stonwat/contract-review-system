<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import SideMenu from './SideMenu.vue'
import NavBar from './NavBar.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const route = useRoute()
const router = useRouter()

const breadcrumb = computed(() => {
  const matched = route.matched.filter((r) => r.meta?.title)
  return matched.length ? matched.map((r) => r.meta.title as string) : [route.meta.title as string]
})

appStore.setBreadcrumb(breadcrumb.value)

function onLogout(): void {
  router.push('/login')
}
</script>

<template>
  <el-container class="layout">
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'">
      <SideMenu :collapse="appStore.sidebarCollapsed" />
    </el-aside>
    <el-container>
      <el-header>
        <NavBar :breadcrumb="appStore.breadcrumb" @toggle="appStore.toggleSidebar" @logout="onLogout" />
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
</style>
