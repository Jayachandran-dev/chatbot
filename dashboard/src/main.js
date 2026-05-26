import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';

import App from './App.vue';
import router from './router';

const vuetify = createVuetify({
  components, directives,
  icons: { defaultSet: 'mdi', aliases, sets: { mdi } },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: { colors: { primary: '#4F46E5', secondary: '#6366F1' } },
    },
  },
});

createApp(App).use(createPinia()).use(router).use(vuetify).mount('#app');
