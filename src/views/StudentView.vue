<template>
    <div class="container mt-5">
      <h1 class="text-gradient">Моя посещаемость</h1>
      <button @click="logout" class="btn btn-logout mb-3 animate-btn">Выйти</button>
  
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <p><strong>Имя:</strong> {{ student.name }}</p>
          <p><strong>Группа:</strong> {{ student.group_number }}</p>
          <h3 class="text-gradient">Посещаемость:</h3>
          <ul>
            <li v-for="(att, index) in student.attendances" :key="index">
              {{ att.subject }}: {{ att.attendance }} <span v-if="att.reason">({{ att.reason }})</span> - {{ att.date }}
            </li>
          </ul>
        </div>
      </div>
  
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="text-gradient">Уведомления</h3>
          <div v-if="notifications.length">
            <div v-for="notif in notifications" :key="notif.id" class="alert alert-light shadow-sm">
              {{ notif.message }} (Предмет: {{ notif.subject_name }}, Дата: {{ notif.attendance_date }})
              <button @click="openReasonModal(notif)" class="btn btn-notify animate-btn ms-3">Ответить</button>
            </div>
          </div>
          <p v-else>Уведомлений нет</p>
        </div>
      </div>
  
      <div class="modal" :class="{ 'd-block': showModal }" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title text-gradient">Укажите причину</h5>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <select v-model="selectedReason" class="form-select mb-3">
                <option value="Уважительная причина">Уважительная причина</option>
                <option value="Болезнь (справка)">Болезнь (справка)</option>
                <option value="Другое">Другое</option>
              </select>
              <input v-if="selectedReason === 'Болезнь (справка)'" type="file" class="form-control" @change="handleFileUpload" />
              <textarea v-if="selectedReason === 'Другое'" v-model="customReason" class="form-control" placeholder="Опишите причину"></textarea>
            </div>
            <div class="modal-footer">
              <button @click="submitReason" class="btn btn-primary animate-btn">Отправить</button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show" v-if="showModal"></div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        student: { attendances: [] },
        notifications: [],
        showModal: false,
        selectedReason: '',
        customReason: '',
        file: null,
        currentNotif: null
      };
    },
    created() {
      this.fetchStudentData();
      this.fetchNotifications();
    },
    methods: {
      fetchStudentData() {
        this.$axios.get('/api/student')
          .then(response => {
            this.student = response.data;
          })
          .catch(error => {
            console.error('Ошибка загрузки данных студента:', error);
          });
      },
      fetchNotifications() {
        this.$axios.get('/api/notifications')
          .then(response => {
            this.notifications = response.data;
          })
          .catch(error => {
            console.error('Ошибка загрузки уведомлений:', error);
          });
      },
      openReasonModal(notif) {
        this.currentNotif = notif;
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;
        this.selectedReason = '';
        this.customReason = '';
        this.file = null;
      },
      handleFileUpload(event) {
        this.file = event.target.files[0];
      },
      submitReason() {
        const reason = this.selectedReason === 'Другое' ? this.customReason : this.selectedReason;
        const date = this.currentNotif.attendance_date; // Используем дату из уведомления
        this.$axios.post('/api/reason', {
          notification_id: this.currentNotif.id,
          response: reason,
          date: date
        })
        .then(() => {
          this.fetchNotifications();
          this.fetchStudentData();
          this.closeModal();
          alert('Причина отправлена');
        })
        .catch(error => {
          console.error('Ошибка отправки причины:', error);
        });
      },
      logout() {
        this.$axios.post('/api/logout')
          .then(() => {
            localStorage.removeItem('token');
            localStorage.removeItem('userRole');
            localStorage.removeItem('userId');
            this.$router.push('/login');
          });
      }
    }
  };
  </script>
  
  <style scoped>
  .container { max-width: 1200px; }
  .card { background: white; border-radius: 15px; border: none; }
  .text-gradient { background: linear-gradient(90deg, #6b48ff, #00ddeb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .btn-logout, .btn-primary { background: linear-gradient(90deg, #6b48ff, #00ddeb); color: white; border: none; border-radius: 25px; }
  .btn-notify { background: linear-gradient(90deg, #ff48a5, #ff6b6b); color: white; border: none; border-radius: 20px; }
  .animate-btn { transition: transform 0.3s ease, box-shadow 0.3s ease; }
  .animate-btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); }
  .modal.d-block { background-color: rgba(0, 0, 0, 0.5); }
  </style>