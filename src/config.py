"""
Configuration centrale de Saul Goodbot.
Toutes les valeurs se règlent dans le fichier .env.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "oui")


# ── LLM (Groq) ────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# ── Documents & base vectorielle ─────────────────────────────
DATA_DIR = ROOT_DIR / os.getenv("DATA_DIR", "data")
DB_DIR = ROOT_DIR / os.getenv("DB_DIR", "db_juridique")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "SaulGoodbot")

# Modèle multilingue ───────────────────────────────────────────
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ── Recherche ────────────────────────────────────────────────
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))          # extraits envoyés au LLM
RETRIEVER_FETCH_K = int(os.getenv("RETRIEVER_FETCH_K", "20"))
WEB_SEARCH_ENABLED = _bool("WEB_SEARCH_ENABLED", True)
WEB_MAX_RESULTS = int(os.getenv("WEB_MAX_RESULTS", "4"))

# ── Conversation & interface ─────────────────────────────────
HISTORY_TURNS = int(os.getenv("HISTORY_TURNS", "3"))      # échanges gardés en mémoire

