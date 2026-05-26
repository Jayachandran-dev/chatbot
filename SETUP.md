# Zenbot — Local Setup Guide

Complete step-by-step instructions to set up and run the Zenbot AI Chatbot
Platform on **any machine** (Windows / macOS / Linux).

---

## Prerequisites

| Tool       | Version     | Check command           |
|------------|-------------|-------------------------|
| **Python** | 3.10 – 3.12 | `python --version`      |
| **Node.js**| 18+         | `node --version`        |
| **npm**    | 9+          | `npm --version`         |
| **Git**    | any         | `git --version`         |

> **Important:** Python 3.13+ may fail because ML packages (numpy, torch,
> chromadb) don't always have prebuilt wheels yet. Use **Python 3.11** for the
> smoothest experience.

### Install Python 3.11 (if needed)

**Windows:**
```powershell
winget install Python.Python.3.11
```

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3.11 python3.11-venv
```

---

## 1. Clone the project

```bash
git clone <your-repo-url> zenbot
cd zenbot
```

Or simply copy the project folder to the target machine.

---

## 2. Backend setup

```bash
cd backend
```

### 2.1 Create & activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2.2 Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, SQLAlchemy, ChromaDB, sentence-transformers, etc.
First run downloads the embedding model (`all-MiniLM-L6-v2`, ~90 MB).

> **If pip gets stuck** resolving `transformers` versions (backtracking through
> dozens of versions), run this explicit install instead:
> ```bash
> pip install fastapi "uvicorn[standard]" sqlalchemy pydantic pydantic-settings \
>   "python-jose[cryptography]" "passlib[bcrypt]" python-multipart httpx \
>   beautifulsoup4 lxml pypdf python-docx "chromadb>=0.5.13,<0.6" \
>   "sentence-transformers>=3.1,<4" "transformers>=4.41,<4.47" \
>   "huggingface-hub>=0.23,<0.27" "tokenizers>=0.19,<0.21" "numpy>=1.26,<3"
> ```

### 2.3 (Optional) Install local LLM support

For full AI-powered answers (instead of extractive fallback):

```bash
# CPU-only prebuilt wheel (recommended):
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Or with CUDA GPU acceleration:
# pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
```

The LLM model (`Qwen2.5-0.5B-Instruct`, ~400 MB GGUF) auto-downloads on the
first chat request. Without `llama-cpp-python`, the bot falls back to
extractive answers from retrieved chunks — still accurate, never hallucinated.

### 2.4 Start the backend

**Windows (OneDrive users — limit reload to app/ folder):**
```powershell
uvicorn app.main:app --reload --reload-dir app
```

**macOS / Linux:**
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

> On first startup, the backend automatically:
> - Creates a SQLite database at `backend/data/zenbot.db`
> - Seeds an **admin** user (`admin` / `admin`)
> - Seeds a demo site **"Zenfuture Technologies"** with sample knowledge & FAQs
> - Initializes ChromaDB at `backend/data/chroma/`

### 2.5 Verify backend is running

Open a **new terminal** (keep the backend running) and test:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Expected: `{"access_token":"eyJ...","token_type":"bearer"}`

---

## 3. Widget build

The widget is a Vue 3 app compiled into a single IIFE script that gets
embedded on target websites. It **must be built before use**.

```bash
cd ../widget
npm install
npm run build
```

Output: `backend/static/widget/zenbot.iife.js` (~74 KB)

> You only need to rebuild the widget when you change its source code.
> The backend serves the built file automatically.

---

## 4. Dashboard setup

```bash
cd ../dashboard
npm install
npm run dev
```

Opens at **http://localhost:5173** — login with `admin` / `admin`.

> The dashboard's Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`.
> Make sure the backend is running first.

---

## 5. Test the chatbot

### Option A: Console injection (quickest)

1. Open any website in your browser (e.g., https://zenfuture.in)
2. Open DevTools → Console (F12)
3. Paste the injection snippet from the dashboard's **Install** tab:

```js
(function(){var s=document.createElement('script');
s.src='http://localhost:8000/zenbot.js?site=YOUR_SITE_ID';
document.body.appendChild(s);})();
```

Replace `YOUR_SITE_ID` with the ID shown in the dashboard (or copy the
ready-made snippet from the Install tab).

### Option B: Inline script tag

Add this before `</body>` in your website's HTML:

```html
<script src="http://localhost:8000/zenbot.js?site=YOUR_SITE_ID"></script>
```

The chatbot launcher button appears in the bottom-right corner. It:
1. Collects visitor's **name, email, phone** (lead capture)
2. Answers questions using knowledge base + current page content
3. Stores the full conversation for follow-up in the dashboard

---

## Quick reference

| Service   | URL                          | Purpose                    |
|-----------|------------------------------|----------------------------|
| Backend   | http://127.0.0.1:8000        | API + widget serving       |
| Dashboard | http://localhost:5173         | Admin panel                |
| Health    | http://127.0.0.1:8000/api/widget/health | Check LLM status |

| Credentials | Value |
|-------------|-------|
| Admin user  | `admin` |
| Admin pass  | `admin` |

---

## Project structure

```
zenbot/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py       # App entrypoint, CORS, routes, widget loader
│   │   ├── config.py     # Settings (SECRET_KEY, model URLs, paths)
│   │   ├── models.py     # SQLAlchemy models (User, Site, Document, FAQ, Lead, etc.)
│   │   ├── seed.py       # Auto-seeds admin user + demo site on first run
│   │   ├── auth.py       # JWT auth + bcrypt password hashing
│   │   ├── db.py         # Database session management
│   │   ├── schemas.py    # Pydantic request/response schemas
│   │   ├── rag/
│   │   │   ├── embedder.py    # sentence-transformers embedding
│   │   │   ├── vectorstore.py # ChromaDB per-site vector storage
│   │   │   ├── llm.py         # llama.cpp local LLM + extractive fallback
│   │   │   └── ingest.py      # Document/URL/FAQ ingestion pipeline
│   │   └── routers/
│   │       ├── auth.py        # POST /api/auth/login, GET /api/auth/me
│   │       ├── sites.py       # CRUD for sites
│   │       ├── knowledge.py   # Document upload, URL crawl, FAQ management
│   │       ├── leads.py       # Lead listing + conversation history
│   │       └── widget.py      # Public chat/lead/config endpoints (no auth)
│   ├── requirements.txt
│   ├── data/             # Auto-created: SQLite DB + ChromaDB + downloaded models
│   └── static/widget/    # Auto-created: built widget bundle served here
├── widget/               # Vue 3 embeddable chat widget (Shadow DOM)
│   ├── src/
│   │   ├── main.js       # Shadow DOM mount + window.Zenbot.mount()
│   │   └── ChatWidget.vue # Chat UI, lead form, page-text capture
│   ├── vite.config.js    # Builds as IIFE → backend/static/widget/
│   └── package.json
├── dashboard/            # Vue 3 + Vuetify admin panel
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Sites.vue
│   │   │   └── SiteDetail.vue  # 4 tabs: Install, Configure, Knowledge, Leads
│   │   ├── components/
│   │   │   └── ChatPreview.vue # Live widget preview for config editing
│   │   ├── api.js        # Axios with JWT interceptor
│   │   ├── router.js     # Routes + auth guard
│   │   └── main.js       # Vue + Vuetify + Pinia setup
│   ├── vite.config.js    # Dev proxy /api → :8000
│   └── package.json
├── docker-compose.yml    # Optional: Docker deployment
├── README.md
└── SETUP.md              # ← You are here
```

---

## Troubleshooting

### `pip install` gets stuck / backtracks through many versions

Use the explicit install command from step 2.2 (with pinned version ranges).

### `passlib` / `bcrypt` error (`module 'bcrypt' has no attribute '__about__'`)

This project uses `bcrypt` directly (not through `passlib`). If you see this
error, make sure you're running the latest code — `auth.py` should import
`bcrypt` directly, not `passlib`.

### `ModuleNotFoundError: No module named 'fastapi'`

Your pip install was interrupted. Run `pip install -r requirements.txt` again
and **let it finish completely** (don't press Ctrl+C).

### Backend keeps restarting on Windows / OneDrive

OneDrive syncs `.venv/` files, triggering uvicorn's file watcher. Use:
```powershell
uvicorn app.main:app --reload --reload-dir app
```

### Dashboard login returns 500 (Internal Server Error)

1. Make sure the **backend is running** on port 8000 first
2. Check that no zombie process holds port 5173:
   ```powershell
   # Windows
   Get-NetTCPConnection -LocalPort 5173 | Select OwningProcess
   # Kill it if needed:
   Stop-Process -Id <PID> -Force
   ```
3. Restart the dashboard: `npm run dev`

### Vite proxy error: `ECONNREFUSED ::1:8000`

`localhost` resolves to IPv6 (`::1`) but uvicorn binds to IPv4 (`127.0.0.1`).
In `dashboard/vite.config.js`, the proxy target must be `http://127.0.0.1:8000`
(not `http://localhost:8000`). This is already set correctly in the codebase.

### Widget doesn't appear after console injection

1. Verify the widget was **built**: `ls backend/static/widget/zenbot.iife.js`
2. Verify the backend serves it: `curl http://127.0.0.1:8000/widget/zenbot.iife.js`
   should return JS content (not 404)
3. If 404, restart the backend (it needs to register the static mount)

### `process is not defined` in browser console

The widget wasn't built with production defines. Run `npm run build` in the
`widget/` folder — the vite config includes `define: { 'process.env.NODE_ENV': '"production"' }`.

### LLM model download is slow / first chat takes long

The Qwen2.5-0.5B model (~400 MB) auto-downloads on the first chat request.
During download, the chat endpoint may be slow. Subsequent requests are instant.
Check download status: `GET http://127.0.0.1:8000/api/widget/health`

---

## Configuration

Edit `backend/app/config.py` or set environment variables:

| Variable              | Default                          | Description                    |
|-----------------------|----------------------------------|--------------------------------|
| `SECRET_KEY`          | `change-me-in-production`        | JWT signing key                |
| `ADMIN_USER`          | `admin`                          | Default admin username         |
| `ADMIN_PASSWORD`      | `admin`                          | Default admin password         |
| `LLM_MODEL_URL`       | Qwen2.5-0.5B GGUF URL           | URL to download the LLM model |
| `LLM_MODEL_FILE`      | `qwen2.5-0.5b-instruct-q4_k_m.gguf` | Local model filename      |
| `CORS_ORIGINS`        | `*`                              | Allowed CORS origins           |

---

## Docker deployment (alternative)

If you have Docker installed:

```bash
docker compose up --build
```

This starts both backend (port 8000) and dashboard (port 5173) in containers.
No Python/Node installation needed on the host machine.

---

## API quick reference

**Public endpoints** (no auth, used by widget):

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | `/api/widget/config/{site_id}`  | Widget config for a site |
| POST   | `/api/widget/lead`              | Submit lead (name/email/phone) |
| POST   | `/api/widget/chat`              | Send chat message        |
| GET    | `/api/widget/health`            | LLM status check         |
| GET    | `/zenbot.js?site=ID`            | Widget loader script     |

**Admin endpoints** (JWT required):

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | `/api/auth/login`                 | Get JWT token            |
| GET    | `/api/auth/me`                    | Current user info        |
| GET    | `/api/sites`                      | List all sites           |
| POST   | `/api/sites`                      | Create a site            |
| DELETE | `/api/sites/{id}`                 | Delete a site            |
| PUT    | `/api/sites/{id}/config`          | Update site config       |
| GET    | `/api/sites/{id}/documents`       | List documents           |
| POST   | `/api/sites/{id}/documents`       | Upload document          |
| POST   | `/api/sites/{id}/documents/url`   | Ingest URL content       |
| DELETE | `/api/sites/{id}/documents/{did}` | Delete document          |
| GET    | `/api/sites/{id}/faqs`            | List FAQs                |
| POST   | `/api/sites/{id}/faqs`            | Create FAQ               |
| DELETE | `/api/sites/{id}/faqs/{fid}`      | Delete FAQ               |
| GET    | `/api/sites/{id}/leads`           | List leads               |
| GET    | `/api/sites/{id}/leads/{lid}/conversations` | Lead's chat history |
