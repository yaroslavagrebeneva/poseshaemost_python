<template>
  <div class="container mt-5">
    <h1 class="text-gradient">Журнал посещаемости</h1>
    <button @click="logout" class="btn btn-logout mb-3 animate-btn">Выйти</button>

    <div class="card mb-4 shadow-sm">
      <div class="card-body">
        <h3 class="text-gradient">Предметы</h3>
        <attendance-table :subjects="subjects" :read-only="false" />
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h3 class="text-gradient">Студенты моей группы</h3>
        <div class="row mb-3">
          <div class="col-md-6">
            <select v-model="selectedSubject" @change="fetchStudents" class="form-select">
              <option v-for="subject in subjects" :value="subject.id" :key="subject.id">{{ subject.name }}</option>
            </select>
          </div>
          <div class="col-md-6">
            <input type="date" v-model="selectedDate" @change="fetchStudents" class="form-control" />
          </div>
        </div>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Имя</th>
              <th>Группа</th>
              <th>Посещаемость</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.name }}</td>
              <td>{{ student.group_number }}</td>
              <td>
                <select v-model="student.attendance" class="form-select">
                  <option value="">-</option>
                  <option value="П">Присутствовал</option>
                  <option value="Н">Отсутствовал</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
        <button @click="saveChanges" class="btn btn-save mt-3 animate-btn" :disabled="!selectedSubject || !selectedDate">
          Сохранить изменения
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import AttendanceTable from '../components/AttendanceTable.vue';

export default {
  components: { AttendanceTable },
  data() {
    return {
      subjects: [],
      students: [],
      selectedSubject: null,
      selectedDate: new Date().toISOString().split('T')[0] // Сегодняшняя дата по умолчанию
    };
  },
  created() {
    this.fetchSubjects();
  },
  methods: {
    fetchSubjects() {
      this.$axios.get('/api/subjects')
        .then(response => {
          this.subjects = response.data;
          if (this.subjects.length) {
            this.selectedSubject = this.subjects[0].id;
            this.fetchStudents();
          }
        })
        .catch(error => {
          console.error('Ошибка загрузки предметов:', error);
        });
    },
    fetchStudents() {
      if (!this.selectedSubject || !this.selectedDate) return;
      this.$axios.get('/api/students')
        .then(response => {
          this.students = response.data.map(student => ({
            ...student,
            attendance: ''
          }));
          this.$axios.get(`/api/attendance/${this.selectedSubject}?date=${this.selectedDate}`)
            .then(attResponse => {
              attResponse.data.forEach(att => {
                const student = this.students.find(s => s.id === att.student_id);
                if (student) student.attendance = att.attendance;
              });
            })
            .catch(error => {
              console.error('Ошибка загрузки посещаемости:', error);
            });
        })
        .catch(error => {
          console.error('Ошибка загрузки студентов:', error);
        });
    },
    saveChanges() {
      if (!this.selectedSubject || !this.selectedDate) {
        alert('Выберите предмет и дату!');
        return;
      }
      const updates = this.students
        .filter(student => student.attendance !== '')
        .map(student => ({
          student_id: student.id,
          subject_id: this.selectedSubject,
          attendance: student.attendance,
          date: this.selectedDate
        }));

      if (updates.length === 0) {
        alert('Нет изменений для сохранения!');
        return;
      }

      Promise.all(updates.map(update =>
        this.$axios.post('/api/update', update)
      ))
      .then(() => {
        alert('Изменения сохранены!');
        this.fetchStudents();
      })
      .catch(error => {
        console.error('Ошибка сохранения изменений:', error);
        alert('Ошибка при сохранении!');
      });
    },
    logout() {
      this.$axios.post('/api/logout')
        .then(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userRole');
          localStorage.removeItem('userId');
          this.$router.push('/login');
        })
        .catch(error => {
          console.error('Ошибка при выходе:', error);
        });
    }
  }
};
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; }
h1, h3 { font-weight: 600; }
.text-gradient { background: linear-gradient(90deg, #6b48ff, #00ddeb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.card { background: white; border-radius: 15px; border: none; }
.btn-logout { background: linear-gradient(90deg, #6b48ff, #00ddeb); color: white; border: none; padding: 10px 20px; border-radius: 25px; }
.btn-save { background: linear-gradient(90deg, #28a745, #20c997); color: white; border: none; padding: 10px 20px; border-radius: 25px; }
.btn-save:disabled { background: #ccc; cursor: not-allowed; }
.animate-btn { transition: transform 0.3s ease, box-shadow 0.3s ease; }
.animate-btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2); }
.table { background: white; border-radius: 10px; overflow: hidden; }
.table th { background: linear-gradient(90deg, #6b48ff, #00ddeb); color: white; }
.table td { vertical-align: middle; }
</style>