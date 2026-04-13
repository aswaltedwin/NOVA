import streamlit as st
import pandas as pd
from crewai import Crew, Process
from agents import NovaAgents
from tasks import NovaTasks
from utils import load_sample_dataset, save_report
from config import Config
import json

# Page optimization
st.set_page_config(page_title="NOVA | Agentic Cyber Defense", layout="wide")

def run_nova_crew(log_input, model_name):
    # Initialize agents and tasks
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    # Instantiate agents
    parser_agent = agents.log_parser_agent()
    analyzer_agent = agents.threat_analyzer_agent()
    reporter_agent = agents.report_generator_agent()
    manager_agent = agents.nova_manager()

    # Define the workflow
    crew = Crew(
        agents=[parser_agent, analyzer_agent, reporter_agent],
        tasks=[
            tasks.parse_task(parser_agent, log_input),
            tasks.analyze_task(analyzer_agent),
            tasks.report_task(reporter_agent)
        ],
        process=Process.hierarchical,
        manager_agent=manager_agent,
        manager_llm=Config.get_llm(model_name),
        verbose=True,
        memory=True
    )

    return crew.kickoff()

def main():
    st.markdown("# 🔥 NOVA: Agentic Cyber Defense")
    st.markdown("### **Phase 1**: Autonomous NLP Threat Triage (100% Local)")

    # Sidebar for control
    st.sidebar.header("NOVA Command Center")
    model_choice = st.sidebar.selectbox("Ollama Model", ["qwen2.5:14b", "deepseek-r1", "llama3.3"], index=0)
    option = st.sidebar.selectbox("Choose Mode", ["Streamlit Dashboard", "CLI Simulation Mode"])
    
    # Load samples
    samples = load_sample_dataset()
    
    if option == "CLI Simulation Mode":
        st.write("---")
        st.subheader("Manual Log Input")
        user_log = st.text_area("Paste Raw Security Log Here:", value=samples[0]["raw"])
        
        if st.button("🚀 Analyze with NOVA Crew"):
            with st.status("NOVA Agents collaborating...", expanded=True) as status:
                result = run_nova_crew(user_log, model_choice)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            st.success("Triage Report Generated!")
            st.markdown(result)
            
            if st.button("Save Report"):
                report_path = save_report(str(result))
                st.info(f"Report saved locally to {report_path}")

    else:
        st.write("Select a representative sample log for triage:")
        sample_options = [f"Log {s['id']}: {s['label'].replace('_', ' ').capitalize()}" for s in samples]
        selected_sample_text = st.selectbox("Sample Database", sample_options)
        
        log_id = int(selected_sample_text.split(":")[0].split(" ")[1])
        selected_log = next(s['raw'] for s in samples if s['id'] == log_id)
        
        st.info(f"Loaded {selected_sample_text}")
        st.code(selected_log, language="bash")

        if st.button("🛡️ Run NOVA Triage"):
            with st.spinner("NOVA agents are collaborating..."):
                result = run_nova_crew(selected_log, model_choice)
            
            st.subheader("📊 NOVA Final Security Report")
            st.markdown(result)
            
            # Download/Save actions
            st.download_button("📥 Download Report (MD)", result.raw if hasattr(result, 'raw') else str(result), file_name=f"nova_triage_{log_id}.md")
            if st.button("💾 Save as JSON"):
                save_report({"log_id": log_id, "report": str(result)}, f"nova_report_{log_id}.json")
                st.toast("Report saved locally.")

if __name__ == "__main__":
    main()
