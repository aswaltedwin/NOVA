import os
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from crewai import LLM

# NOVA Phase 2: Agentic & RAG-Enabled Configuration
class Config:
    # Model Settings
    MODEL_NAME = "ollama/qwen2.5:14b"
    BASE_URL = "http://localhost:11434"
    
    # RAG Settings
    CHROMA_PERSIST_DIR = os.path.join(os.getcwd(), ".nova_knowledge")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Local-only sentence embeddings
    
    # Memory Settings
    MEMORY_STORE_PATH = os.path.join(os.getcwd(), ".nova_memory")
    
    # Dashboard Settings
    DEBUG_MODE = True
    VERBOSE_LEVEL = 2

    @classmethod
    def get_llm(cls, model_name=None):
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
        """Returns a local embedder to ensure 100% offline memory without OpenAI."""
        return {
            "provider": "huggingface",
            "config": {
                "model": cls.EMBEDDING_MODEL,
                # Force local-only
            }
        }

# Initialize global LLM
llm = Config.get_llm()
