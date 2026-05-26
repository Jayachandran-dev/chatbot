"""FastAPI entrypoint."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import settings
from .seed import init_db
from .routers import auth as auth_router
from .routers import sites as sites_router
from .routers import knowledge as knowledge_router
from .routers import leads as leads_router
from .routers import widget as widget_router


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title=settings.APP_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,   # widget runs on third-party sites
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router)
    app.include_router(sites_router.router)
    app.include_router(knowledge_router.router)
    app.include_router(leads_router.router)
    app.include_router(widget_router.router)

    # Serve embeddable widget bundle (the built JS file)
    widget_dist = Path(__file__).resolve().parent.parent / "static" / "widget"
    widget_dist.mkdir(parents=True, exist_ok=True)
    app.mount("/widget", StaticFiles(directory=str(widget_dist)), name="widget")

    # Loader endpoint: `<script src="/zenbot.js?site=xxx"></script>`
    @app.get("/zenbot.js")
    def loader(site: str = "", request: Request = None):
        # Tiny bootstrap that injects the real widget bundle and passes site id
        base = str(request.base_url).rstrip("/") if request else ""
        js = f"""
(function() {{
  if (window.__ZenbotLoaded) return; window.__ZenbotLoaded = true;
  window.ZENBOT_CONFIG = {{ apiBase: "{base}", siteId: "{site}" }};
  var s = document.createElement('script');
  s.src = "{base}/widget/zenbot.iife.js";
  s.async = true;
  document.head.appendChild(s);
}})();
""".strip()
        return Response(content=js, media_type="application/javascript")

    @app.get("/")
    def root():
        return {"app": settings.APP_NAME, "status": "ok"}

    return app


app = create_app()
