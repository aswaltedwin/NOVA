import os
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from crewai import LLM

# NOVA Phase 2: Agentic & RAG-Enabled Configuration
class Config:
    # Model Settings
    MODEL_NAME = "ollama/llama3.2"
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
        """Returns a standardized local embedder configuration for CrewAI memory."""
        return {
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text:latest",
                "base_url": cls.BASE_URL
            }
        }

# Initialize global LLM
llm = Config.get_llm()
