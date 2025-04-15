<template>
    <login-form :is-register="true" />
  </template>
  
  <script>
  import LoginForm from '../components/LoginForm.vue';
  
  export default {
    components: { LoginForm }
  };
  </script>