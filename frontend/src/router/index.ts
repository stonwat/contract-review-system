import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardView.vue'), meta: { title: '仪表盘', roles: ['super_admin', 'city_admin', 'viewer'] } },
      { path: 'projects', name: 'ProjectList', component: () => import('@/views/projects/ProjectList.vue'), meta: { title: '项目管理', roles: ['super_admin', 'city_admin', 'viewer'] } },
      { path: 'projects/:contractNo', name: 'ProjectDetail', component: () => import('@/views/projects/ProjectDetail.vue'), meta: { title: '项目详情', roles: ['super_admin', 'city_admin', 'viewer'] } },
      { path: 'reports', name: 'ReportCenter', component: () => import('@/views/reports/ReportCenter.vue'), meta: { title: '报表中心', roles: ['super_admin', 'city_admin', 'viewer'] } },
      { path: 'admins', name: 'AdminManage', component: () => import('@/views/admins/AdminManage.vue'), meta: { title: '账号管理', roles: ['super_admin'] } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // 未登录 → 跳转登录页
  if (!to.meta.public && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 角色权限检查
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && !requiredRoles.includes(authStore.role)) {
    next('/dashboard')
    return
  }

  next()
})

export default router
