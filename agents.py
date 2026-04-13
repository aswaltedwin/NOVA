from crewai import Agent
from config import Config
from tools import RiskCalculatorTool, LogParserTool

class NovaAgents:
    def __init__(self, model_name=None):
        self.llm = Config.get_llm(model_name)
        self.risk_calc_tool = RiskCalculatorTool()
        self.log_parser_tool = LogParserTool()

    def log_parser_agent(self):
        return Agent(
            role="LogParserAgent",
            goal="Parse and normalize raw security logs into structured JSON data.",
            backstory="Experienced in log architecture, regex, and extracting entities from raw cybersecurity telemetry.",
            tools=[self.log_parser_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def threat_analyzer_agent(self):
        return Agent(
            role="ThreatAnalyzerAgent",
            goal="Analyze security threats, map them to MITRE ATT&CK, and calculate risk scores.",
            backstory="Senior Threat Hunter with deep expertise in adversary TTPs (Tactics, Techniques, and Procedures).",
            tools=[self.risk_calc_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def report_generator_agent(self):
        return Agent(
            role="ReportGeneratorAgent",
            goal="Create clear, actionable, and human-readable triage reports with executive summaries.",
            backstory="Expert SOC Analyst and technical writer focused on incident response communication.",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def nova_manager(self):
        return Agent(
            role="NovaManager",
            goal="Orchestrate the entire cyber triage lifecycle and ensure final report quality.",
            backstory="Advanced AI supervisor coordinating specialized security agents for high-fidelity threat intelligence.",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
