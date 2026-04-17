from crewai import Agent
from config import Config
from tools import RiskCalculatorTool, FileReaderTool
from rag_tool import RAGSearchTool
from textwrap import dedent

class NovaAgents:
    def __init__(self, model_name=None):
        self.llm = Config.get_llm(model_name)
        self.risk_calc_tool = RiskCalculatorTool()
        self.file_reader_tool = FileReaderTool()
        self.rag_search_tool = RAGSearchTool()

    def manager_agent(self):
        """Supervisor agent that coordinates the mission and adds memory context."""
        return Agent(
            role="NovaManager",
            goal="Coordinate the security triage mission and ensure transparent, multi-agent collaboration.",
            backstory=dedent("""
                You are the autonomous supervisor of the NOVA Sentinel Command Center.
                Your mission is to oversee the Parser, Analyzer, and Reporter agents.
                You ensure that findings are mapped to MITRE ATT&CK and that long-term memory 
                is consulted to detect cross-session patterns.
            """),
            allow_delegation=True,
            llm=self.llm
        )

    def log_parser_agent(self):
        return Agent(
            role="ParserAgent",
            goal="Normalize raw logs into structured JSON entities for high-fidelity analysis.",
            backstory="Security data engineer specializing in high-speed log normalization and noise reduction.",
            tools=[self.file_reader_tool],
            llm=self.llm,
        )

    def threat_analyzer_agent(self):
        return Agent(
            role="AnalyzerAgent",
            goal="Map anomalies to MITRE ATT&CK via RAG and score risk with full transparency.",
            backstory="Threat researcher focused on identifying attack chains and mapping signals to MITRE tactics.",
            tools=[self.rag_search_tool, self.risk_calc_tool],
            llm=self.llm,
        )

    def report_generator_agent(self):
        return Agent(
            role="ReporterAgent",
            goal="Synthesize agent findings into an executive-grade triage report.",
            backstory="Professional SOC Analyst specialized in concise, evidence-based reporting.",
            llm=self.llm,
        )

