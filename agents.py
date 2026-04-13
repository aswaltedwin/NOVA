from crewai import Agent
from config import Config
from tools import LogParserTool, RiskScorerTool

class NovaAgents:
    def __init__(self, model_name=None):
        self.llm = Config.get_llm(model_name)
        self.log_parser_tool = LogParserTool()
        self.risk_scorer_tool = RiskScorerTool()

    def log_parser_agent(self):
        return Agent(
            role='Security Data Architect',
            goal='Accurately parse and normalize raw security logs into structured JSON entities.',
            backstory='Expert in pattern matching and regex-based data extraction for diverse log sources like Syslog, Windows Event, and EDR logs.',
            tools=[self.log_parser_tool],
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def threat_analyzer_agent(self):
        return Agent(
            role='Senior Threat Intel Hunter',
            goal='Identify malicious patterns, map to MITRE ATT&CK techniques, and assess threat impact.',
            backstory='Veteran security researcher with deep knowledge of adversary behavior, C2 infrastructure, and data exfiltration techniques.',
            tools=[self.risk_scorer_tool],
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def report_generator_agent(self):
        return Agent(
            role='Incident Response Coordinator',
            goal='Synthesize agent findings into clear, actionable executive and technical reports.',
            backstory='Technical communication expert who bridges the gap between raw data analysis and strategic decision-making.',
            tools=[],
            llm=self.llm,
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def manager_agent(self):
        """The NovaManager supervisor coordinating the entire operation."""
        return Agent(
            role='NOVA System Manager',
            goal='Supervise the cyber triage crew, resolve conflicting findings, and ensure report quality.',
            backstory='An ultra-reliable manager that orchestrates tasks with military precision and maintains a global view of the threat landscape.',
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
