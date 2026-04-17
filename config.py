import os
import logging
from pathlib import Path
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from crewai import LLM

# Configure logging for the entire platform
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nova_sentinel.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("NOVA-Config")

class Config:
    VERSION = "3.1.0-PRO"
    
    # Base Directories using Pathlib
    BASE_DIR = Path.cwd()
    LOGS_DIR = BASE_DIR / "logs"
    
    # Model Settings
    MODEL_NAME = "ollama/llama3.2"
    BASE_URL = "http://localhost:11434"
    
    # RAG Settings
    CHROMA_PERSIST_DIR = str(BASE_DIR / ".nova_knowledge")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Memory Settings
    MEMORY_STORE_PATH = str(BASE_DIR / ".nova_memory")
    
    # Dashboard Settings
    DEBUG_MODE = True
    VERBOSE_LEVEL = 2

    @classmethod
    def validate(cls):
        """Ensures the environment is ready for NOVA operations."""
        logger.info(f"Initializaing NOVA Sentinel {cls.VERSION}")
        # Ensure directories exist
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
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
Config.validate()
llm = Config.get_llm()
