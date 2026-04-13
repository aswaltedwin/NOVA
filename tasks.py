from crewai import Task
from textwrap import dedent

class NovaTasks:
    def parse_task(self, agent, log_input):
        return Task(
            description=dedent(f"""
                Parse the following raw security log and extract all relevant entities (IPs, users, actions).
                Log: {log_input}
                Normalize the data for the Threat Analyzer.
            """),
            expected_output="A structured JSON-like normalization of the log containing entities and metadata.",
            agent=agent
        )

    def analyze_task(self, agent):
        return Task(
            description=dedent("""
                Using the parsed log data, identify common malicious patterns.
                1. Map findings to MITRE ATT&CK techniques (e.g., T1071.001 - Web Protocols).
                2. Calculate a risk score using your tool (Severity, Confidence, Impact).
                3. Explain your reasoning in detail (Chain of Thought).
            """),
            expected_output="An in-depth analysis report including MITRE tags, risk score, and detailed reasoning.",
            agent=agent
        )

    def report_task(self, agent):
        return Task(
            description=dedent("""
                Synthesize all prior agent insights into a final NOVA Security Report.
                The report must include:
                - Executive Summary (High/Medium/Low risk badge)
                - Technical Breakdown (Entities, Patterns, MITRE mappings)
                - Risk Score & Explanation
                - Actionable Recommendations (Remediation steps)
                Format the final output as clean Markdown.
            """),
            expected_output="A complete, professional Markdown document for initial cyber threat triage.",
            agent=agent
        )
