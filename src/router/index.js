import { createRouter, createWebHistory } from 'vue-router';
import HeadmanView from '../views/HeadmanView.vue';
import StudentView from '../views/StudentView.vue';
import TeacherView from '../views/TeacherView.vue';
import RegisterView from '../views/RegisterView.vue';
import LoginView from '../views/LoginView.vue';
import HomeView from '../views/HomeView.vue';

const routes = [
  { 
    path: '/', 
    name: 'Headman', 
    component: HeadmanView, 
    meta: { requiresAuth: true, role: 'headman' } 
  },
  { 
    path: '/dashboard', 
    name: 'Student', 
    component: StudentView, 
    meta: { requiresAuth: true, role: 'student' } 
  },
  { 
    path: '/teacher', 
    name: 'Teacher', 
    component: TeacherView, 
    meta: { requiresAuth: true, role: 'teacher' } 
  },
  { 
    path: '/register', 
    name: 'Register', 
    component: RegisterView 
  },
  { 
    path: '/login', 
    name: 'Login', 
    component: LoginView 
  },
  { 
    path: '/home', 
    name: 'home', 
    component: HomeView 
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token');
  const userRole = localStorage.getItem('userRole');

  // Если маршрут требует авторизацию
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // Если пользователь не авторизован, перенаправляем на логин
      next('/login');
    } else if (to.meta.role && to.meta.role !== userRole) {
      // Если роль не соответствует, перенаправляем на логин или главную страницу
      next('/home');
    } else {
      // Роль и авторизация в порядке, пропускаем
      next();
    }
  } else {
    // Маршрут не требует авторизации (login, register), пропускаем
    next();
  }
});

export default router;