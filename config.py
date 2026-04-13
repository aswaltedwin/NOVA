from langchain_ollama import ChatOllama
from crewai import LLM

# NOVA Configuration - 100% Local Multi-Model Support
class Config:
    MODEL_NAME = "ollama/qwen2.5:14b"
    BASE_URL = "http://localhost:11434"
    
    # Primary LLM interface using the modern CrewAI LLM class
    @classmethod
    def get_llm(cls, model_name=None):
        target_model = model_name or cls.MODEL_NAME
        # Prefix with ollama/ if not already present for CrewAI compatibility
        if not target_model.startswith("ollama/"):
            target_model = f"ollama/{target_model}"
            
        return LLM(
            model=target_model,
            base_url=cls.BASE_URL,
            temperature=0.3
        )

# Direct instance for simple imports
llm = Config.get_llm()
