# 🛡️ NOVA: Autonomous Multi-Agent Cyber Triage

**NOVA** (Network Operations Visual Analyst) is a 100% free, local, and autonomous multi-agent system for cyber threat triage. Built in 2026, it leverages the power of local LLMs and role-based agentic workflows to analyze security logs without sending data to the cloud.

---

## 🌟 Key Features

- **Multi-Agent Collaboration**: A crew of AI specialists working together (Log Architect, Threat Hunter, Incident Coordinator).
- **Local-First (Privacy)**: Powered by **Ollama**, ensuring your sensitive logs never leave your infrastructure.
- **Explainable AI (XAI)**: Full chain-of-thought reasoning for every threat detected.
- **MITRE ATT&CK Mapping**: Automatically maps malicious behaviors to standardized security frameworks.
- **Interactive Dashboard**: Premium Streamlit UI for real-time triage and report generation.

---

## 🛠️ Tech Stack

- **Core**: Python 3.12+
- **Orchestration**: [CrewAI](https://crewai.com) (Latest 2026 Version)
- **Local LLM**: [Ollama](https://ollama.ai/) (Recommended: `qwen2.5:14b` or `deepseek-r1`)
- **Frontend**: Streamlit
- **ML/Parsing**: Pandas, Scikit-learn, Transformers

---

## 🚀 Quick Start

### 1. Prerequisites
Install [Ollama](https://ollama.ai/) and pull the required model:
```bash
ollama pull qwen2.5:14b
```

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <your-repo-url>
cd NOVA
pip install -r nova_phase1/requirements.txt
```

### 3. Usage
Launch the NOVA Dashboard:
```bash
streamlit run main.py
```

---

## 🕵️ Agents in Action

1.  **LogParserAgent**: Normalizes raw logs into structured entities.
2.  **ThreatAnalyzerAgent**: Detects anomalies and calculates risk scores.
3.  **ReportGeneratorAgent**: Synthesizes findings into human-readable executive reports.
4.  **NovaManager**: Orchestrates the workflow and ensures quality control.

---

## 📊 Sample Datasets
NOVA comes pre-loaded with 15 realistic security logs covering:
- Brute Force & Credential Stuffing
- C2 Beaconing & DNS Tunneling
- SQL Injection & RCE
- Insider Threat & Data Exfiltration

---

## 📝 License
This project is open-source under the MIT License.

---

*NOVA Phase 1 is complete. Ready for Phase 2 integration (Vision & SOC automation).*
