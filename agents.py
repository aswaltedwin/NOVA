from crewai import Agent
from config import Config
from tools import RiskCalculatorTool, FileReaderTool
from rag_tool import RAGSearchTool

class NovaAgents:
    def __init__(self, model_name=None):
        self.llm = Config.get_llm(model_name)
        self.risk_calc_tool = RiskCalculatorTool()
        self.file_reader_tool = FileReaderTool()
        self.rag_search_tool = RAGSearchTool()

    def log_parser_agent(self):
        return Agent(
            role="LogParserAgent",
            goal="Parse and normalize raw security logs into structured JSON data.",
            backstory="Experienced in log architecture, regex, and extracting entities from raw cybersecurity telemetry.",
            tools=[self.file_reader_tool],
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def threat_analyzer_agent(self):
        return Agent(
            role="ThreatAnalyzerAgent",
            goal="Analyze security threats, map them to MITRE ATT&CK using RAG, and calculate risk scores.",
            backstory="Senior Threat Hunter with deep expertise in adversary TTPs. Always use the RAG Search Tool to verify technical IDs.",
            tools=[self.rag_search_tool, self.risk_calc_tool],
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def report_generator_agent(self):
        return Agent(
            role="ReportGeneratorAgent",
            goal="Create clear, actionable, and human-readable triage reports with executive summaries.",
            backstory="Expert SOC Analyst and technical writer focused on incident response communication.",
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def nova_manager(self):
        return Agent(
            role="NovaManager",
            goal="Orchestrate the entire cyber triage lifecycle, resolve agent conflicts, and ensure final report quality.",
            backstory="Advanced AI supervisor coordinating specialized security agents for high-fidelity threat intelligence. You review all agent outputs and make the final call.",
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=True
        )
