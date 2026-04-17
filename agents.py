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
            role="ParserAgent",
            goal="Normalize raw logs into structured JSON entities.",
            backstory="Security data engineer specializing in log normalization.",
            tools=[self.file_reader_tool],
            llm=self.llm,
        )

    def threat_analyzer_agent(self):
        return Agent(
            role="AnalyzerAgent",
            goal="Map anomalies to MITRE ATT&CK via RAG and score risk.",
            backstory="Threat researcher using MITRE and RAG context.",
            tools=[self.rag_search_tool, self.risk_calc_tool],
            llm=self.llm,
        )

    def report_generator_agent(self):
        return Agent(
            role="ReporterAgent",
            goal="Summarize findings into a clear Markdown triage report.",
            backstory="SOC Analyst focused on concise status reporting.",
            llm=self.llm,
        )

