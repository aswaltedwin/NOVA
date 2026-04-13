import os
from langchain_ollama import ChatOllama

# NOVA Configuration - 100% Local LLM via Ollama
class Config:
    # Default local models (User can update these via Ollama pull)
    MODEL_NAME = "qwen2.5:14b"
    # ALTERNATIVE: "deepseek-r1" or "llama3.3"
    
    BASE_URL = "http://localhost:11434"
    
    # Enable verbose output for every agent chain-of-thought
    VERBOSE = True
    
    # Process management: CrewAI Hierarchical requires a Manager LLM
    PROCESS = "hierarchical" # Or "sequential"

    @classmethod
    def get_llm(cls, model_name=None):
        """Returns a ChatOllama instance."""
        target_model = model_name or cls.MODEL_NAME
        return ChatOllama(
            model=target_model,
            base_url=cls.BASE_URL,
            temperature=0,
            num_ctx=8192 # Sufficient context for 15 logs
        )

# Example Usage:
# llm = Config.get_llm()
