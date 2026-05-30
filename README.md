# Zenbot — Embeddable AI Chatbot Platform

A self-hosted, multi-tenant AI chatbot platform you can embed on **any website**
(Zenfuture Technologies and beyond). 100% local — **no OpenAI / external APIs**.

- **Backend** — FastAPI + SQLite + ChromaDB + sentence-transformers + llama.cpp
- **Widget** — Vue 3 in Shadow DOM (paste a `<script>` or inject from console)
- **Dashboard** — Vue 3 + Vuetify (login, sites, knowledge base, leads, config + live preview)

## What it does

1. Admin registers a **website by domain** in the dashboard.
2. Admin uploads documents (PDF/DOCX/TXT/MD), adds website URLs to crawl, and FAQs.
3. The system embeds everything locally with `all-MiniLM-L6-v2` into ChromaDB
   (scoped per site).
4. End-users on the website see a chat launcher. The widget first collects
   **name / email / phone**, then chats.
5. Each question is answered by a **local LLM (Qwen2.5-0.5B-Instruct, GGUF)**
   grounded in retrieved chunks **plus** the visible text of the page they are on.
   If the model is not present, the bot falls back to high-quality extractive answers
   from the retrieved chunks.
6. Leads + full conversation history are stored and visible in the dashboard for
   follow-up.

## Run with Docker (recommended)

```bash
# 1. Build & start
docker compose up --build

# 2. Open:
#    Dashboard: http://localhost:5173
#    Backend:   http://localhost:8000
# Login: admin / admin
```

A seeded site **Zenfuture Technologies** is created automatically. Open it →
go to **Install** → copy the snippet.

## Deploy to production (HTTPS)

This repository includes a production stack with automatic HTTPS via Caddy.

### 1. Prepare server

- Install Docker Engine + Docker Compose plugin.
- Open inbound ports: **80** and **443** in your VM/firewall.
- Point your domain DNS A record to the server IP.

### 2. Configure environment

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and set at least:

- `DOMAIN` (example: `chat.yourdomain.com`)
- `SECRET_KEY` (long random string)
- `ADMIN_PASSWORD` (strong password)

### 3. Start production stack

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

### 4. Verify

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f caddy
```

Open:

- `https://<your-domain>` for dashboard
- `https://<your-domain>/api/widget/health` for backend health

### 5. Embed widget on any website

Use your production domain in snippet:

```html
<script src="https://<your-domain>/zenbot.js?site=YOUR_SITE_ID"></script>
```

### 6. Update deployment

```bash
git pull
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

## Run locally (dev)

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# (Optional) enable local LLM:
# On Windows, use a compatible Python version and install Visual Studio Build Tools
# with C++ and NMake before installing llama-cpp-python.
# If you don't want the local model, skip this line; the app will still run with
# extractive fallback answers.
pip install llama-cpp-python==0.3.1
# IMPORTANT on Windows / OneDrive: limit reload to app/ so .venv changes
# don't cause uvicorn to restart in the middle of a request.
uvicorn app.main:app --reload --reload-dir app

# Widget (build once, then served by backend at /widget/zenbot.iife.js)
cd ..\widget
npm install
npm run build

# Dashboard
cd ..\dashboard
npm install
npm run dev   # http://localhost:5173 (proxies /api -> :8000)
```

## Embed on any website — two ways

**1. Inline script tag** (paste before `</body>`):
```html
<script src="http://your-server:8000/zenbot.js?site=YOUR_SITE_ID"></script>
```

**2. Browser console injection** (try it live without editing the site):
```js
(function(){var s=document.createElement('script');
 s.src='http://your-server:8000/zenbot.js?site=YOUR_SITE_ID';
 document.body.appendChild(s);})();
```

The widget mounts inside a **Shadow DOM**, so it never collides with host CSS.

## How the bot stays accurate

- Retrieval is **strictly per-site** (`site_id` scoped Chroma collection).
- The prompt forces grounding: *"Answer ONLY from the provided context. If not
  present, say you don't know and offer to connect with the team."*
- The widget sends the **current page's visible text** as additional context, so
  the bot can answer page-specific questions out of the box.
- Temperature is low (0.2). The fallback message is admin-configurable.
- If the LLM is unavailable, an **extractive answer** is returned from the top
  retrieved chunk — still relevant, never hallucinated.

## Models / hardware

Default LLM: `Qwen2.5-0.5B-Instruct` (Q4_K_M GGUF, ~400 MB). Auto-downloads on
first chat. Runs on CPU with ~1.5 GB RAM. To use a larger / better model edit
`LLM_MODEL_URL` and `LLM_MODEL_FILE` in `backend/app/config.py` (or via env).

Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (~90 MB, CPU friendly).

## Project layout

```
backend/    FastAPI app, RAG pipeline, SQLite DB, ChromaDB store
widget/     Embeddable Vue 3 widget (Shadow DOM), built into backend/static/widget
dashboard/  Vue 3 + Vuetify admin
```

## API summary

Public (no auth, used by widget):
- `GET  /api/widget/config/{site_id}`
- `POST /api/widget/lead`
- `POST /api/widget/chat`
- `GET  /api/widget/health`
- `GET  /zenbot.js?site=...`  (loader)

Admin (JWT):
- `POST /api/auth/login`
- `GET/POST/DELETE /api/sites`, `PUT /api/sites/{id}/config`
- `GET/POST /api/sites/{id}/documents`, upload, url ingest, delete
- `GET/POST/DELETE /api/sites/{id}/faqs`
- `GET /api/sites/{id}/leads`, `/conversations`, `/leads/{lead_id}/conversations`

## Notes for the interview demo

- Default admin: `admin` / `admin` (change `SECRET_KEY` and credentials before production).
- The widget uses plain Vue 3 (not Vuetify) so it can live inside Shadow DOM on
  arbitrary host pages — Vuetify's global styles don't play well there. The
  **admin dashboard** uses Vuetify as requested.
- All data is local: SQLite file + Chroma persistence at `backend/data/`.
