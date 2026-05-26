<template>
  <v-main class="bg-grey-lighten-4">
    <v-container class="d-flex align-center justify-center" style="min-height:100vh">
      <v-card width="400" class="pa-6" elevation="4">
        <div class="text-center mb-4">
          <v-icon size="48" color="primary">mdi-robot-happy</v-icon>
          <h2 class="mt-2">Zenbot Admin</h2>
        </div>
        <v-form @submit.prevent="login">
          <v-text-field v-model="username" label="Username" prepend-inner-icon="mdi-account" />
          <v-text-field v-model="password" label="Password" type="password" prepend-inner-icon="mdi-lock" />
          <v-alert v-if="error" type="error" density="compact" class="mb-3">{{ error }}</v-alert>
          <v-btn type="submit" block color="primary" :loading="loading">Sign in</v-btn>
        </v-form>
        <v-alert type="info" density="compact" variant="tonal" class="mt-4">
          Default: <strong>admin</strong> / <strong>admin</strong>
        </v-alert>
      </v-card>
    </v-container>
  </v-main>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const username = ref('admin');
const password = ref('admin');
const error = ref('');
const loading = ref(false);
const router = useRouter();

async function login() {
  loading.value = true; error.value = '';
  try {
    const { data } = await api.post('/api/auth/login', {
      username: username.value, password: password.value,
    });
    localStorage.setItem('zb_token', data.access_token);
    router.push('/sites');
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed';
  } finally { loading.value = false; }
}
</script>
