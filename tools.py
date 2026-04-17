from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
from typing import Dict, Any, Optional

class FileReaderSchema(BaseModel):
    """Input for FileReaderTool."""
    file_path: str = Field(..., description="The relative or absolute path to the local file.")

class FileReaderTool(BaseTool):
    name: str = "Local File Reader"
    description: str = "Reads sensitive local log files or threat intelligence documents for context."
    args_schema: type[BaseModel] = FileReaderSchema

    def _run(self, file_path: str) -> str:
        """Reads a file from the local workspace."""
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class RiskCalculatorSchema(BaseModel):
    """Input for RiskCalculatorTool."""
    severity: str = Field(..., description="Severity level: low, medium, high, or critical.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0.")
    context: Optional[str] = Field(None, description="Additional context or matching MITRE techniques.")

class RiskCalculatorTool(BaseTool):
    name: str = "Advanced Risk Score Calculator"
    description: str = "Calculates threat risk score (0-100) based on severity, confidence, and environmental context."
    args_schema: type[BaseModel] = RiskCalculatorSchema

    def _run(self, severity: str, confidence: float, context: Optional[str] = None) -> str:
        """As specified: severity (low/medium/high/critical) and confidence (0.0-1.0)."""
        scores = {"low": 20, "medium": 50, "high": 80, "critical": 95}
        base = scores.get(severity.lower(), 50)
        
        # Adjust base based on confidence
        final_score = int(base * confidence)
        
        # Adjust for context (e.g., matching known MITRE techniques)
        if context and any(x in context.upper() for x in ["T1", "ATT&CK", "EXPLOIT"]):
            final_score = min(100, final_score + 10)
            
        risk_level = "LOW"
        if final_score >= 80: risk_level = "CRITICAL/HIGH"
        elif final_score >= 55: risk_level = "HIGH"
        elif final_score >= 40: risk_level = "MEDIUM"
        
        return f"Risk Score: {final_score} (Level: {risk_level}) Based on Severity {severity}, Confidence {confidence}, and context: {context[:50] if context else 'None'}..."

