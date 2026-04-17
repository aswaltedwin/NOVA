from crewai import Crew, Process, Task
from agents import NovaAgents
from tasks import NovaTasks
from config import Config
from textwrap import dedent

def run_nova_analysis_stage(log_input, model_name):
    """Stage 1: Parse and Analyze the intelligence signals."""
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    manager = agents.manager_agent()
    parser_agent = agents.log_parser_agent()
    analyzer_agent = agents.threat_analyzer_agent()

    crew = Crew(
        agents=[parser_agent, analyzer_agent],
        tasks=[
            tasks.parse_task(parser_agent, log_input),
            tasks.analyze_task(analyzer_agent)
        ],
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=True,
        memory=True,
        embedder=Config.get_embedder()
    )
    return crew.kickoff()

def run_nova_report_stage(analysis_results, model_name):
    """Stage 2: Synthesize findings into the final report."""
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    manager = agents.manager_agent()
    reporter_agent = agents.report_generator_agent()

    # Pass analysis results into the report task description
    report_task_desc = dedent(f"""
        Synthesize the following security analysis results into an executive report:
        ---
        {analysis_results}
        ---
    """)

    crew = Crew(
        agents=[reporter_agent],
        tasks=[
            Task(
                description=report_task_desc,
                expected_output="Final Markdown report for Phase 2 triage.",
                agent=reporter_agent
            )
        ],
        process=Process.sequential, # Simple synthesis
        verbose=True
    )
    return crew.kickoff()
