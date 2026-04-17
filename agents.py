from crewai import Agent
from config import Config
from tools import RiskCalculatorTool, FileReaderTool
from response_tools import FirewallBlockTool, ProcessIsolationTool
from rag_tool import RAGSearchTool
from textwrap import dedent

class NovaAgents:
    def __init__(self, model_name=None):
        self.llm = Config.get_llm(model_name)
        self.risk_calc_tool = RiskCalculatorTool()
        self.file_reader_tool = FileReaderTool()
        self.rag_search_tool = RAGSearchTool()
        self.firewall_tool = FirewallBlockTool()
        self.process_tool = ProcessIsolationTool()

    def manager_agent(self):
        """Supervisor agent that coordinates missions and triggers active defense."""
        return Agent(
            role="NovaManager",
            goal="Oversee the end-to-end security mission, from triage to autonomous response recommendation.",
            backstory=dedent("""
                You are the autonomous supervisor of NOVA Phase 3.
                Your mission is to oversee the Parser, Analyzer, and Responder agents.
                If the calculated Risk Score is > 75, you MUST automatically delegate 
                a task to the ResponderAgent to identify containment actions.
                You maintain the 'State of Defense' across all mission stages.
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

    def responder_agent(self):
        """Action-oriented agent that generates containment and response recommendations."""
        return Agent(
            role="ResponderAgent",
            goal="Identify optimal containment actions and generate step-by-step response playbooks.",
            backstory=dedent("""
                You are an Incident Responder. You don't just find threats; you stop them.
                Given a threat analysis, you recommend specific, prioritized actions:
                - Block malicious IPs/Domains
                - Isolate or kill suspicious processes
                - Generate firewall rules
                - Create actionable remediation playbooks
                Always classify actions by risk (Safe, Medium, High).
            """),
            tools=[self.firewall_tool, self.process_tool],
            llm=self.llm,
        )

