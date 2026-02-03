import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import Layout from '@/layout/index.vue'

const routes = [
  // 1. 登录页 (不需要 Layout)
  {
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  
  // 2. 首页仪表盘
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页仪表盘', requiresAuth: true }
      }
    ]
  },

  // 3. 系统管理 - 门店管理
  {
    path: '/dept',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/dept/index.vue'),
        meta: { title: '门店管理', requiresAuth: true }
      }
    ]
  },

  // 4. 系统管理 - 角色管理
  {
    path: '/role',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/role/index.vue'),
        meta: { title: '角色管理', requiresAuth: true }
      }
    ]
  },

  // 5. 系统管理 - 用户管理
  {
    path: '/user',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      }
    ]
  },

  // 6. 商品资料
  {
    path: '/product',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/product/index.vue'),
        meta: { title: '商品资料', requiresAuth: true }
      }
    ]
  },

  // 7. 客户列表 (新增)
  {
    path: '/customer',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/customer/index.vue'),
        meta: { title: '客户列表', requiresAuth: true }
      }
    ]
  },

  // 8. 客资分配规则 (新增)
  {
    path: '/allocation',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/allocation/index.vue'),
        meta: { title: '客资分配', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // 检查是否需要登录权限
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router