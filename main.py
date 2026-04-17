import streamlit as st
from crewai import Crew, Process
from agents import NovaAgents
from tasks import NovaTasks
from utils import load_sample_logs, save_report, initialize_rag
from config import Config
import os

# Page Configuration
st.set_page_config(page_title="NOVA 🛡️ Sentinel Upgrade Phase 2", layout="wide")

def run_nova_sentinel(log_input, model_name):
    # Initialize agents and tasks
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    # Instantiate agents
    parser_agent = agents.log_parser_agent()
    analyzer_agent = agents.threat_analyzer_agent()
    reporter_agent = agents.report_generator_agent()

    # Define the workflow (Hierarchical)
    crew = Crew(
        agents=[parser_agent, analyzer_agent, reporter_agent],
        tasks=[
            tasks.parse_task(parser_agent, log_input),
            tasks.analyze_task(analyzer_agent),
            tasks.report_task(reporter_agent)
        ],
        process=Process.sequential,
        verbose=True,
        memory=True, # CrewAI built-in memory
        embedder=Config.get_embedder() # Uses local Ollama model (nomic-embed-text)
    )

    return crew.kickoff()

def main():
    st.markdown("# 🛡️ NOVA: Sentinel Upgrade-Phase 2")
    st.markdown("### **Autonomous Cyber Defense** | RAG Memory & Agentic Collaboration")

    # Sidebar for control
    st.sidebar.header("NOVA Command Hub")
    model_choice = st.sidebar.selectbox("Local/Cloud Ollama Model", ["deepseek-v3.1:671b-cloud", "qwen2.5:7b", "deepseek-r1", "llama3.3"], index=0)
    
    # RAG Init Status
    if st.sidebar.button("⚙️ Initialize/Reset RAG Knowledge Base"):
        with st.status("Initializing MITRE ATT&CK database..."):
            status_msg = initialize_rag()
            st.sidebar.success(status_msg)
    
    # Data Mode
    data_mode = st.sidebar.radio("Input Source", ["Sample Dataset", "Direct Log Entry", "Local File (Phase 2)"])
    
    logs = load_sample_logs()
    
    if data_mode == "Sample Dataset":
        selected_sample = st.selectbox("Select a Sample Log:", [f"Log {s['id']}: {s['label'].replace('_', ' ').capitalize()}" for s in logs])
        log_id = int(selected_sample.split(":")[0].split(" ")[1])
        user_log = next(s['raw'] for s in logs if s['id'] == log_id)
        st.code(user_log, language="bash")
        
    elif data_mode == "Local File (Phase 2)":
        user_log = st.text_input("Enter local file path (Relative or Absolute):", value="sample_intel.txt")
        if not os.path.exists(user_log):
            st.warning("File not found! Please ensure it exists.")
        else:
            st.info("File detected. NOVA will use the File Reader tool.")
            
    else:
        user_log = st.text_area("Paste Raw Security Log:", placeholder="2026-04-14 [AUTH] FAILED...")

    if st.button("🚀 Execute NOVA Sentinel Triage"):
        if not user_log:
            st.error("Missing log input!")
            return

        cols = st.columns(2)
        with cols[0]:
            st.subheader("🕵️ Agent Collaboration Trace")
            with st.status("NOVA Agents collaborating...", expanded=True) as status:
                st.write("📖 Memory retrieval in progress...")
                st.write("🔍 RAG Search Tool querying MITRE ATT&CK...")
                # Result is kickoff
                result = run_nova_sentinel(user_log, model_choice)
                status.update(label="Triage Complete!", state="complete", expanded=False)

        with cols[1]:
            st.subheader("📊 Sentinel Security Report")
            st.markdown(result)
            
            # Action buttons
            st.download_button("📥 Download Report (MD)", result.raw if hasattr(result, 'raw') else str(result), file_name=f"nova_sentinel_report.md")
            if st.button("💾 Save to Global Repository"):
                save_report({"model": model_choice, "report": str(result)}, "nova_sentinel_log.json")
                st.toast("Report saved locally.")

    # Memory Hub Mockup (Phase 2 Visual)
    st.divider()
    st.subheader("🧠 Memory & Knowledge Hub")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Knowledge Base Status**: 30 MITRE techniques active in ChromaDB.")
    with col2:
        st.info("**Short-term Memory**: Enabled (stores task outputs for contextual reasoning).")

if __name__ == "__main__":
    main()
