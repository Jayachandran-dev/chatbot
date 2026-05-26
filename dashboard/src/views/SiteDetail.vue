<template>
  <div v-if="site">
    <div class="d-flex align-center mb-4">
      <v-btn icon="mdi-arrow-left" variant="text" to="/sites" />
      <div class="ml-2">
        <h2>{{ site.name }}</h2>
        <div class="text-grey">{{ site.domain }}</div>
      </div>
    </div>

    <v-tabs v-model="tab" color="primary" class="mb-4">
      <v-tab value="embed"><v-icon start>mdi-code-tags</v-icon>Install</v-tab>
      <v-tab value="config"><v-icon start>mdi-palette</v-icon>Configure</v-tab>
      <v-tab value="knowledge"><v-icon start>mdi-book-open-variant</v-icon>Knowledge</v-tab>
      <v-tab value="leads"><v-icon start>mdi-account-multiple</v-icon>Leads</v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <!-- INSTALL -->
      <v-window-item value="embed">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <h3>Inline script tag</h3>
            <v-tooltip location="right" max-width="350">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
              </template>
              Add this script tag to your website's HTML source code. It loads the chatbot widget automatically when the page opens. Best for permanent installation.
            </v-tooltip>
          </div>
          <p class="text-body-2 text-grey">Paste this just before <code>&lt;/body&gt;</code> in your website's HTML.</p>
          <v-textarea readonly :model-value="inlineSnippet" rows="2" variant="outlined" class="mt-2" />
          <v-btn size="small" variant="tonal" @click="copy(inlineSnippet)">Copy</v-btn>

          <v-divider class="my-6" />
          <div class="d-flex align-center">
            <h3>Browser console injection</h3>
            <v-tooltip location="right" max-width="350">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
              </template>
              Test the chatbot on any website without editing its code. Open the browser console (F12 → Console), paste this snippet, and press Enter. The chatbot appears instantly — great for demos.
            </v-tooltip>
          </div>
          <p class="text-body-2 text-grey">Open the target site, press F12 → Console, paste this and hit Enter to try the bot live without touching any code.</p>
          <v-textarea readonly :model-value="consoleSnippet" rows="4" variant="outlined" class="mt-2" />
          <v-btn size="small" variant="tonal" @click="copy(consoleSnippet)">Copy</v-btn>

          <v-divider class="my-6" />
          <div class="d-flex align-center">
            <h3>LLM status</h3>
            <v-tooltip location="right" max-width="350">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
              </template>
              Shows whether the local AI model is loaded and ready. If "model_present" is false, the model (~400 MB) will auto-download on the first chat. Until then, the bot uses extractive answers from your knowledge base.
            </v-tooltip>
          </div>
          <pre class="bg-grey-lighten-3 pa-3 rounded">{{ health }}</pre>
        </v-card>
      </v-window-item>

      <!-- CONFIG with preview -->
      <v-window-item value="config">
        <v-row>
          <v-col cols="12" md="7">
            <v-card class="pa-4">
              <div class="d-flex align-center mb-3">
                <h3>Appearance & messages</h3>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  Customize how the chatbot looks and what it says. Changes are reflected in the live preview on the right. The primary color applies to the chat header, buttons, and launcher icon.
                </v-tooltip>
              </div>
              <v-text-field v-model="cfg.botName" label="Bot name" />
              <v-textarea v-model="cfg.welcomeMessage" label="Start conversation message" rows="2" />
              <v-textarea v-model="cfg.leadFormTitle" label="Lead form title" rows="1" />
              <v-textarea v-model="cfg.fallbackMessage" label="Fallback message (when no answer found)" rows="2" />

              <div class="d-flex gap-2 align-center">
                <label class="mr-2">Primary color</label>
                <input type="color" v-model="cfg.primaryColor" />
                <span class="ml-2">{{ cfg.primaryColor }}</span>
              </div>

              <v-select v-model="cfg.position" :items="['bottom-right','bottom-left']" label="Position" class="mt-3" />
              <v-text-field v-model="cfg.botAvatar" label="Avatar URL (optional)" />

              <v-divider class="my-4" />
              <div class="d-flex align-center mb-3">
                <h3>Lead capture</h3>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  When enabled, visitors must provide their contact details before chatting. Their info and full conversation history are stored under the Leads tab for follow-up.
                </v-tooltip>
              </div>
              <v-switch v-model="cfg.requireLead" label="Require lead details before chat" color="primary" />
              <div class="d-flex gap-4">
                <v-checkbox v-model="cfg.fields.name" label="Name" />
                <v-checkbox v-model="cfg.fields.email" label="Email" />
                <v-checkbox v-model="cfg.fields.phone" label="Phone" />
              </div>

              <v-divider class="my-4" />
              <div class="d-flex align-center mb-3">
                <h3>Contact info (optional)</h3>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  If the bot can't answer a question, it can suggest contacting your team. Enable this and provide an email/phone so visitors know how to reach you.
                </v-tooltip>
              </div>
              <v-switch v-model="cfg.showContact" label="Show contact details in chat" color="primary" />
              <v-text-field v-model="cfg.contactEmail" label="Contact email" />
              <v-text-field v-model="cfg.contactPhone" label="Contact phone" />

              <v-btn color="primary" class="mt-4" :loading="saving" @click="saveCfg">Save changes</v-btn>
              <v-alert v-if="saved" type="success" density="compact" class="mt-3">Saved.</v-alert>
            </v-card>
          </v-col>

          <v-col cols="12" md="5">
            <v-card class="pa-4" color="grey-lighten-4">
              <h3 class="mb-3">Live preview</h3>
              <div class="preview-frame">
                <ChatPreview :config="cfg" />
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- KNOWLEDGE -->
      <v-window-item value="knowledge">
        <v-row>
          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <div class="d-flex align-center">
                <h3>Documents</h3>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  Upload files (PDF, DOCX, TXT, MD) containing information you want the chatbot to know — company brochures, product manuals, policies, etc. The content is split into chunks, embedded, and stored for retrieval.
                </v-tooltip>
              </div>
              <v-file-input v-model="upload" label="Upload PDF/DOCX/TXT/MD" prepend-icon="mdi-upload" />
              <v-btn color="primary" :disabled="!upload" :loading="uploading" @click="uploadFile">Upload</v-btn>

              <v-divider class="my-4" />
              <div class="d-flex align-center">
                <h4>Add website URL</h4>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  Fetch and ingest content from a web page. Enter a URL to ingest a single page, or enable "Crawl entire site" to automatically follow all links within the same domain and ingest multiple pages at once.
                </v-tooltip>
              </div>
              <v-text-field v-model="urlForm.url" label="https://example.com" />
              <v-checkbox v-model="urlForm.crawl" label="Crawl entire site (same domain)" />
              <v-text-field v-if="urlForm.crawl" v-model.number="urlForm.max_pages" label="Max pages" type="number" />
              <v-btn color="primary" :loading="urling" @click="ingestUrl">Ingest URL</v-btn>

              <v-divider class="my-4" />
              <h4>Existing</h4>
              <v-list density="compact">
                <v-list-item v-for="d in docs" :key="d.id">
                  <template v-slot:prepend>
                    <v-icon>{{ d.source_type === 'url' ? 'mdi-web' : 'mdi-file-document' }}</v-icon>
                  </template>
                  <v-list-item-title>{{ d.title || d.source }}</v-list-item-title>
                  <v-list-item-subtitle>{{ d.chunk_count }} chunks · {{ d.source }}</v-list-item-subtitle>
                  <template v-slot:append>
                    <v-btn icon="mdi-delete" variant="text" size="small" @click="delDoc(d.id)" />
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">
            <v-card class="pa-4">
              <div class="d-flex align-center">
                <h3>FAQs</h3>
                <v-tooltip location="right" max-width="350">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
                  </template>
                  Add common questions and their ideal answers. FAQs get the highest priority when a visitor asks a matching question, ensuring precise and consistent responses.
                </v-tooltip>
              </div>
              <v-text-field v-model="faqForm.question" label="Question" />
              <v-textarea v-model="faqForm.answer" label="Answer" rows="3" />
              <v-btn color="primary" :disabled="!faqForm.question" :loading="faqing" @click="addFaq">Add FAQ</v-btn>

              <v-divider class="my-4" />
              <v-expansion-panels>
                <v-expansion-panel v-for="f in faqs" :key="f.id">
                  <v-expansion-panel-title>{{ f.question }}</v-expansion-panel-title>
                  <v-expansion-panel-text>
                    {{ f.answer }}
                    <div class="text-right">
                      <v-btn size="small" color="error" variant="text" @click="delFaq(f.id)">Delete</v-btn>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- LEADS -->
      <v-window-item value="leads">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <h3>Leads ({{ leads.length }})</h3>
            <v-tooltip location="right" max-width="350">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" size="small" class="ml-2" color="grey">mdi-information-outline</v-icon>
              </template>
              All visitors who submitted their contact details through the chatbot. Click on a lead to view their full conversation history — useful for follow-up and understanding what customers are asking.
            </v-tooltip>
          </div>
          <v-data-table
            :headers="leadHeaders"
            :items="leads"
            density="comfortable"
            class="mt-3"
            @click:row="(_, { item }) => openLead(item)"
          />
        </v-card>

        <v-dialog v-model="leadDlg" max-width="700">
          <v-card v-if="selectedLead">
            <v-card-title>{{ selectedLead.name || 'Anonymous' }}</v-card-title>
            <v-card-subtitle>
              {{ selectedLead.email }} · {{ selectedLead.phone }}
            </v-card-subtitle>
            <v-card-text>
              <div class="text-caption mb-2">Page: {{ selectedLead.page_url }}</div>
              <v-divider class="mb-3" />
              <h4>Conversations</h4>
              <div v-for="c in leadConvs" :key="c.id" class="mb-3">
                <div class="text-caption text-grey">{{ new Date(c.started_at).toLocaleString() }}</div>
                <div v-for="(m,i) in c.messages" :key="i" class="pa-2 my-1 rounded"
                     :class="m.role === 'user' ? 'bg-primary text-white' : 'bg-grey-lighten-3'">
                  <strong>{{ m.role }}:</strong> {{ m.content }}
                </div>
              </div>
              <v-alert v-if="!leadConvs.length" type="info" variant="tonal">No conversations yet.</v-alert>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import api from '../api';
import ChatPreview from '../components/ChatPreview.vue';

const props = defineProps({ id: String });
const tab = ref('embed');
const site = ref(null);
const cfg = reactive({ fields: { name: true, email: true, phone: true } });
const saving = ref(false);
const saved = ref(false);
const health = ref(null);

const docs = ref([]);
const faqs = ref([]);
const upload = ref(null);
const uploading = ref(false);
const urlForm = reactive({ url: '', crawl: false, max_pages: 10 });
const urling = ref(false);
const faqForm = reactive({ question: '', answer: '' });
const faqing = ref(false);

const leads = ref([]);
const leadHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Phone', key: 'phone' },
  { title: 'Page', key: 'page_url' },
  { title: 'Created', key: 'created_at' },
];
const leadDlg = ref(false);
const selectedLead = ref(null);
const leadConvs = ref([]);

const apiBase = computed(() => window.location.origin.replace(':5173', ':8000'));
const inlineSnippet = computed(() =>
  `<script src="${apiBase.value}/zenbot.js?site=${props.id}"><\/script>`);
const consoleSnippet = computed(() =>
  `(function(){var s=document.createElement('script');s.src='${apiBase.value}/zenbot.js?site=${props.id}';document.body.appendChild(s);})();`);

async function loadSite() {
  const { data } = await api.get(`/api/sites/${props.id}`);
  site.value = data;
  Object.assign(cfg, { fields: { name: true, email: true, phone: true } }, data.config || {});
  if (!cfg.fields) cfg.fields = { name: true, email: true, phone: true };
}
async function loadKnowledge() {
  const [d, f] = await Promise.all([
    api.get(`/api/sites/${props.id}/documents`),
    api.get(`/api/sites/${props.id}/faqs`),
  ]);
  docs.value = d.data; faqs.value = f.data;
}
async function loadLeads() {
  const { data } = await api.get(`/api/sites/${props.id}/leads`);
  leads.value = data;
}
async function loadHealth() {
  try { health.value = (await api.get('/api/widget/health')).data; } catch {}
}

async function saveCfg() {
  saving.value = true; saved.value = false;
  try {
    await api.put(`/api/sites/${props.id}/config`, { config: cfg });
    saved.value = true;
    setTimeout(() => saved.value = false, 2000);
  } finally { saving.value = false; }
}

async function uploadFile() {
  if (!upload.value) return;
  uploading.value = true;
  try {
    const file = Array.isArray(upload.value) ? upload.value[0] : upload.value;
    const fd = new FormData(); fd.append('file', file);
    await api.post(`/api/sites/${props.id}/documents/upload`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    upload.value = null;
    await loadKnowledge();
  } finally { uploading.value = false; }
}
async function ingestUrl() {
  if (!urlForm.url) return;
  urling.value = true;
  try {
    await api.post(`/api/sites/${props.id}/documents/url`, urlForm);
    urlForm.url = '';
    await loadKnowledge();
  } finally { urling.value = false; }
}
async function delDoc(id) {
  await api.delete(`/api/sites/${props.id}/documents/${id}`);
  await loadKnowledge();
}
async function addFaq() {
  faqing.value = true;
  try {
    await api.post(`/api/sites/${props.id}/faqs`, faqForm);
    faqForm.question = ''; faqForm.answer = '';
    await loadKnowledge();
  } finally { faqing.value = false; }
}
async function delFaq(id) {
  await api.delete(`/api/sites/${props.id}/faqs/${id}`);
  await loadKnowledge();
}
async function openLead(lead) {
  selectedLead.value = lead;
  leadDlg.value = true;
  const { data } = await api.get(`/api/sites/${props.id}/leads/${lead.id}/conversations`);
  leadConvs.value = data;
}
function copy(t) { navigator.clipboard?.writeText(t); }

onMounted(async () => {
  await loadSite();
  await Promise.all([loadKnowledge(), loadLeads(), loadHealth()]);
});

watch(tab, (t) => {
  if (t === 'leads') loadLeads();
  if (t === 'knowledge') loadKnowledge();
});
</script>

<style scoped>
.preview-frame {
  position: relative; height: 600px;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3f4f6 100%);
  border-radius: 8px; overflow: hidden;
}
</style>
