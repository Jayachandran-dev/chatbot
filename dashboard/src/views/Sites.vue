<template>
  <div>
    <div class="d-flex align-center mb-4">
      <h2>Websites</h2>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="dialog = true">Add website</v-btn>
    </div>

    <v-row>
      <v-col v-for="s in sites" :key="s.id" cols="12" md="4">
        <v-card hover @click="$router.push(`/sites/${s.id}`)">
          <v-card-title>
            <v-icon class="mr-2" color="primary">mdi-web</v-icon>{{ s.name }}
          </v-card-title>
          <v-card-subtitle>{{ s.domain }}</v-card-subtitle>
          <v-card-text>
            <v-chip size="small" color="primary" variant="tonal">
              Bot: {{ s.config?.botName || 'Assistant' }}
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col v-if="!sites.length" cols="12">
        <v-alert type="info" variant="tonal">No websites yet. Add one to get started.</v-alert>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>Add website</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Name (e.g. Zenfuture Technologies)" />
          <v-text-field v-model="form.domain" label="Domain (e.g. zenfuture.tech)" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="dialog = false">Cancel</v-btn>
          <v-btn color="primary" :loading="saving" @click="save">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const sites = ref([]);
const dialog = ref(false);
const saving = ref(false);
const form = ref({ name: '', domain: '' });

async function load() {
  const { data } = await api.get('/api/sites');
  sites.value = data;
}
async function save() {
  saving.value = true;
  try {
    await api.post('/api/sites', form.value);
    dialog.value = false;
    form.value = { name: '', domain: '' };
    await load();
  } finally { saving.value = false; }
}
onMounted(load);
</script>
