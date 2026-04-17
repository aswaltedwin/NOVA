# 🛡️ NOVA: Autonomous Multi-Agent Active Defense (Phase 3.1)

**NOVA** (Network Operations Visual Analyst) is an autonomous, semi-autonomous cybersecurity defense system. It doesn't just triage—it responds. Built for the modern SOC, NOVA combines agentic reasoning with local containment tools and multi-modal vision analysis.

---

## 🌟 Key Features (Active Defense Upgrade)

### 🛡️ Active Response Center (Phase 3.1)
- **Semi-Autonomous Containment**: The `ResponderAgent` identifies optimal mitigation actions and generates step-by-step remediation playbooks.
- **Simulation Safeguards**: All defensive actions (Firewall blocks, Process Isolation) run in **Simulation Mode** first, requiring human-in-the-loop (HITL) approval before execution.
- **Audit Logging**: Every agent-suggested action is recorded in a persistent JSON audit trail for compliance and forensic review.

### 👁️ Multi-Modal Intelligence
- **Computer Vision**: Analyze SIEM/EDR screenshots directly via the `ScreenshotAnalyzerTool` powered by **Llama-3.2-Vision**. 
- **Auto-Ingestion**: Correlate visual alert evidence with raw log telemetry in a unified triage mission.

### 🧠 Distributed Intelligence (RAG)
- **100+ MITRE Techniques**: Expanded local knowledge base (ChromaDB) for high-fidelity threat mapping.
- **Micro-Sandboxing**: Foundations for local containerized behavior analysis (SandboxAnalyzer) to return verdicts on suspicious binaries.

---

## 🛠️ Tech Stack

- **Orchestration**: [CrewAI](https://crewai.com) (Hierarchical Supervisor Process)
- **LLM Engine**: [Ollama](https://ollama.ai/) (`llama3.2` and `llama3.2-vision`)
- **Embeddings**: `sentence-transformers` (100% local)
- **Backend**: FastAPI (Python)
- **Visuals**: Chart.js & Vanilla CSS (Premium Command Center)
- **Vector Base**: ChromaDB

---

## 🚀 Quick Start (Zero-Touch Onboarding)

### 1. Prerequisites
Install [Ollama](https://ollama.ai/) and pull the required local models:
```bash
ollama pull llama3.2
ollama pull llama3.2-vision
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
> **Zero-Touch Setup**: On the first run, NOVA automatically seeds its MITRE knowledge base and opens the Command Center at `http://localhost:8000`.

---

## 🏗️ Architecture (Phase 3)

1.  **Ingestion**: `LogParserAgent` and `VisionTool` ingest multi-modal artifacts.
2.  **Analysis**: `ThreatAnalyzerAgent` maps signals to the expanded RAG intelligence base.
3.  **Containment**: `ResponderAgent` recommends OS-level actions based on risk scores (>75).
4.  **HITL Approval**: The analyst approves, executes, or simulates actions through the **Response Center**.
5.  **Learning**: Feedback is persisted into long-term memory to refine future containment logic.

---

## 📊 Phase 3.x Roadmap
- **CACAO Playbooks**: Export standard actionable response playbooks.
- **Full Sandboxing**: Complete `docker-py` integration for real-world malware detonating.
- **Network Isolation**: Automated VLAN/Interface containment logic.

---

## 📝 License
MIT License - Open Source & Community Driven.
