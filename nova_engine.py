from crewai import Crew, Process
from agents import NovaAgents
from tasks import NovaTasks
from config import Config

def run_nova_sentinel(log_input, model_name):
    """Core logic to run the NOVA Sentinel agents."""
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
        memory=True,
        embedder=Config.get_embedder()
    )

    return crew.kickoff()
