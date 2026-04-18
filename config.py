import os
import logging
from pathlib import Path
from typing import Optional, List
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from crewai import LLM

# Base configuration class with environment-first overrides
class Config:
    VERSION = "3.1.0-PRO"
    
    # Base Directories
    BASE_DIR = Path.cwd()
    LOGS_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    
    # Model Settings (Environment-supported)
    MODEL_NAME = os.getenv("NOVA_MODEL", "ollama/llama3.2")
    VISION_MODEL = os.getenv("NOVA_VISION_MODEL", "llama3.2-vision")
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # RAG Settings
    CHROMA_PERSIST_DIR = str(BASE_DIR / ".nova_knowledge")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Memory Settings
    MEMORY_STORE_PATH = str(BASE_DIR / ".nova_memory")
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/nova_sentinel.db")
    
    # Security
    API_KEY = os.getenv("NOVA_API_KEY", "NOVA-SENTINEL-SECURE-KEY-2026") # Default for demo
    
    # Available Models for UI
    AVAILABLE_MODELS = [
        "llama3.2", 
        "qwen2.5:7b", 
        "deepseek-r1:7b", 
        "deepseek-v3.1:671b-cloud"
    ]

    @classmethod
    def setup_logging(cls):
        """Centralized logging configuration."""
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOGS_DIR / "nova_sentinel.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("NOVA-System")

    @classmethod
    def validate(cls):
        """Ensures the environment is ready for NOVA operations."""
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        Path(cls.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        return True

    @classmethod
    def get_llm(cls, model_name: Optional[str] = None):
        target_model = model_name or cls.MODEL_NAME
        if not target_model.startswith("ollama/"):
            target_model = f"ollama/{target_model}"
            
        return LLM(
            model=target_model,
            base_url=cls.BASE_URL,
            temperature=0.3
        )

    @classmethod
    def get_embedder(cls):
        return {
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text:latest",
                "base_url": cls.BASE_URL
            }
        }

# Global initialization
logger = Config.setup_logging()
Config.validate()
llm = Config.get_llm()

