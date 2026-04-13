from crewai.tools import BaseTool
import re
from typing import Dict, Any

class LogParserTool(BaseTool):
    name: str = "Security Log Parser"
    description: str = "Extracts key metadata (IP, User, Action, Timestamp) from raw text logs."

    def _run(self, raw_log: str) -> Dict[str, Any]:
        """High-performance regex parsing."""
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        found_ips = re.findall(ip_pattern, raw_log)
        
        user_pattern = r'user=["\'](.*?)["\']|user:(\w+)|account:(\w+)'
        users = [u for matches in re.findall(user_pattern, raw_log) for u in matches if u]
        
        actions = ["LOGIN", "DENIED", "FAILED", "SUCCESS", "REMOVED", "CREATED", "EXECUTED", "DOWNLOAD"]
        found_action = next((a for a in actions if a.lower() in raw_log.lower()), "UNKNOWN")
        
        return {
            "entities": {"ips": list(set(found_ips)), "users": list(set(users)), "action": found_action},
            "raw": raw_log
        }

class RiskCalculatorTool(BaseTool):
    name: str = "Risk Score Calculator"
    description: str = "Calculates threat risk score (0-100) based on severity and confidence."

    def _run(self, severity: str, confidence: float) -> str:
        """As specified: severity (low/medium/high/critical) and confidence (0.0-1.0)."""
        scores = {"low": 20, "medium": 50, "high": 80, "critical": 95}
        base = scores.get(severity.lower(), 50)
        
        # Multiply base by confidence factor
        final_score = int(base * confidence)
        
        risk_level = "LOW"
        if final_score >= 80: risk_level = "CRITICAL/HIGH"
        elif final_score >= 50: risk_level = "MEDIUM"
        
        return f"Risk Score: {final_score} (Level: {risk_level}) Based on Severity {severity} and Confidence {confidence}"
