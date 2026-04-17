import ollama
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os

class ScreenshotAnalyzerSchema(BaseModel):
    image_path: str = Field(..., description="Path to the SIEM/EDR screenshot artifact.")
    prompt: str = Field("Analyze this security dashboard screenshot. Extract all alerts, IPs, timestamps, and severity levels.", description="Specific analysis prompt.")

class ScreenshotAnalyzerTool(BaseTool):
    name: str = "Multi-Modal Screenshot Analyzer"
    description: str = "Uses Llama-3.2-Vision to extract threat intelligence from security dashboard screenshots."
    args_schema: type[BaseModel] = ScreenshotAnalyzerSchema

    def _run(self, image_path: str, prompt: str = "Analyze this security dashboard screenshot. Extract all alerts, IPs, timestamps, and severity levels.") -> str:
        if not os.path.exists(image_path):
            return f"Error: Image artifact {image_path} not found."
            
        try:
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
            return f"Vision Analysis Failed: {str(e)}. Ensure llama3.2-vision is pulled in Ollama."
