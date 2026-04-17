from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
import psutil
import datetime
import subprocess

AUDIT_LOG = "nova_action_audit.json"

def log_action(tool_name, action, target, risk, state="SIMULATED"):
    """Records security actions for auditing and human-in-the-loop review."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": tool_name,
        "action": action,
        "target": target,
        "risk": risk,
        "state": state
    }
    history = []
    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r") as f:
            try: history = json.load(f)
            except: pass
    history.append(entry)
    with open(AUDIT_LOG, "w") as f:
        json.dump(history, f, indent=2)

class FirewallBlockSchema(BaseModel):
    ip_address: str = Field(..., description="Malicious IP address to block.")
    direction: str = Field("in", description="Traffic direction: in/out.")

class FirewallBlockTool(BaseTool):
    name: str = "Firewall Block Policy Tool"
    description: str = "Recommends or executes firewall rules to block malicious IPs. Always starts in SIMULATION mode."
    args_schema: type[BaseModel] = FirewallBlockSchema

    def _run(self, ip_address: str, direction: str = "in") -> str:
        # Simulation Logic
        log_action("FirewallBlockTool", "BLOCK_IP", ip_address, "SAFE", "SIMULATED")
        
        # OS Detection for suggestion
        cmd_suggestion = f"netsh advfirewall firewall add rule name='NOVA_BLOCK_{ip_address}' dir={direction} action=block remoteip={ip_address}"
        if os.name != 'nt':
            cmd_suggestion = f"iptables -A INPUT -s {ip_address} -j DROP"

        return f"[SIMULATION] Recommended Firewall Policy: {cmd_suggestion}. Action logged for analyst approval."

class ProcessIsolationSchema(BaseModel):
    pid: int = Field(..., description="Process ID to terminate or isolate.")
    reason: str = Field(..., description="Security rationale for isolation.")

class ProcessIsolationTool(BaseTool):
    name: str = "Process Isolation Tool"
    description: str = "Recommends process termination or containment for suspicious binaries."
    args_schema: type[BaseModel] = ProcessIsolationSchema

    def _run(self, pid: int, reason: str) -> str:
        proc_name = "Unknown"
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except: pass

        log_action("ProcessIsolationTool", "KILL_PID", f"{pid} ({proc_name})", "MEDIUM", "SIMULATED")
        return f"[SIMULATION] Recommended Action: Terminate PID {pid} ({proc_name}). Reason: {reason}. Action logged for analyst approval."
