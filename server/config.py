# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "TruthPulse"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    vectorstore_path: str = "data/vectorstore"
    faiss_index_path: str = "data/faiss/index.faiss"
    faiss_pk_path: str = "data/faiss/docstore.pkl"
    data_path: str = "data"
    rss_sources_path: str = "data/rss_sources.yaml"
    
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    bcrypt_rounds: int = 12
    allowed_origins: str = "*"
    
    rss_fetch_timeout: int = 15
    rss_max_headlines_per_feed: int = 15
    rss_cache_ttl: int = 3600  # 1 hour
    
    # API Keys
    google_fact_check_api_key: str
    groq_api_key: str  # ← NEW: Required for Groq-powered final verdict

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Create settings instance
settings = Settings()

# Export all config values for easy import across the app
APP_NAME = settings.app_name
APP_VERSION = settings.app_version
DEBUG = settings.debug
ENVIRONMENT = settings.environment
HOST = settings.host
PORT = settings.port
RELOAD = settings.reload
ALLOWED_ORIGINS = settings.allowed_origins.split(",") if settings.allowed_origins else []

VECTORSTORE_PATH = settings.vectorstore_path
FAISS_INDEX_PATH = settings.faiss_index_path
FAISS_PK_PATH = settings.faiss_pk_path
DATA_PATH = settings.data_path
RSS_SOURCES_PATH = settings.rss_sources_path

EMBEDDING_MODEL_NAME = settings.embedding_model_name
EMBEDDING_DIM = settings.embedding_dim

JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

BCRYPT_ROUNDS = settings.bcrypt_rounds

RSS_FETCH_TIMEOUT = settings.rss_fetch_timeout
RSS_MAX_HEADLINES_PER_FEED = settings.rss_max_headlines_per_feed
RSS_CACHE_TTL = settings.rss_cache_ttl

# API Keys (now safely imported everywhere)
GOOGLE_FACT_CHECK_API_KEY = settings.google_fact_check_api_key
GROQ_API_KEY = settings.groq_api_key  # ← This is what your VerifierAgent needs!