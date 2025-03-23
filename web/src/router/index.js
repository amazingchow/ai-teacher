import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      children: [
        {
          path: '',
          redirect: '/students'
        },
        {
          path: '/students',
          name: 'students',
          component: () => import('../views/students/StudentList.vue')
        },
        {
          path: '/questions',
          name: 'questions',
          component: () => import('../views/questions/QuestionList.vue')
        },
        {
          path: '/recite',
          name: 'recite',
          component: () => import('../views/recite/RecitePage.vue')
        }
      ]
    }
  ]
})

export default router