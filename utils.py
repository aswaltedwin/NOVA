import json
import os
from typing import List, Dict

# NOVA Phase 2: Comprehensive MITRE ATT&CK Knowledge Base Initializer
MITRE_DATA = [
    {"id": "T1566", "name": "Phishing", "description": "Sending spearphishing emails to gain initial access via malicious attachments or links."},
    {"id": "T1110", "name": "Brute Force", "description": "Attacking account passwords by guessing or systematically checking combinations."},
    {"id": "T1071", "name": "Command and Control (C2) - Web Protocols", "description": "Using standard HTTP/S protocols to communicate with malware for exfiltration or control."},
    {"id": "T1059", "name": "Command and Scripting Interpreter", "description": "Leveraging PowerShell, Python, or Windows Command Shell to execute malicious logic."},
    {"id": "T1567", "name": "Data Exfiltration Over Web Service", "description": "Stealing data by uploading it to legitimate cloud services or external IPs."},
    {"id": "T1021", "name": "Remote Services", "description": "Using legitimate remote management tools like RDP or SSH to move laterally within a network."},
    {"id": "T1003", "name": "OS Credential Dumping", "description": "Harvesting credentials from operating system memory or files (e.g., LSASS memory)."},
    {"id": "T1078", "name": "Valid Accounts", "description": "Using compromised credentials for legitimate accounts to gain access and persist."},
    {"id": "T1548", "name": "Abuse Elevation Control Mechanism", "description": "Leveraging UAC or Sudo to gain higher privileges (e.g., Administrator or Root)."},
    {"id": "T1190", "name": "Exploit Public-Facing Application", "description": "Targeting vulnerabilities in web servers (SQL Injection, Heap Overflow, etc.)."},
    {"id": "T1210", "name": "Exploitation of Remote Services", "description": "Targeting vulnerabilities like EternalBlue or Log4j to gain access from outside."},
    {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "description": "Using DNS, ICMP, or non-standard ports to sneak data out of the network."},
    {"id": "T1053", "name": "Scheduled Task/Job", "description": "Achieving persistence by scheduling malicious scripts to run at specific times."},
    {"id": "T1486", "name": "Data Encrypted for Impact", "description": "The primary mechanism of Ransomware: encrypting user data to deny access."},
    {"id": "T1562", "name": "Impair Defenses", "description": "Disabling EDR, Antivirus, or Firewall processes to avoid detection."},
    {"id": "T1070", "name": "Indicator Removal", "description": "Deleting logs or history to hide traces of the intrusion."},
    {"id": "T1552", "name": "Unsecured Credentials", "description": "Searching local files for passwords stored in cleartext."},
    {"id": "T1090", "name": "Proxy/External Gateways", "description": "Using external gateways to proxy malicious traffic and hide the origin."},
    {"id": "T1134", "name": "AccessToken Manipulation", "description": "Forging or stealing security tokens to impersonate users."},
    {"id": "T1484", "name": "Domain Policy Modification", "description": "Changing Group Policy Objects (GPO) to propagate malware across a domain."},
    {"id": "T1543", "name": "Create or Modify System Process", "description": "Creating new Windows services or system processes for persistence."},
    {"id": "T1037", "name": "Boot or Logon Initialization Scripts", "description": "Using startup scripts to execute malicious payloads upon logon."},
    {"id": "T1558", "name": "Steal or Forge Kerberos Tickets", "description": "Golden Ticket or Silver Ticket attacks for domain-wide persistence."},
    {"id": "T1046", "name": "Network Service Discovery", "description": "Scanning the internal network for open ports and vulnerable services."},
    {"id": "T1135", "name": "Network Share Discovery", "description": "Searching for accessible SMB/NFS shares to find sensitive documents."},
    {"id": "T1560", "name": "Archive Collected Data", "description": "Compressing or encrypting exfiltrated data before upload (e.g., ZIP with password)."},
    {"id": "T1041", "name": "Exfiltration Over C2 Channel", "description": "Merging exfiltrated data into standard command-and-control heartbeats."},
    {"id": "T1491", "name": "Defacement", "description": "Changing the visual appearance of a website for geopolitical or hacktivist reasons."},
    {"id": "T1531", "name": "Account Access Removal", "description": "Locking out legitimate administrators to prevent incident response."},
    {"id": "T1027", "name": "Obfuscated Files or Information", "description": "Encrypting or encoding payloads to bypass static signature detection."}
]

def initialize_rag():
    """Seed the RAG knowledge base with MITRE ATT&CK data."""
    from rag_tool import RAGSearchTool
    rag = RAGSearchTool()
    
    docs = [f"ID: {item['id']} | Name: {item['name']} | Description: {item['description']}" for item in MITRE_DATA]
    ids = [item['id'] for item in MITRE_DATA]
    rag.add_knowledge(documents=docs, ids=ids)
    return f"Initialized RAG with {len(ids)} MITRE ATT&CK entries."

def load_sample_logs():
    """Legacy/Phase 1 sample logs for testing."""
    return [
        {"id": 1, "raw": "Failed login attempts from IP 45.67.89.12 (25 times in 5 min)", "label": "brute_force"},
        {"id": 2, "raw": "User 'admin' accessed sensitive HR database at 02:15 AM", "label": "insider_threat"},
        {"id": 3, "raw": "Normal traffic spike during business hours from known VPN", "label": "normal"},
        {"id": 4, "raw": "Suspicious PowerShell script execution on endpoint WIN-XYZ", "label": "malware"},
        {"id": 5, "raw": "Multiple DNS queries to rare domain 'x7k9p4q2z.com'", "label": "c2_beaconing"},
    ]

def save_report(report_data, filename="nova_report.json"):
    """Saves the final NOVA report to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    return filename
