from crewai import Task
from textwrap import dedent

class NovaTasks:
    def parse_task(self, agent, log_input):
        return Task(
            description=f"Analyze and parse this log input: {log_input}. If it points to an external file, use your File Reader tool.",
            expected_output="Structured JSON of entities (IPs, users, actions) found in the log.",
            agent=agent
        )

    def analyze_task(self, agent):
        return Task(
            description=dedent("""
                1. Take the parsed log entities and perform a RAG Search for matching MITRE ATT&CK techniques.
                2. Identify the likely Attack Vector (e.g., Initial Access, Persistence).
                3. Calculate the Risk Score (0-100) based on severity and confidence.
                4. Incorporate previous memory results if a similar attack was seen before.
                5. Detail your reasoning step-by-step.
            """),
            expected_output="A deep threat analysis including technical IDs (e.g. T1566) and a contextual risk score.",
            agent=agent
        )

    def report_task(self, agent):
        return Task(
            description=dedent("""
                Synthesize all agent findings and tool results into the Final Sentinel Report.
                The report must be executive-grade and include:
                - Threat Summary with Severity Badge
                - RAG-Augmented MITRE Context
                - Detailed Risk Breakdown
                - Persistence & Memory Context (if applicable)
                - Technical Recommendations for Remediation
            """),
            expected_output="A professional, structured Markdown report representing the definitive Phase 2 triage.",
            agent=agent
        )
