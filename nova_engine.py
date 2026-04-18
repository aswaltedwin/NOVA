from crewai import Crew, Process, Task
from agents import NovaAgents
from tasks import NovaTasks
from config import Config
from textwrap import dedent
import logging
import hashlib
import diskcache

logger = logging.getLogger("NOVA-Engine")
cache = diskcache.Cache(str(Config.BASE_DIR / ".nova_cache"))

def get_cache_key(log_input, model_name):
    """Generates a unique key for the analysis payload."""
    payload = f"{model_name}:{log_input}".encode('utf-8')
    return hashlib.md5(payload).hexdigest()

def run_nova_analysis_stage(log_input, model_name, vision_results=None):
    """Stage 1: Parse and Analyze the intelligence signals with caching."""
    
    # Prepend vision if exists
    if vision_results:
        log_input = f"--- VISUAL INTELLIGENCE REPORT ---\n{vision_results}\n\n--- RAW TELEMETRY ---\n{log_input}"

    # Check Cache
    cache_key = get_cache_key(log_input, model_name)
    if cache_key in cache:
        logger.info("Found analysis results in local cache. Retrieving...")
        return cache[cache_key]

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
    
    logger.info("Kickoff: NOVA Analysis Stage")
    result = crew.kickoff()
    
    # Store in Cache
    cache[cache_key] = str(result)
    return result


def run_nova_report_stage(analysis_results, model_name):
    """Stage 2: Synthesize findings into the final report."""
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    reporter_agent = agents.report_generator_agent()

    # Pass analysis results into the report task description
    report_task_desc = dedent(f"""
        Synthesize the following security analysis results into an executive report.
        Focus on identifying the 'Critical Path' of the attack and recommending containment.
        ---
        {analysis_results}
        ---
    """)

    crew = Crew(
        agents=[reporter_agent],
        tasks=[
            Task(
                description=report_task_desc,
                expected_output="Final Markdown report for Phase 3 triage with actionable containment steps.",
                agent=reporter_agent
            )
        ],
        process=Process.sequential, 
        verbose=True
    )
    
    logger.info("Kickoff: NOVA Reporting Stage")
    return crew.kickoff()

def run_nova_response_stage(analysis_results, model_name):
    """Stage 1.5: Generate active response recommendations based on analysis."""
    agents = NovaAgents(model_name)
    tasks = NovaTasks()
    
    manager = agents.manager_agent()
    responder = agents.responder_agent()

    crew = Crew(
        agents=[responder],
        tasks=[tasks.recommendation_task(responder, analysis_results)],
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=True
    )
    
    logger.info("Kickoff: NOVA Response Stage")
    return crew.kickoff()

def run_nova_vision_stage(image_path, model_name="llama3.2-vision"):
    """Multi-modal stage: Analyze security screenshots via Llama-Vision."""
    from vision_tool import ScreenshotAnalyzerTool
    logger.info(f"Kickoff: NOVA Vision Stage for {image_path}")
    vision_tool = ScreenshotAnalyzerTool()
    
    # We run the tool directly for faster turnaround in the single-image pipeline
    try:
        return vision_tool._run(image_path)
    except Exception as e:
        logger.error(f"Vision Tool failed: {e}")
        return f"Error analyzing screenshot: {str(e)}"
