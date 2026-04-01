"""
config.py — centralised settings via pydantic-settings
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FAISS_INDEX_PATH: str = "data/faiss.index"
    METADATA_PATH: str = "data/metadata.json"
    BM25_INDEX_PATH: str = "data/bm25.pkl"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    CACHE_SIZE: int = 512

    class Config:
        env_file = ".env"


settings = Settings()
