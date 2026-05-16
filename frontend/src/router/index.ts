import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/boards' },
    { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
    { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
    { path: '/boards', component: () => import('@/views/BoardsView.vue') },
    { path: '/boards/:id', component: () => import('@/views/BoardView.vue') },
    { path: '/admin', component: () => import('@/views/AdminView.vue'), meta: { admin: true } },
  ],
})

router.beforeEach(async (to) => {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()
  const hasToken = auth.loadFromStorage()

  if (!hasToken && !to.meta.public) return '/login'
  if (hasToken && !auth.user) await auth.fetchMe()
  if (to.meta.public && auth.isAuthenticated) return '/boards'
  if (to.meta.admin && !auth.user?.is_admin) return '/boards'
})

export default router
