import ollama
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import logging

logger = logging.getLogger("NOVA-Vision")

class ScreenshotAnalyzerSchema(BaseModel):
    image_path: str = Field(..., description="Path to the SIEM/EDR screenshot artifact.")
    prompt: Optional[str] = Field(
        "Analyze this security dashboard screenshot. Identify all suspicious activity, IPs, usernames, and alert severities. Format findings for a security report.", 
        description="Specific analysis prompt."
    )

class ScreenshotAnalyzerTool(BaseTool):
    name: str = "Multi-Modal Screenshot Analyzer"
    description: str = "Uses Llama-3.2-Vision to extract threat intelligence from security dashboard screenshots."
    args_schema: type[BaseModel] = ScreenshotAnalyzerSchema

    def _run(self, image_path: str, prompt: Optional[str] = None) -> str:
        if not prompt:
            prompt = "Analyze this security dashboard screenshot. Identify all suspicious activity, IPs, usernames, and alert severities. Format findings for a security report."
            
        if not os.path.exists(image_path):
            error_msg = f"Error: Image artifact {image_path} not found."
            logger.error(error_msg)
            return error_msg
            
        try:
            logger.info(f"Ollama Vision: Processing {image_path}")
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path]
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Vision Analysis Failed: {e}")
            return f"Vision Analysis Failed: {str(e)}. Ensure 'llama3.2-vision' is available in Ollama."
