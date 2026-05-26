<template>
  <div :style="cssVars">
    <!-- Floating launcher button -->
    <div v-if="!open" class="zb-launcher" :class="posClass"
         :style="{ background: cfg.primaryColor }" @click="toggle">
      <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
    </div>

    <!-- Chat panel -->
    <div v-if="open" class="zb-panel" :class="posClass">
      <div class="zb-header" :style="{ background: cfg.primaryColor }">
        <div class="zb-avatar">
          <img v-if="cfg.botAvatar" :src="cfg.botAvatar" alt=""/>
          <span v-else>{{ initial }}</span>
        </div>
        <div class="zb-title-wrap">
          <div class="zb-title">{{ cfg.botName || 'Assistant' }}</div>
          <div class="zb-subtitle">
            <span class="zb-status-dot"></span>
            Online
          </div>
        </div>
        <div class="zb-close" @click="toggle">✕</div>
      </div>

      <div class="zb-body" ref="bodyRef">
        <div v-for="(m, i) in messages" :key="i" class="zb-msg" :class="m.role">
          <div class="zb-msg-text">{{ m.content }}</div>
          <div class="zb-meta">
            <span>{{ m.at || '' }}</span>
            <span v-if="m.role === 'user'" class="zb-ticks">✓✓</span>
          </div>
        </div>
        <div v-if="loading" class="zb-msg bot">
          <span class="zb-typing"><span></span><span></span><span></span></span>
        </div>
      </div>

      <div v-if="error" class="zb-err">{{ error }}</div>

      <div v-if="cfg.showContact && (cfg.contactEmail || cfg.contactPhone)" class="zb-contact">
        Reach us:
        <a v-if="cfg.contactEmail" :href="`mailto:${cfg.contactEmail}`">{{ cfg.contactEmail }}</a>
        <span v-if="cfg.contactEmail && cfg.contactPhone"> · </span>
        <a v-if="cfg.contactPhone" :href="`tel:${cfg.contactPhone}`">{{ cfg.contactPhone }}</a>
      </div>

      <!-- Lead form -->
      <div v-if="needsLead" class="zb-form">
        <h4>{{ cfg.leadFormTitle || 'Please share your details:' }}</h4>
        <input v-if="cfg.fields?.name !== false" v-model="lead.name" class="zb-input" placeholder="Your name" />
        <input v-if="cfg.fields?.email !== false" v-model="lead.email" class="zb-input" placeholder="Email" type="email" />
        <input v-if="cfg.fields?.phone !== false" v-model="lead.phone" class="zb-input" placeholder="Phone" />
        <button class="zb-btn" :style="{ background: cfg.primaryColor }"
                :disabled="!leadValid || submitting" @click="submitLead">
          {{ submitting ? 'Saving…' : 'Start chat' }}
        </button>
      </div>

      <!-- Message input -->
      <div v-else class="zb-input-bar">
        <input v-model="draft" :disabled="loading" @keydown.enter="send"
               :placeholder="loading ? 'Thinking…' : 'Type your message…'" />
        <button :style="{ background: cfg.primaryColor }"
                :disabled="!draft.trim() || loading" @click="send">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';

const props = defineProps({
  apiBase: { type: String, required: true },
  siteId: { type: String, required: true },
});

const open = ref(false);
const loading = ref(false);
const submitting = ref(false);
const error = ref('');
const draft = ref('');
const cfg = reactive({});
const messages = ref([]);
const conversationId = ref(null);
const leadId = ref(localStorage.getItem('zenbot_lead_' + props.siteId) || null);
const lead = reactive({ name: '', email: '', phone: '' });
const bodyRef = ref(null);

const initial = computed(() => (cfg.botName || 'A').charAt(0).toUpperCase());
const posClass = computed(() => cfg.position === 'bottom-left' ? 'zb-pos-bl' : 'zb-pos-br');
const cssVars = computed(() => ({ '--zb-primary': cfg.primaryColor || '#00A884' }));
const needsLead = computed(() => cfg.requireLead !== false && !leadId.value);
const leadValid = computed(() => {
  const f = cfg.fields || {};
  if (f.name !== false && !lead.name.trim()) return false;
  if (f.email !== false && !/^\S+@\S+\.\S+$/.test(lead.email)) return false;
  if (f.phone !== false && lead.phone.trim().length < 6) return false;
  return true;
});

function nowTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function api(path, opts = {}) {
  const r = await fetch(props.apiBase + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}

async function loadConfig() {
  try {
    const data = await api(`/api/widget/config/${props.siteId}`);
    Object.assign(cfg, {
      welcomeMessage: 'Hello!',
      primaryColor: '#00A884',
      botName: 'Assistant',
      position: 'bottom-right',
      requireLead: true,
      fields: { name: true, email: true, phone: true },
    }, data.config || {});
    cfg.siteName = data.name;
  } catch (e) {
    error.value = 'Could not load chat config';
  }
}

function toggle() {
  open.value = !open.value;
  if (open.value && messages.value.length === 0 && cfg.welcomeMessage) {
    messages.value.push({ role: 'bot', content: cfg.welcomeMessage, at: nowTime() });
  }
}

async function submitLead() {
  submitting.value = true;
  error.value = '';
  try {
    const data = await api('/api/widget/lead', {
      method: 'POST',
      body: JSON.stringify({
        site_id: props.siteId,
        name: lead.name, email: lead.email, phone: lead.phone,
        page_url: location.href,
      }),
    });
    leadId.value = data.id;
    localStorage.setItem('zenbot_lead_' + props.siteId, data.id);
    messages.value.push({
      role: 'bot',
      content: `Thanks ${lead.name || ''}! How can I help you today?`,
      at: nowTime(),
    });
    scrollDown();
  } catch (e) {
    error.value = 'Could not save your details. Try again.';
  } finally {
    submitting.value = false;
  }
}

function scrollDown() {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight;
  });
}

function pageText() {
  // grab visible text from the host page (limited length)
  try {
    return (document.body?.innerText || '').slice(0, 4000);
  } catch { return ''; }
}

async function send() {
  const text = draft.value.trim();
  if (!text || loading.value) return;
  draft.value = '';
  messages.value.push({ role: 'user', content: text, at: nowTime() });
  scrollDown();
  loading.value = true;
  error.value = '';
  try {
    const data = await api('/api/widget/chat', {
      method: 'POST',
      body: JSON.stringify({
        site_id: props.siteId,
        conversation_id: conversationId.value,
        lead_id: leadId.value,
        message: text,
        page_url: location.href,
        page_title: document.title,
        page_text: pageText(),
      }),
    });
    conversationId.value = data.conversation_id;
    messages.value.push({ role: 'bot', content: data.reply, at: nowTime() });
    scrollDown();
  } catch (e) {
    error.value = 'Sorry, the assistant is unavailable right now.';
  } finally {
    loading.value = false;
  }
}

watch(messages, scrollDown, { deep: true });
onMounted(loadConfig);
</script>
