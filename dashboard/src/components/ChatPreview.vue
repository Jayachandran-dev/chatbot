<template>
  <div class="preview-root">
    <!-- Launcher -->
    <div v-if="!open" class="pv-launcher" :style="launcherStyle" @click="open = true">
      <v-icon color="white">mdi-message-text</v-icon>
    </div>

    <!-- Panel -->
    <div v-else class="pv-panel" :class="posClass">
      <div class="pv-header" :style="{ background: config.primaryColor }">
        <div class="pv-avatar">{{ initial }}</div>
        <div class="flex-grow-1">{{ config.botName || 'Assistant' }}</div>
        <v-icon color="white" @click="open = false">mdi-close</v-icon>
      </div>

      <div class="pv-body">
        <div class="pv-msg bot">{{ config.welcomeMessage || 'Hello!' }}</div>
        <div class="pv-msg user" :style="{ background: config.primaryColor }">
          Hi! I'd like to know more about your services.
        </div>
        <div class="pv-msg bot">
          Sure! We offer web development, mobile apps, and AI/ML consulting.
        </div>
      </div>

      <div v-if="config.showContact && (config.contactEmail || config.contactPhone)"
           class="pv-contact">
        Reach us:
        <span v-if="config.contactEmail">{{ config.contactEmail }}</span>
        <span v-if="config.contactPhone"> · {{ config.contactPhone }}</span>
      </div>

      <div v-if="config.requireLead" class="pv-form">
        <div class="text-caption mb-2">{{ config.leadFormTitle }}</div>
        <input v-if="config.fields?.name" placeholder="Name" class="pv-input" />
        <input v-if="config.fields?.email" placeholder="Email" class="pv-input" />
        <input v-if="config.fields?.phone" placeholder="Phone" class="pv-input" />
        <button class="pv-btn" :style="{ background: config.primaryColor }">Start chat</button>
      </div>
      <div v-else class="pv-input-bar">
        <input placeholder="Type your message…" class="pv-input" style="margin:0" />
        <button class="pv-send" :style="{ background: config.primaryColor }">
          <v-icon size="18" color="white">mdi-send</v-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
const props = defineProps({ config: { type: Object, required: true } });
const open = ref(true);
const initial = computed(() => (props.config.botName || 'A').charAt(0).toUpperCase());
const posClass = computed(() => props.config.position === 'bottom-left' ? 'pv-bl' : 'pv-br');
const launcherStyle = computed(() => ({
  background: props.config.primaryColor || '#4F46E5',
  ...(props.config.position === 'bottom-left' ? { left: '12px' } : { right: '12px' }),
  bottom: '12px',
}));
</script>

<style scoped>
.preview-root { position: absolute; inset: 0; }
.pv-launcher {
  position: absolute; width: 50px; height: 50px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.pv-panel {
  position: absolute; width: 300px; height: 470px;
  background: white; border-radius: 12px; overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  display: flex; flex-direction: column; font-size: 13px;
}
.pv-br { right: 12px; bottom: 12px; }
.pv-bl { left: 12px; bottom: 12px; }
.pv-header {
  padding: 10px 12px; color: white;
  display: flex; align-items: center; gap: 8px;
}
.pv-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  font-weight: bold;
}
.pv-body { flex: 1; padding: 10px; overflow-y: auto; background: #f9fafb;
  display: flex; flex-direction: column; gap: 8px; }
.pv-msg { max-width: 80%; padding: 7px 10px; border-radius: 12px; }
.pv-msg.bot { background: white; border: 1px solid #e5e7eb; align-self: flex-start; }
.pv-msg.user { color: white; align-self: flex-end; }
.pv-form { padding: 10px; border-top: 1px solid #e5e7eb; background: white; }
.pv-input { width: 100%; padding: 6px 8px; border: 1px solid #d1d5db;
  border-radius: 6px; margin-bottom: 6px; font-size: 12px; outline: none; }
.pv-btn { width: 100%; padding: 8px; border: 0; border-radius: 6px;
  color: white; font-weight: 600; cursor: pointer; }
.pv-input-bar { display: flex; gap: 6px; padding: 8px; background: white;
  border-top: 1px solid #e5e7eb; align-items: center; }
.pv-send { width: 32px; height: 32px; border-radius: 50%; border: 0; cursor: pointer;
  display: flex; align-items: center; justify-content: center; }
.pv-contact { padding: 6px 10px; background: #f3f4f6; font-size: 11px;
  color: #6b7280; border-top: 1px solid #e5e7eb; }
</style>
