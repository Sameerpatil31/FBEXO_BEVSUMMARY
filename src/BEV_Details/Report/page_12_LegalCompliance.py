"""
Batch generator – Legal & Compliance Assessment.
Runs all phases & tasks in one go and saves a master result file.

> python legal_compliance_batch.py
"""

from __future__ import annotations
import os
from datetime import datetime
from src.LLM.azure_openai import AzureOpenAIClient
from typing import Dict
from pathlib import Path


class LegalComplianceAssessmentTool:
    """Single-class implementation with batch capability."""

    # ─── constructor ────────────────────────────────────────────────────
    def __init__(self, db_row_id: int = 1) -> None:
        self.db_row_id = db_row_id
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

        # Phase / Task map
        self.phases: Dict[str, Dict] = {
            "Phase 1": {
                "name": "Corporate Governance",
                "tasks": {"Task 1": "Analyze Corporate Governance Structure"},
            },
            "Phase 2": {
                "name": "Regulatory Compliance",
                "tasks": {"Task 2": "Assess Regulatory Compliance"},
            },
            "Phase 3": {
                "name": "Litigation History and Legal Risks",
                "tasks": {"Task 3": "Analyze Litigation History and Legal Risks"},
            },
            "Phase 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 4": "Synthesize Findings and Identify Key Issues",
                    "Task 5": "Develop Questions for Leadership",
                    "Task 6": "Create Legal and Compliance Assessment Report",
                },
            },
        }

    def get_default_prompt(self, phase, task):
        """Get default prompt template based on phase and task."""
        prompts = {
            "Phase 1": {
                "Task 1": """
                Analyze the corporate governance structure focusing on:
                1. Board composition and independence
                2. Key committees and their effectiveness
                3. Management team assessment
                4. Governance policies and practices
                5. Regulatory compliance in corporate governance
                
                Provide specific insights and recommendations.
                """
            },
            "Phase 2": {
                "Task 2": """
                Assess regulatory compliance in the following areas:
                1. Industry-specific regulations
                2. Environmental, Health, and Safety (EHS)
                3. Data Privacy and Cybersecurity
                4. Anti-corruption and Anti-bribery
                5. International Trade
                
                Identify compliance gaps and recommend improvements.
                """
            },
            "Phase 3": {
                "Task 3": """
                Analyze litigation history and legal risks:
                1. Current pending litigation
                2. Historical legal issues
                3. Potential future risks
                4. Risk management approach
                5. Legal department assessment
                
                Provide risk assessment and mitigation strategies.
                """
            },
            "Phase 4": {
                "Task 4": """
                Synthesize key findings focusing on:
                1. Material non-compliance issues
                2. Significant litigation risks
                3. Governance weaknesses
                4. Emerging legal risks
                
                Prioritize issues by potential impact.
                """,
                "Task 5": """
                Develop targeted questions for leadership:
                1. Understanding of key issues
                2. Risk mitigation plans
                3. Financial impact assessment
                4. Operational implications
                
                Format questions for maximum clarity and insight.
                """,
                "Task 6": """
                Create comprehensive assessment report including:
                1. Executive summary
                2. Governance assessment
                3. Compliance review
                4. Litigation analysis
                5. Key issues and questions
                
                Follow MBB report structure and formatting.
                """
            }
        }
        return prompts.get(phase, {}).get(task, "Conduct thorough analysis for the selected phase and task.")

    # ─── PUBLIC API ─────────────────────────────────────────────────────
    def generate(
        self,
        *,
        phase: str,
        task: str,
        company_type: str,
        prompt_override: str | None = None,
    ) -> str:
        """Generate analysis for a single phase/task; returns the text."""
        self._check_phase_task(phase, task)

        # Use prompt_override if provided, otherwise use default prompt
        prompt = prompt_override if prompt_override is not None else self.get_default_prompt(phase, task)

        return self._ask_chatgpt(prompt, phase, task, company_type)

    def generate_all(
        self,
        company_type: str = "Public Company",
        save_individual: bool = False,
    ) -> Dict[str, Dict[str, str]]:
        """
        Loop through *all* phase/task pairs and return a nested dict
        {phase -> {task -> analysis}}

        If save_individual=True each answer is also written to its own txt file.
        A combined master file is always written.
        """
        results: Dict[str, Dict[str, str]] = {}
        for phase, pinfo in self.phases.items():
            results[phase] = {}
            for task in pinfo["tasks"]:
                print(f"▶ Generating {phase} / {task} …")
                analysis = self.generate(
                    phase=phase,
                    task=task,
                    company_type=company_type,
                )
                results[phase][task] = analysis

                if save_individual:
                    self._write_text_file(
                        content=analysis,
                        suffix=f"{phase}_{task}".replace(" ", "_"),
                    )

        # Master file combining everything
        master_text = self._combine_results(results, company_type)
        self._write_text_file(master_text, suffix="ALL")

        print("✔ All phases & tasks completed.")
        return results

    # ─── INTERNAL UTILS ─────────────────────────────────────────────────
    def _ask_chatgpt(
        self, prompt: str, phase: str, task: str, company_type: str
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an experienced MBB consultant specialising in "
                    "legal and compliance assessment."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"As an MBB consultant, analyse the following:\n\n"
                    f"Phase: {phase}\nTask: {task}\nCompany Type: {company_type}\n\n"
                    f"Specific Instructions:\n{prompt}\n\n"
                    "Provide a detailed assessment with legal-risk insight, "
                    "compliance gaps and actionable recommendations."
                ),
            },
        ]

        try:
            resp = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),
                messages=messages,
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as exc:
            return f"ERROR contacting Azure OpenAI: {exc}"

    # ─── DB helpers (removed - using default prompts instead)
    
    # ─── Misc helpers
    @staticmethod
    def _combine_results(res: Dict, company_type: str) -> str:
        parts = []
        for phase in res:
            for task in res[phase]:
                header = (
                    f"Phase: {phase}  |  Task: {task}  |  Company Type: {company_type}"
                )
                parts.append(header)
                parts.append("-" * len(header))
                parts.append(res[phase][task])
                parts.append("\n")
        return "\n\n".join(parts)

    @staticmethod
    def _write_text_file(content: str, suffix: str) -> None:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"legal_compliance_{suffix}_{ts}.txt"
        Path(fname).write_text(content, encoding="utf-8")
        print(f"  ⤵  saved to {fname}")

    def _check_phase_task(self, phase: str, task: str) -> None:
        if phase not in self.phases:
            raise ValueError(f"Unknown phase {phase}")
        if task not in self.phases[phase]["tasks"]:
            raise ValueError(f"Unknown task {task} for {phase}")


# ─── MAIN (no interaction required) ──────────────────────────────────────
if __name__ == "__main__":
    # Company type can be hard-wired here or taken from env/CLI; modify as needed.
    COMPANY_TYPE = os.getenv("COMPANY_TYPE", "Public Company")

    tool = LegalComplianceAssessmentTool()
    tool.generate_all(
        company_type=COMPANY_TYPE,
        save_individual=False,   # change to True if you also want per-task files
    )
