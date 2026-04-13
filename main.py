import streamlit as st
import pandas as pd
from crewai import Crew, Process
from agents import NovaAgents
from tasks import NovaTasks
from utils import load_sample_dataset
from config import Config
import json

# Page optimization
st.set_page_config(page_title="NOVA | Autonomous Cyber Triage", layout="wide")

def run_nova_crew(log_input, model_name):
    # Initialize agents and tasks
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    # Instantiate agents
    parser_agent = agents.log_parser_agent()
    analyzer_agent = agents.threat_analyzer_agent()
    reporter_agent = agents.report_generator_agent()
    manager_agent = agents.manager_agent()

    # Define the workflow
    crew = Crew(
        agents=[parser_agent, analyzer_agent, reporter_agent],
        tasks=[
            tasks.parse_task(parser_agent, log_input),
            tasks.analyze_task(analyzer_agent),
            tasks.report_task(reporter_agent)
        ],
        process=Process.hierarchical,
        manager_llm=Config.get_llm(model_name),
        verbose=True,
        memory=True
    )

    return crew.kickoff()

def main():
    st.markdown("# 🛡️ NOVA: Autonomous Cyber Triage Phase 1")
    st.markdown("### 100% Free & Local Multi-Agent Cyber Simulation")

    # Sidebar for control
    st.sidebar.header("NOVA Controls")
    model_choice = st.sidebar.selectbox("Ollama Model", ["qwen2.5:14b", "deepseek-r1", "llama3.3"], index=0)
    
    # Load samples
    samples = load_sample_dataset()
    sample_options = [f"Log {s['id']}: {s['label']}" for s in samples]
    selected_sample = st.sidebar.selectbox("Load Sample Log", ["Manual Input"] + sample_options)

    if selected_sample == "Manual Input":
        user_log = st.text_area("Paste Raw Security Log Here:", placeholder="2026-04-13 22:01:45 [AUTH] FAILED...")
    else:
        log_id = int(selected_sample.split(":")[0].split(" ")[1])
        user_log = next(s['raw'] for s in samples if s['id'] == log_id)
        st.info(f"Loaded {selected_sample}")
        st.code(user_log)

    if st.button("🚀 Analyze Threat with NOVA Crew"):
        if not user_log:
            st.error("Please provide a log first!")
            return

        with st.status("NOVA Agents collaborating... (Chain-of-Thought in progress)", expanded=True) as status:
            st.write("🕵️ Log Data Architect parsing entities...")
            # Result is kickoff
            result = run_nova_crew(user_log, model_choice)
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        st.markdown("## 📊 NOVA Security Triage Report")
        st.markdown(result)
        
        # Download option
        st.download_button("📥 Download Report (MD)", result.raw if hasattr(result, 'raw') else str(result), file_name="nova_report.md")

if __name__ == "__main__":
    main()
