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
    {"id": "T1027", "name": "Obfuscated Files or Information", "description": "Encrypting or encoding payloads to bypass static signature detection."},
    # Expanded Phase 2 Data (100+ goal)
    {"id": "T1055", "name": "Process Injection", "description": "Injecting malicious code into legitimate processes to hide and gain privileges."},
    {"id": "T1133", "name": "External Remote Services", "description": "Using VPNs or Proxies to gain initial access from outside."},
    {"id": "T1136", "name": "Create Account", "description": "Creating new system users to maintain persistence."},
    {"id": "T1211", "name": "Exploitation for Privilege Escalation", "description": "Targeting local vulnerabilities to gain SYSTEM or Root access."},
    {"id": "T1033", "name": "System Owner/User Discovery", "description": "Learning who is logged in to target higher-privilege accounts."},
    {"id": "T1016", "name": "System Network Configuration Discovery", "description": "Enumerating network interfaces and routing tables for lateral movement."},
    {"id": "T1082", "name": "System Information Discovery", "description": "Gleaning OS version and patch levels for targeted exploitation."},
    {"id": "T1083", "name": "File and Directory Discovery", "description": "Scanning the filesystem for sensitive data like spreadsheets or database files."},
    {"id": "T1105", "name": "Ingress Tool Transfer", "description": "Downloading malicious tools from external C2 servers onto the target."},
    {"id": "T1074", "name": "Data Staged", "description": "Collecting stolen data into a central directory before exfiltration."},
    {"id": "T1485", "name": "Data Destruction", "description": "Irreversibly deleting data to cause business disruption."},
    {"id": "T1489", "name": "Service Stop", "description": "Stopping security services (Sysmon, CrowdStrike, etc.) to blinding the SOC."},
    {"id": "T1490", "name": "Inhibit System Recovery", "description": "Deleting VSS snapshots or backups to ensure ransomware payment."},
    {"id": "T1569", "name": "System Services", "description": "Using Service Control Manager (SCM) to execute malicious binaries."},
    {"id": "T1570", "name": "Lateral Tool Transfer", "description": "Using SMB/WMI to push tools between internal workstations."},
    {"id": "T1571", "name": "Non-Standard Port", "description": "Communicating on ports like 4444 or 8888 to hide C2 traffic."},
    {"id": "T1572", "name": "Protocol Tunneling", "description": "Tunneling malicious data through standard protocols like DNS or ICMP."},
    {"id": "T1573", "name": "Encrypted Channel", "description": "Using AES or RSA to encrypt C2 traffic and avoid deep packet inspection."},
    {"id": "T1574", "name": "Hijack Execution Flow", "description": "Using DLL Search Order Hijacking or PATH abuse to run malware."},
    {"id": "T1592", "name": "Gather Victim Host Information", "description": "Reconnaissance targeting specific workstations or servers."},
    {"id": "T1595", "name": "Active Scanning", "description": "Using Nmap or Masscan to find external vulnerabilities."},
    {"id": "T1608", "name": "Stage Capabilities", "description": "Preparing malicious infrastructure (certificates, domains) before an attack."},
    {"id": "T1614", "name": "System Location Discovery", "description": "Identifying physical or logical location of the target to ensure targeting accuracy."},
    {"id": "T1620", "name": "Reflective Code Loading", "description": "Loading code into memory without writing to disk to evade antivirus."},
    {"id": "T1622", "name": "Debugger Evasion", "description": "Detecting if the malware is being analyzed in a VM or debugger and stopping execution."},
    {"id": "T1036", "name": "Masquerading", "description": "Renaming malicious binaries to look like legitimate ones (e.g., svchost.exe)."},
    {"id": "T1047", "name": "Windows Management Instrumentation (WMI)", "description": "Using WMI to execute code or discover system info remotely."},
    {"id": "T1056", "name": "Input Capture", "description": "Keylogging or capturing GUI input to steal credentials."},
    {"id": "T1069", "name": "Permission Groups Discovery", "description": "Enumerating Domain Admins or local Admin groups."},
    {"id": "T1098", "name": "Account Manipulation", "description": "Modifying account permissions or adding SSH keys to maintain access."},
    {"id": "T1102", "name": "Web Service - C2", "description": "Using Slack, Discord, or GitHub as a C2 channel."},
    {"id": "T1112", "name": "Modify Registry", "description": "Changing registry keys for persistence or to disable security features."},
    {"id": "T1113", "name": "Screen Capture", "description": "Taking screenshots of the analyst's desktop to steal info."},
    {"id": "T1115", "name": "Clipboard Data", "description": "Stealing data from the system clipboard."},
    {"id": "T1119", "name": "Automated Collection", "description": "Running scripts to automatically grab documents based on keywords."},
    {"id": "T1120", "name": "Peripheral Device Discovery", "description": "Searching for connected USB or network drives."},
    {"id": "T1123", "name": "Audio Capture", "description": "Using the microphone to listen to local conversations."},
    {"id": "T1124", "name": "System Time Discovery", "description": "Checking system time for time-based evasion or scheduling."},
    {"id": "T1125", "name": "Video Capture", "description": "Using the webcam to spy on the user."},
    {"id": "T1127", "name": "Trusted Developer Utilities Proxy Execution", "description": "Using MSBuild or InstallUtil to bypass AppLocker."},
    {"id": "T1129", "name": "Shared Modules", "description": "Loading malicious DLLs via standard system APIs."},
    {"id": "T1140", "name": "Deobfuscate/Decode Files or Information", "description": " مالware decoding its own payloads after execution."},
    {"id": "T1202", "name": "Indirect Command Execution", "description": "Using forfiles or pcalua to run commands around security monitors."},
    {"id": "T1205", "name": "Traffic Signaling", "description": "Port knocking to open access to a hidden service."},
    {"id": "T1218", "name": "System Binary Proxy Execution", "description": "Using LOLBins like Rundll32 or Regsvr32 to execute code."},
    {"id": "T1482", "name": "Domain Trust Discovery", "description": "Mapping Active Directory forest and domain trusts for lateral movement."},
    {"id": "T1496", "name": "Resource Hijacking", "description": "Using system CPU/GPU for cryptomining (Cryptojacking)."},
    {"id": "T1497", "name": "Virtualization/Sandbox Evasion", "description": "Checking for artifacts of VMware, VirtualBox, or Cuckoo Sandbox."},
    {"id": "T1505", "name": "Server Software Component", "description": "Installing Web Shells on compromised IIS/Apache servers."},
    {"id": "T1529", "name": "System Shutdown/Reboot", "description": "Forcing a reboot to ensure persistence mechanisms are triggered."},
    {"id": "T1534", "name": "Internal Spearphishing", "description": "Sending phishing emails from a compromised internal account to colleagues."},
    {"id": "T1539", "name": "Steal Web Session Cookie", "description": "Harvesting cookies to bypass MFA and hijack sessions."},
    {"id": "T1542", "name": "Pre-OS Boot", "description": "Installing Rootkits/Bootkits in the UEFI or BIOS."},
    {"id": "T1546", "name": "Event Triggered Execution", "description": "Running malware when the user logs on or a certain file is opened."},
    {"id": "T1547", "name": "Boot or Logon Autostart Execution", "description": "Persistent malware in Registry Run keys or Startup folders."},
    {"id": "T1550", "name": "Use Alternate Authentication Material", "description": "Pass-the-Hash or Pass-the-Ticket attacks."},
    {"id": "T1553", "name": "Subvert Trust Controls", "description": "Installing rogue CA certificates or using stolen code-signing certs."},
    {"id": "T1555", "name": "Credentials from Password Stores", "description": "Stealing passwords from browsers or the Windows Vault."},
    {"id": "T1557", "name": "Adversary-in-the-Middle", "description": "Using LLMNR/NBT-NS Poisoning to steal hashes."},
    {"id": "T1559", "name": "Inter-Process Communication", "description": "Using COM or DDE to trigger malicious logic in other apps."},
    {"id": "T1563", "name": "Remote Service Session Hijacking", "description": "Hijacking an existing RDP session."},
    {"id": "T1564", "name": "Hide Artifacts", "description": "Using hidden files or Alternate Data Streams (ADS) to hide malware."},
    {"id": "T1568", "name": "Dynamic Resolution", "description": "Using Domain Generation Algorithms (DGA) to find C2 servers."},
    {"id": "T1578", "name": "Modify Cloud Compute Infrastructure", "description": "Creating rogue instances or snapshots in AWS/Azure/GCP."},
    {"id": "T1583", "name": "Acquire Infrastructure", "description": "Buying domains or botnets for an upcoming attack."}
]

def initialize_rag():
    """Seed the RAG knowledge base with MITRE ATT&CK data."""
    from rag_tool import RAGSearchTool
    rag = RAGSearchTool()
    
    # Optional: Clear existing data for a clean reset if necessary
    # rag.collection.delete(where={"id": {"$ne": ""}}) # Simplified reset logic
    
    docs = [f"ID: {item['id']} | Name: {item['name']} | Description: {item['description']}" for item in MITRE_DATA]
    ids = [item['id'] for item in MITRE_DATA]
    
    # Upsert allows both initial seeding and updates
    rag.add_knowledge(documents=docs, ids=ids)
    return f"Successfully synced {len(ids)} MITRE ATT&CK entries to local knowledge base."


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
