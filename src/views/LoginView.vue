<template>
    <login-form :is-register="false" />
  </template>
  
  <script>
  import LoginForm from '../components/LoginForm.vue';
  
  export default {
    components: { LoginForm }
  };
  </script>