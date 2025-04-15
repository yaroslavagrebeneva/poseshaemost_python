<template>
    <v-container class="home-container">
      <v-row justify="center">
        <v-col cols="12" class="text-center">
          <h1 class="main-title">Добро пожаловать!</h1>
        </v-col>
      </v-row>
  
      <!-- Блок О нас -->
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card class="about-us" elevation="4">
            <v-card-title class="text-center">О нас</v-card-title>
            <v-card-text class="text-center">
              <v-img src="@/assets/123.png" contain height="80" class="mb-3" />
              <p>Крымский инженерно-педагогический университет имени Февзи Якубова — высшее учебное заведение Симферополя, основанное в 1993 году с учётом потребностей возвращающихся из депортации крымских татар. Преподавание ведётся на крымскотатарском, русском и украинском языках.</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Контакты -->
      <v-row justify="center">
        <v-col cols="12" md="6" class="text-center">
          <div class="contact-info">
            <p class="contact-text">
              <v-icon>mdi-phone</v-icon>
              Телефон: <a href="tel:+79788049582" class="contact-link">+7 978 804 95 82</a>
            </p>
            <p class="contact-text">
              <v-icon>mdi-telegram</v-icon>
              Telegram: <a href="tg://resolve?domain=anarhisssttt" class="contact-link">@anarhisssttt</a>
            </p>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'HomeView',
  };
  </script>
  
  <style scoped>
  
  .home-container {
    padding: 20px;
  }
  
  .main-title {
    font-size: 36px;
    font-weight: bold;
    color: #333;
    font-family: 'Didot', serif;
    margin-bottom: 40px;
  }
  
  .about-us {
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    padding: 20px;
    font-family: 'Didot', serif;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
  }
  

  
  .contact-info {
    padding: 10px;
  }
  
  .contact-text {
    font-size: 18px;
    color: #333;
    font-family: 'Didot', serif;
  
    margin-bottom: 10px;
  }
  
  .contact-link {
    color: black;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s ease;
  }
  
  .contact-link:hover {
    color: #818181;
  }
  </style>
  