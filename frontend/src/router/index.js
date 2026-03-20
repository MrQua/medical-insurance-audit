import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'
import Chat from '@/views/Chat.vue'
import Patients from '@/views/Patients.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/chat',
    children: [
      {
        path: 'chat',
        name: 'Chat',
        component: Chat,
        meta: { title: '智能对话', icon: 'ChatDotRound' }
      },
      {
        path: 'patients',
        name: 'Patients',
        component: Patients,
        meta: { title: '患者管理', icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
