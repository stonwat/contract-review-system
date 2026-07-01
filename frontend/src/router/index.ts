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
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
      { path: 'contracts', name: 'ContractList', component: () => import('@/views/contracts/ContractList.vue') },
      { path: 'contracts/:id', name: 'ContractDetail', component: () => import('@/views/contracts/ContractDetail.vue') },
      { path: 'comparisons', name: 'ComparisonReview', component: () => import('@/views/comparisons/ComparisonReview.vue') },
      { path: 'acceptance', name: 'AcceptanceManage', component: () => import('@/views/acceptance/AcceptanceManage.vue') },
      { path: 'risks', name: 'RiskDashboard', component: () => import('@/views/risks/RiskDashboard.vue') },
      { path: 'reports', name: 'ReportCenter', component: () => import('@/views/reports/ReportCenter.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (!to.meta.public && !authStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
