import { createRouter, createWebHistory } from 'vue-router'
import Mall from '@/views/Mall.vue'
import Cart from '@/views/Cart.vue'
import Orders from '@/views/Orders.vue'
import Users from '@/views/Users.vue'

const routes = [
  { path: '/', component: Mall },
  { path: '/cart', component: Cart },
  { path: '/orders', component: Orders },
  { path: '/users', component: Users }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
