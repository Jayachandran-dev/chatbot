import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/login', component: () => import('./views/Login.vue') },
  {
    path: '/',
    component: () => import('./views/Shell.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/sites' },
      { path: 'sites', component: () => import('./views/Sites.vue') },
      { path: 'sites/:id', component: () => import('./views/SiteDetail.vue'), props: true },
    ],
  },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to) => {
  const token = localStorage.getItem('zb_token');
  if (to.meta.requiresAuth && !token) return '/login';
  if (to.path === '/login' && token) return '/sites';
});

export default router;
