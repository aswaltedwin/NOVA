# 🛡️ NOVA: Autonomous Multi-Agent Cyber Defense (Phase 2)

**NOVA** (Network Operations Visual Analyst) is a 100% free, local, and autonomous multi-agent cybersecurity system. Built in 2026, it leverages **CrewAI**, **Ollama**, and **ChromaDB** to provide agentic triage, deep RAG knowledge, and explainable threat analysis.

---

## 🌟 Key Features (Sentinel Upgrade)

### 🏥 Phase 1: Core Triage (Completed)
- **Hierarchical Multi-Agent Crew**: LogParser, ThreatAnalyzer, ReportGenerator, and NovaManager.
- **Local-Only LLM**: Powered by **Ollama** (qwen2.5:14b / deepseek-r1).
- **Explainable AI (XAI)**: Full chain-of-thought tracing for every triage session.

### 🛡️ Phase 2: Sentinel Upgrade (Latest)
- **Local RAG Integration**: Powered by **ChromaDB** with a built-in knowledge base of 30+ MITRE ATT&CK techniques.
- **Agentic Memory**: Enabled short-term and long-term context retention across analysis sessions.
- **Advanced Tooling**:
    - `RAGSearchTool`: Semantic search over the local MITRE database.
    - `FileReaderTool`: Ingestion of large local log files (txt, log, json).
    - `RiskCalculatorTool`: Context-aware security scoring.
- **Master Datasets**: Includes 1000+ lines of realistic synthetic logs (Auth, Web, EDR, Network) for production-like testing.

---

## 🛠️ Tech Stack

- **Orchestration**: [CrewAI](https://crewai.com) (v0.100+)
- **LLM Engine**: [Ollama](https://ollama.ai/)
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2) - 100% local
- **Vector Store**: [ChromaDB](https://www.trychroma.com/)
- **Frontend**: Streamlit (Premium UI)

---

## 🚀 Quick Start

### 1. Prerequisites
Install [Ollama](https://ollama.ai/) and pull the local models:
```bash
ollama pull qwen2.5:14b
ollama pull nomic-embed-text # Optional: Local embedding model
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
streamlit run main.py
```

> [!IMPORTANT]
> **First Run**: Click the **"Initialize/Reset RAG Knowledge Base"** button in the sidebar to populate your local ChromaDB with MITRE ATT&CK intelligence.

---

## 🏗️ Architecture

1.  **Ingestion**: `LogParserAgent` structure raw inputs using the `FileReaderTool`.
2.  **Intelligence**: `ThreatAnalyzerAgent` queries the `RAGSearchTool` to map anomalies to MITRE Tactic IDs.
3.  **Synthesis**: `ReportGeneratorAgent` produces executive summaries with risk heatmaps.
4.  **Memory**: The `NovaManager` reviews past interactions to identify persistent threat patterns.

---

## 📊 Phase 3 Preview (Coming Soon)
- **Computer Vision**: Analyze SOC screenshots with Llama-3.2-Vision.
- **Active Defense**: Automated firewall/EDR isolation integration.
- **Sandboxing**: Local container execution for malware analysis.

---

## 📝 License
MIT License - Open Source & Community Driven.
