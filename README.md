# 🛡️ NOVA: Autonomous Multi-Agent SOC Command Center (Phase 2)

**NOVA** (Network Operations Visual Analyst) is a 100% free, local, and autonomous multi-agent cybersecurity system. Transform your security logs into a professional triage mission with a premium, single-page command center.

---

## 🌟 Key Features (Sentinel Upgrade)

### 🕵️ Global Triage Center
- **FastAPI + JS Architecture**: A lightning-fast, glassmorphic single-page application (SPA).
- **Hierarchical Engine**: Controlled by a `NovaManager` supervisor, ensuring coordinated mission execution across Parser, Analyzer, and Reporter agents.
- **Explainable AI (XAI)**: A live collaboration console streaming a real-time chain-of-thought trace from the agents.

### 🧠 Deep Intelligence (RAG)
- **MITRE ATT&CK Mastery**: Built-in 100% local knowledge base covering **102 mapped MITRE techniques**.
- **Learned Context**: Analysts can mark findings as "Confirmed" or "False Positive," updating the long-term vector memory for evolving defense.

### 📂 Synthetic Telemetry Repository
- **Ready-to-Triage Data**: Includes 1000+ lines of realistic synthetic logs across Web, Network, Auth, and Lateral Movement categories.
- **One-Click Loading**: Instantly ingest high-fidelity artifacts from the built-in **Intelligence Gallery**.

---

## 🛠️ Tech Stack

- **Orchestration**: [CrewAI](https://crewai.com) (Hierarchical Process)
- **LLM Engine**: [Ollama](https://ollama.ai/) (Local `llama3.2` default)
- **Embeddings**: `sentence-transformers` (100% local)
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JS + CSS (Premium Aesthetics)
- **Vector Base**: ChromaDB

---

## 🚀 Quick Start (Zero-Touch Onboarding)

### 1. Prerequisites
Install [Ollama](https://ollama.ai/) and pull the local models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 2. Installation
```bash
git clone https://github.com/aswaltedwin/NOVA
cd NOVA
pip install -r requirements.txt
```

### 3. Usage
Launch the NOVA Sentinel Command Center:
```bash
python app.py
```

> [!TIP]
> **Zero-Touch Setup**: On the first run, NOVA will automatically detect the empty knowledge base and auto-seed it with 102 MITRE techniques. It will also automatically open your default browser to `http://localhost:8000`.

---

## 🏗️ Architecture

1.  **Ingestion**: `LogParserAgent` normalizes telemetry streams.
2.  **Intelligence**: `ThreatAnalyzerAgent` maps anomalies to the expanded MITRE base.
3.  **Human-in-the-Loop**: The analyst validates intermediate findings before the final synthesis.
4.  **Learning**: Feedback is persisted into long-term vector memory to improve future missions.

---

## 📊 Phase 3 Preview (Coming Soon)
- **Computer Vision**: Analyze SOC screenshots with Llama-3.2-Vision.
- **Active Defense**: Automated firewall/EDR isolation integration.
- **Sandboxing**: Local container execution for malware analysis.

---

## 📝 License
MIT License - Open Source & Community Driven.
