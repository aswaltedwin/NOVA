from crewai import Task
from textwrap import dedent

class NovaTasks:
    def parse_task(self, agent, log_input):
        return Task(
            description=dedent(f"""
                Parse the following log data:
                ---
                {log_input}
                ---
                Instructions: Identify and extract all entities (IPs, users, actions, timestamps). 
                If the input is a file path, use the File Reader tool first.
            """),
            expected_output="Normalized JSON list of security events.",
            agent=agent
        )

    def analyze_task(self, agent):
        return Task(
            description=dedent("""
                Analyze the parsed events:
                1. RAG Search: Map anomalies to MITRE ATT&CK techniques.
                2. Risk: Calculate a score (0-100).
                3. Context: Check memory for repeat patterns.
            """),
            expected_output="Technical threat analysis with MITRE IDs and Risk Score.",
            agent=agent
        )

    def report_task(self, agent):
        return Task(
            description=dedent("""
                Generate the Final Sentinel Report:
                - Severity Badge & Summary
                - MITRE Context (RAG)
                - Risk Breakdown
                - Responder Recommendations (if high risk)
            """),
            expected_output="Final Markdown report for Phase 2 triage.",
            agent=agent
        )

    def recommendation_task(self, agent, threat_context):
        return Task(
            description=dedent(f"""
                Review the following threat analysis:
                ---
                {threat_context}
                ---
                Instructions:
                1. Identify the most critical entities (IPs, PIDs, domains).
                2. Use your tools to SIMULATE containment actions.
                3. Categorize actions by risk (Low/Medium/High).
                4. Generate a step-by-step remediation playbook.
            """),
            expected_output="A list of recommended response actions and a detailed playbook.",
            agent=agent
        )
