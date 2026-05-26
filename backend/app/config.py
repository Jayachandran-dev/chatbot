"""Application configuration."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Zenbot"
    SECRET_KEY: str = "change-me-in-production-please-its-just-for-demo"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
    DB_URL: str = ""  # filled in __init__
    CHROMA_DIR: str = ""
    MODELS_DIR: str = ""

    # RAG
    EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 4

    # LLM (llama.cpp). Will auto-download if model file missing.
    LLM_ENABLED: bool = True
    LLM_MODEL_URL: str = (
        "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/"
        "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    )
    LLM_MODEL_FILE: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
    LLM_CTX: int = 2048
    LLM_MAX_TOKENS: int = 300

    # Default admin
    ADMIN_USER: str = "admin"
    ADMIN_PASSWORD: str = "admin"

    # CORS – widget must work from any domain
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.DB_URL:
            self.DB_URL = f"sqlite:///{self.DATA_DIR / 'zenbot.db'}"
        if not self.CHROMA_DIR:
            self.CHROMA_DIR = str(self.DATA_DIR / "chroma")
        if not self.MODELS_DIR:
            self.MODELS_DIR = str(self.DATA_DIR / "models")
        Path(self.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.MODELS_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
