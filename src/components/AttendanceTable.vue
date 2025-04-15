<template>
    <div>
      <div class="mb-3">
        <label for="subject" class="form-label">Выберите предмет:</label>
        <select v-model="selectedSubject" @change="fetchAttendance" class="form-select">
          <option v-for="subject in subjects" :value="subject.id" :key="subject.id">{{ subject.name }}</option>
        </select>
      </div>
      <table class="table table-bordered" v-if="attendances.length">
        <thead>
          <tr>
            <th>Имя студента</th>
            <th>Номер группы</th>
            <th>Посещаемость</th>
            <th v-if="!readOnly">Действие</th>
            <th v-if="readOnly">Причина</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="att in attendances" :key="att.id">
            <td>{{ att.student_name }}</td>
            <td>{{ att.group_number }}</td>
            <td>
              <select v-model="att.attendance" @change="updateAttendance(att)" :disabled="readOnly">
                <option value="П">П</option>
                <option value="Н">Н</option>
              </select>
              <span v-if="att.reason" class="text-muted"> ({{ att.reason }})</span>
            </td>
            <td v-if="!readOnly">
              <button v-if="att.attendance === 'Н'" @click="openModal(att)" class="btn btn-sm btn-warning">Указать причину</button>
            </td>
            <td v-if="readOnly">{{ att.reason || '-' }}</td>
          </tr>
        </tbody>
      </table>
  
      <!-- Модальное окно -->
      <div class="modal" :class="{ 'd-block': showModal }" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Причина пропуска</h5>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <select v-model="selectedReason" class="form-select">
                <option value="Уважительная причина">Уважительная причина</option>
                <option value="Болезнь (справка)">Болезнь (справка)</option>
                <option value="Другое">Другое</option>
              </select>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-primary" @click="saveReason">Сохранить</button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show" v-if="showModal"></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    props: {
      subjects: {
        type: Array,
        required: true
      },
      readOnly: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        selectedSubject: null,
        attendances: [],
        showModal: false,
        selectedAtt: null,
        selectedReason: ''
      };
    },
    methods: {
      fetchAttendance() {
        if (this.selectedSubject) {
          axios.get(`/api/attendance/${this.selectedSubject}`)
            .then(response => {
              this.attendances = response.data;
            })
            .catch(error => {
              console.error('Ошибка загрузки:', error);
            });
        }
      },
      updateAttendance(att) {
        if (att.attendance === 'Н' && !this.readOnly) {
          this.openModal(att);
        } else {
          att.reason = null;
          this.saveAttendance(att);
        }
      },
      openModal(att) {
        this.selectedAtt = att;
        this.selectedReason = att.reason || '';
        this.showModal = true;
      },
      saveReason() {
        this.selectedAtt.reason = this.selectedReason;
        this.saveAttendance(this.selectedAtt);
        this.closeModal();
      },
      saveAttendance(att) {
        axios.post('/api/update', {
          id: att.id,
          attendance: att.attendance,
          reason: att.reason
        })
        .then(() => {
          this.fetchAttendance();
        })
        .catch(error => {
          console.error('Ошибка сохранения:', error);
        });
      },
      closeModal() {
        this.showModal = false;
        this.selectedReason = '';
      }
    }
  };
  </script>
  
  <style scoped>
  .modal.d-block {
    background-color: rgba(0, 0, 0, 0.5);
  }
  </style>