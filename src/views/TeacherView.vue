<template>
    <div class="container mt-5">
      <h1 class="text-gradient">Мои предметы</h1>
      <button @click="logout" class="btn btn-logout mb-3 animate-btn">Выйти</button>
  
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h3 class="text-gradient d-flex justify-content-between align-items-center">
            Предметы
            <button @click="showModal = true" class="btn btn-filter animate-btn">Добавить предмет</button>
          </h3>
  
          <select v-model="selectedSubject" @change="fetchAttendance" class="form-select mb-3">
            <option v-for="subject in subjects" :value="subject.id" :key="subject.id">{{ subject.name }}</option>
          </select>
  
          <div class="mb-3">
            <button @click="setFilter('day')" class="btn btn-filter animate-btn me-2">За день</button>
            <input v-if="filterType === 'day'" type="date" v-model="selectedDate" @change="fetchAttendance" class="form-control d-inline-block w-auto ms-2" />
            <button @click="setFilter('week')" class="btn btn-filter animate-btn me-2">За неделю</button>
            <button @click="setFilter('month')" class="btn btn-filter animate-btn me-2">За месяц</button>
            <!-- Кнопки сортировки -->
            <button @click="sortByPresent" class="btn btn-filter animate-btn me-2 ms-3">Присутствующие</button>
            <button @click="sortByAbsent" class="btn btn-filter animate-btn me-2">Отсутствующие</button>
            <button @click="showAll" class="btn btn-filter animate-btn">Все</button>
          </div>
  
          <table class="table table-hover" v-if="attendances.length">
            <thead>
              <tr>
                <th>Имя студента</th>
                <th>Группа</th>
                <th>Посещаемость</th>
                <th>Причина</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="att in filteredAttendances" :key="att.id">
                <td>{{ att.student_name }}</td>
                <td>{{ att.group_number }}</td>
                <td>{{ att.attendance }}</td>
                <td>{{ att.reason }}</td>
                <td>{{ att.date }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else>Нет данных за выбранный период</p>
        </div>
      </div>
  
      <!-- Модальное окно для добавления предмета -->
      <div v-if="showModal" class="modal-overlay">
        <div class="modal-content">
          <h4 class="text-gradient">Добавить новый предмет</h4>
          <input v-model="newSubjectName" type="text" class="form-control mb-3" placeholder="Название предмета" />
          <div class="d-flex justify-content-end">
            <button @click="showModal = false" class="btn btn-secondary me-2">Отмена</button>
            <button @click="addSubject" class="btn btn-filter animate-btn">Добавить</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        subjects: [],
        selectedSubject: null,
        attendances: [],
        filteredAttendances: [],
        filterType: 'day',
        selectedDate: new Date().toISOString().split('T')[0],
        showModal: false,
        newSubjectName: '',
        sortFilter: null
      };
    },
    created() {
      this.fetchSubjects();
    },
    methods: {
      fetchSubjects() {
        this.$axios.get('/api/subjects')
          .then(response => {
            this.subjects = response.data.filter(s => s.teacher_id === parseInt(localStorage.getItem('userId')));
            if (this.subjects.length && !this.selectedSubject) {
              this.selectedSubject = this.subjects[0].id;
              this.fetchAttendance();
            }
          })
          .catch(error => {
            console.error('Ошибка загрузки предметов:', error);
          });
      },
      fetchAttendance() {
        if (this.selectedSubject) {
          let url = `/api/teacher/attendance/${this.selectedSubject}?filter=${this.filterType}`;
          if (this.filterType === 'day' && this.selectedDate) {
            url += `&date=${this.selectedDate}`;
          }
          this.$axios.get(url)
            .then(response => {
              this.attendances = response.data;
              this.applySortFilter();
            })
            .catch(error => {
              console.error('Ошибка загрузки посещаемости:', error);
            });
        }
      },
      setFilter(type) {
        this.filterType = type;
        this.fetchAttendance();
      },
      sortByPresent() {
        this.sortFilter = 'present';
        this.applySortFilter();
      },
      sortByAbsent() {
        this.sortFilter = 'absent';
        this.applySortFilter();
      },
      showAll() {
        this.sortFilter = null;
        this.applySortFilter();
      },
      applySortFilter() {
        if (this.sortFilter === 'present') {
          this.filteredAttendances = this.attendances.filter(att => att.attendance === 'П');
        } else if (this.sortFilter === 'absent') {
          this.filteredAttendances = this.attendances.filter(att => att.attendance === 'Н');
        } else {
          this.filteredAttendances = [...this.attendances];
        }
      },
      logout() {
        this.$axios.post('/api/logout')
          .then(() => {
            localStorage.removeItem('token');
            localStorage.removeItem('userRole');
            localStorage.removeItem('userId');
            this.$router.push('/login');
          });
      },
      addSubject() {
        if (!this.newSubjectName.trim()) return;
        this.$axios.post('/api/subjects', {
          name: this.newSubjectName
        })
          .then(response => {
            const newId = response.data.id;
            this.subjects.push({ id: newId, name: this.newSubjectName, teacher_id: parseInt(localStorage.getItem('userId')) });
            this.selectedSubject = newId;
            this.newSubjectName = '';
            this.showModal = false;
            this.fetchAttendance();
          })
          .catch(error => {
            console.error('Ошибка при добавлении предмета:', error);
          });
      }
    },
    watch: {
      attendances() {
        this.applySortFilter();
      }
    }
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
  h1, h3 {
    font-weight: 600;
  }
  .text-gradient {
    background: linear-gradient(90deg, #6b48ff, #00ddeb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .card {
    background: white;
    border-radius: 15px;
    border: none;
  }
  .btn-logout,
  .btn-filter {
    background: linear-gradient(90deg, #6b48ff, #00ddeb);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
  }
  .animate-btn {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  .animate-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }
  .table {
    background: white;
    border-radius: 10px;
    overflow: hidden;
  }
  .table th {
    background: linear-gradient(90deg, #6b48ff, #00ddeb);
    color: white;
  }
  .table td {
    vertical-align: middle;
  }
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
  }
  .modal-content {
    background: #fff;
    border-radius: 15px;
    padding: 30px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
  }
  </style>