"""Configuration management"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

# Trigger AI workflow


class Settings(BaseSettings):
    """Application settings"""
    newsapi_key: str = ""
    gnews_api_key: str = ""
    
    log_level: str = "INFO"
    max_workers: int = 5
    memory_persist_dir: Path = Path("./memory_store")
    articles_dir: Path = Path("./articles")
    generated_articles_dir: Path = Path("./generated_articles")
    
    # LLM configuration
    llm_model_path: str = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    llm_enabled: bool = True  # Re-enabled with smaller model
    
    # Agent configuration (optimized for twice-daily runs within free tier)
    # 2 categories × 25 articles × 1 page = ~50 API calls per run
    # 2 runs/day = 100 API calls/day (exactly at free tier limit!)
    categories: List[str] = ["technology", "business"]  # Reduced from 4 to 2
    page_size: int = 25  # Reduced from 50 to 25
    pages_per_category: int = 1  # Reduced from 2 to 1
    similarity_threshold: int = 90
    max_retries: int = 3
    
    # Metacognitive parameters
    reflection_interval: int = 10
    confidence_threshold: float = 0.7
    learning_rate: float = 0.1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
