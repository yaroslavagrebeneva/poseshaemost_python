<template>
  <div id="app" class="min-vh-100 d-flex flex-column">
    <!-- Навигационная панель -->
    <nav class="navbar navbar-expand-lg shadow-sm">
      <div class="container">
        <router-link to="/" class="navbar-brand text-gradient">
          <img src="@/assets/logo.jpg" alt="Logo" class="nav-icon me-2" /> Посещаемость
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item" v-for="link in navLinks" :key="link.path">
              <router-link :to="link.path" class="nav-link d-flex align-items-center gap-2" @click="link.action ? link.action : null">
                <img :src="link.icon" alt="icon" class="nav-icon" />
                <span class="badge-pill bg-glass">{{ link.text }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Основной контент -->
    <main class="flex-grow-1">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      userRole: localStorage.getItem('userRole') || null
    };
  },
  computed: {
    navLinks() {
      const baseLinks = [
        { path: '/home', text: 'Главная', icon: require('@/assets/home.png') }
      ];

      if (!this.userRole) {
        return [
          ...baseLinks,
          { path: '/login', text: 'Войти', icon: require('@/assets/login.png') },
          { path: '/register', text: 'Регистрация', icon: require('@/assets/register.png') }
        ];
      }

      const roleLinks = {
        student: [
          { path: '/dashboard', text: 'Кабинет', icon: require('@/assets/dashboard.png') }
        ],
        headman: [
          { path: '/', text: 'Журнал', icon: require('@/assets/journal.png') },
          { path: '/dashboard', text: 'Кабинет', icon: require('@/assets/dashboard.png') }
        ],
        teacher: [
          { path: '/teacher', text: 'Преподаватель', icon: require('@/assets/teacher.png') }
        ]
      };

      return [
        ...baseLinks,
        ...(roleLinks[this.userRole] || []),
        { 
          path: '/login', 
          text: 'Выйти', 
          icon: require('@/assets/logout.png'), 
          action: this.logout 
        }
      ];
    }
  },
  methods: {
    logout() {
      this.$axios.post('/api/logout')
        .then(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userRole');
          localStorage.removeItem('userId');
          this.userRole = null; // Обновляем роль в компоненте
          this.$router.push('/login');
        })
        .catch(error => {
          console.error('Ошибка при выходе:', error);
        });
    },
    updateUserRole() {
      this.userRole = localStorage.getItem('userRole');
    }
  },
  created() {
    // Слушаем изменения роли при входе/выходе
    window.addEventListener('storage', this.updateUserRole);
    this.updateUserRole(); // Проверяем роль при загрузке
  },
  beforeUnmount() {  // Заменили beforeDestroy на beforeUnmount
    window.removeEventListener('storage', this.updateUserRole);
  }
};
</script>

<style>
body {
  background: linear-gradient(135deg, #f8f9fa 0%, #e0e7ff 100%);
  margin: 0;
  font-family: 'Segoe UI', sans-serif;
}

#app {
  background: transparent;
}

.navbar {
  background: white;
  padding: 15px 0;
  border-bottom: 1px solid rgba(107, 72, 255, 0.1);
}

.navbar-brand, .nav-link {
  font-weight: 500;
  position: relative;
  display: flex;
  align-items: center;
}

.text-gradient {
  background: linear-gradient(90deg, #6b48ff, #00ddeb);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-link:hover {
  transform: translateY(-2px);
  transition: transform 0.3s ease;
}

.nav-icon {
  width: 20px;
  height: 20px;
  vertical-align: middle;
}

/* Полупрозрачный стеклянный бейдж */
.bg-glass {
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3); /* Стеклянный эффект */
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  box-shadow: 0 0 10px rgba(0,0,0,0.05);
  transition: background 0.3s ease;
}

.bg-glass:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
