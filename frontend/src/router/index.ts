import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '仪表盘', icon: 'Dashboard' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UsersView.vue'),
        meta: { title: '用户管理', icon: 'User' },
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/roles/RolesView.vue'),
        meta: { title: '角色管理', icon: 'UserFilled' },
      },
      {
        path: 'teams',
        name: 'Teams',
        component: () => import('@/views/teams/TeamsView.vue'),
        meta: { title: '团队管理', icon: 'Team' },
      },
      {
        path: 'scripts',
        name: 'Scripts',
        component: () => import('@/views/scripts/ScriptsView.vue'),
        meta: { title: '脚本管理', icon: 'Document' },
      },
      {
        path: 'repos',
        name: 'Repos',
        component: () => import('@/views/repos/ReposView.vue'),
        meta: { title: '仓库管理', icon: 'Folder' },
      },
      {
        path: 'pipelines',
        name: 'Pipelines',
        component: () => import('@/views/pipelines/PipelinesView.vue'),
        meta: { title: '流水线管理', icon: 'Connection' },
      },
      {
        path: 'gates',
        name: 'Gates',
        component: () => import('@/views/gates/GatesView.vue'),
        meta: { title: '门禁管理', icon: 'Lock' },
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/system/SystemView.vue'),
        meta: { title: '系统配置', icon: 'Setting' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/auth/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!localStorage.getItem('accessToken')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth !== false)

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
