import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import MapPage from '@/views/MapPage.vue'
import AnalyticsPage from '@/views/AnalyticsPage.vue'
import SubmissionPage from '@/views/SubmissionPage.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Map',
    component: MapPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: AnalyticsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/submission',
    name: 'Submission',
    component: SubmissionPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('token')
  const userInfo = JSON.parse(sessionStorage.getItem('userInfo') || '{}')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && userInfo.role !== 'admin') {
    next('/')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
