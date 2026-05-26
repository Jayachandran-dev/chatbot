// Entry — mounts the chat widget inside an isolated Shadow DOM
// so host page styles never bleed in or out.
import { createApp } from 'vue';
import ChatWidget from './ChatWidget.vue';
import styles from './widget.css?inline';

function getConfig() {
  return window.ZENBOT_CONFIG || {};
}

function mount() {
  const cfg = getConfig();
  if (!cfg.siteId) {
    console.warn('[Zenbot] missing siteId — set window.ZENBOT_CONFIG.siteId');
    return;
  }

  // host element + shadow root
  const host = document.createElement('div');
  host.id = 'zenbot-host';
  host.style.all = 'initial';
  document.body.appendChild(host);

  const shadow = host.attachShadow({ mode: 'open' });
  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  const mountEl = document.createElement('div');
  shadow.appendChild(styleEl);
  shadow.appendChild(mountEl);

  const app = createApp(ChatWidget, {
    apiBase: cfg.apiBase || '',
    siteId: cfg.siteId,
  });
  app.mount(mountEl);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mount, { once: true });
} else {
  mount();
}

// Expose a manual mount fn for the "console injection" use case
window.Zenbot = { mount };
