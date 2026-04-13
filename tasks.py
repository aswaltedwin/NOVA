from crewai import Task
from textwrap import dedent

class NovaTasks:
    def parse_task(self, agent, log_input):
        return Task(
            description=f"Parse this log into clean JSON structure, extracting IP, User, and Action: {log_input}",
            expected_output="Structured JSON data containing extracted security metadata.",
            agent=agent
        )

    def analyze_task(self, agent):
        return Task(
            description=dedent("""
                Analyze the provided log JSON data for security threats.
                1. Identify potential malicious patterns.
                2. Map the behavior to MITRE ATT&CK techniques.
                3. Calculate a risk score (0-100) using your tool (Severity and Confidence).
                4. Explain your expert reasoning (Chain of Thought).
            """),
            expected_output="Detailed threat analysis including risk score, MITRE mappings, and reasoning.",
            agent=agent
        )

    def report_task(self, agent):
        return Task(
            description=dedent("""
                Generate a final human-readable Security Triage Report.
                The report must include:
                - Executive Summary (Severity Badge)
                - Technical Breakdown (Entities, Mappings)
                - Risk Analysis (Score & Reasoning)
                - Recommendations (Remediation steps)
                Output final report as professional Markdown.
            """),
            expected_output="A polished, executive-level security triage report in Markdown format.",
            agent=agent
        )
