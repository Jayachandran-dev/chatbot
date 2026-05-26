<template>
  <v-app-bar color="primary" density="comfortable">
    <v-app-bar-title>
      <v-icon class="mr-2">mdi-robot-happy</v-icon>Zenbot Admin
    </v-app-bar-title>
    <v-spacer />
    <v-btn variant="text" to="/sites" prepend-icon="mdi-web">Sites</v-btn>
    <v-btn variant="text" @click="logout" prepend-icon="mdi-logout">Logout</v-btn>
  </v-app-bar>
  <v-main class="bg-grey-lighten-4">
    <v-container fluid class="pa-6">
      <router-view />
    </v-container>
  </v-main>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
function logout() {
  localStorage.removeItem('zb_token');
  router.push('/login');
}
</script>
