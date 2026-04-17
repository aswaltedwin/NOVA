from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
import psutil
import datetime
import logging

logger = logging.getLogger("NOVA-Response")

AUDIT_LOG = "nova_action_audit.json"

def log_action(tool_name, action, target, risk, state="SIMULATED", script=None):
    """Records security actions for auditing and human-in-the-loop review."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": tool_name,
        "action": action,
        "target": target,
        "risk": risk,
        "state": state,
        "remediation_script": script
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
    reason: str = Field("Malicious traffic detected", description="Reason for the block.")

class FirewallBlockTool(BaseTool):
    name: str = "Firewall Block Policy Tool"
    description: str = "Generates and logs firewall containment rules. Always operates in SIMULATION mode for safety."
    args_schema: type[BaseModel] = FirewallBlockSchema

    def _run(self, ip_address: str, direction: str = "in", reason: str = "Malicious traffic") -> str:
        # OS Detection for proper script generation
        if os.name == 'nt':
            script = f"netsh advfirewall firewall add rule name='NOVA_BLOCK_{ip_address}' dir={direction} action=block remoteip={ip_address}"
            platform = "Windows (Netsh)"
        else:
            script = f"iptables -A {'INPUT' if direction=='in' else 'OUTPUT'} -s {ip_address} -j DROP"
            platform = "Linux (Iptables)"

        log_action("FirewallBlockTool", "BLOCK_IP", ip_address, "SAFE", "SIMULATED", script)
        
        return f"[SIMULATION] Generated {platform} Rule: {script}. Reason: {reason}. Action logged for review."

class ProcessIsolationSchema(BaseModel):
    pid: int = Field(..., description="Process ID to terminate or isolate.")
    reason: str = Field(..., description="Security rationale for isolation.")

class ProcessIsolationTool(BaseTool):
    name: str = "Process Isolation Tool"
    description: str = "Generates recommendations for process termination or isolation."
    args_schema: type[BaseModel] = ProcessIsolationSchema

    def _run(self, pid: int, reason: str) -> str:
        proc_name = "Unknown"
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except: pass

        script = f"Stop-Process -Id {pid} -Force" if os.name == 'nt' else f"kill -9 {pid}"
        
        log_action("ProcessIsolationTool", "TERMINATE_PROC", f"{proc_name} (PID: {pid})", "MEDIUM", "SIMULATED", script)
        
        return f"[SIMULATION] Recommended Action: {script}. Reason: {reason}. Target: {proc_name}. Action logged for review."
