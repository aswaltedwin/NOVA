from crewai.tools import BaseTool
import re
from typing import Dict, Any, List

class LogParserTool(BaseTool):
    name: str = "Log Parser Utility"
    description: str = "Parses raw security logs to extract structured JSON (IP, Timestamp, User, Action, etc.)."

    def _run(self, raw_log: str) -> Dict[str, Any]:
        """Simple regex-based log parsing pattern. Real production would use more complex OSINT/YARA-style rules."""
        
        # Look for IP addresses
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        found_ips = re.findall(ip_pattern, raw_log)
        
        # Look for users
        user_pattern = r'user=["\'](.*?)["\']|user:(\w+)|account:(\w+)'
        users = [u for matches in re.findall(user_pattern, raw_log) for u in matches if u]
        
        # Look for actions (Login, Access, Denied, Delete, etc.)
        actions = ["LOGIN", "DENIED", "FAILED", "SUCCESS", "REMOVED", "CREATED", "EXECUTED"]
        found_action = next((a for a in actions if a.lower() in raw_log.lower()), "UNKNOWN")
        
        return {
            "source_raw": raw_log,
            "entities": {
                "ips": list(set(found_ips)),
                "users": list(set(users)),
                "detected_action": found_action
            },
            "structured": True
        }

class RiskScorerTool(BaseTool):
    name: str = "Risk Calculator"
    description: str = "Calculates a dynamic risk score (0-10) based on threat severity, confidence, and environmental context."

    def _run(self, severity: str, confidence: float, impact: str) -> Dict[str, Any]:
        """Dynamic heuristic risk calculation."""
        
        severity_map = {"LOW": 1.0, "MEDIUM": 2.5, "HIGH": 4.5, "CRITICAL": 6.0}
        impact_map = {"LOW": 0.5, "MEDIUM": 1.0, "HIGH": 1.5, "CRITICAL": 2.0}
        
        base_score = severity_map.get(severity.upper(), 1.0)
        impact_mult = impact_map.get(impact.upper(), 1.0)
        
        final_score = min(10.0, (base_score * impact_mult) + (confidence * 2))
        
        risk_level = "LOW"
        if final_score >= 8: risk_level = "CRITICAL"
        elif final_score >= 6: risk_level = "HIGH"
        elif final_score >= 4: risk_level = "MEDIUM"

        return {
            "risk_score": round(final_score, 2),
            "risk_level": risk_level,
            "justification": f"Base severity {severity} with impact {impact} and confidence {confidence}."
        }
