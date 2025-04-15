<template>
    <div class="container mt-5">
      <h1>{{ isRegister ? 'Регистрация' : 'Вход' }}</h1>
      <div v-if="message" :class="['alert', error ? 'alert-danger' : 'alert-success']">{{ message }}</div>
      <form @submit.prevent="submit">
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="email" required>
          <small v-if="isRegister" class="form-text text-muted">Используйте _teacher или _headman для роли.</small>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Пароль</label>
          <input type="password" class="form-control" id="password" v-model="password" required>
        </div>
        <div v-if="isRegister" class="mb-3">
          <label for="name" class="form-label">ФИО</label>
          <input type="text" class="form-control" id="name" v-model="name" required>
        </div>
        <div v-if="isRegister" class="mb-3">
          <label for="group_number" class="form-label">Номер группы</label>
          <input type="text" class="form-control" id="group_number" v-model="group_number">
        </div>
        <button type="submit" class="btn btn-primary">{{ isRegister ? 'Зарегистрироваться' : 'Войти' }}</button>
        <router-link :to="isRegister ? '/login' : '/register'" class="btn btn-link">
          {{ isRegister ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться' }}
        </router-link>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      isRegister: Boolean
    },
    data() {
      return {
        email: '',
        password: '',
        name: '',
        group_number: '',
        message: '',
        error: false
      };
    },
    methods: {
      submit() {
        const data = {
          email: this.email,
          password: this.password
        };
        if (this.isRegister) {
          data.name = this.name;
          data.group_number = this.group_number;
          this.$axios.post('/api/register', data)
            .then(response => {
              this.message = response.data.message;
              this.error = false;
              setTimeout(() => this.$router.push('/login'), 1000);
            })
            .catch(error => {
              this.message = error.response.data.error;
              this.error = true;
            });
        } else {
          this.$axios.post('/api/login', data)
            .then(response => {
              this.message = response.data.message;
              this.error = false;
              localStorage.setItem('token', response.data.token);
              localStorage.setItem('userRole', response.data.role);
              localStorage.setItem('userId', response.data.user_id);
              setTimeout(() => {
                if (response.data.role === 'headman') this.$router.push('/');
                else if (response.data.role === 'student') this.$router.push('/dashboard');
                else if (response.data.role === 'teacher') this.$router.push('/teacher');
              }, 1000);
            })
            .catch(error => {
              this.message = error.response.data.error;
              this.error = true;
            });
        }
      }
    }
  };
  </script>