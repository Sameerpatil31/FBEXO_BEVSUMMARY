"""
Operational-Assessment generator (no Streamlit, one self-contained class).
--------------------------------------------------------------------------

Dependences already existing in your project:

• src.db.sql_operation.fetch_query
• src.db.sql_operation.execute_query
• openai.AzureOpenAI  (azure-openai Python SDK)
• python-dotenv       (for .env)

Put this file anywhere inside your repo and import / call as needed.
"""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import text
from src.BEV_Details.sql_db_operation import execute_query, fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import random

import json


class OperationalAssessmentTool:
    """
    End-to-end generator for MBB-style Operational Assessment reports.
    Usage (programmatic):
        oa = OperationalAssessmentTool()
        report = oa.generate(
            phase="Section 2",
            task="Task 5",
            industry_context="Pharmaceutical",
        )
        print(report)
    """

    # ---------------- constructor -------------------------------------------
    def __init__(self, db_row_id: int = 1) -> None:
        # load_dotenv()                              # read .env once
        self.db_row_id = db_row_id                 # prompt row in DB

        # Azure OpenAI client
        # self.client = AzureOpenAIClient(
        #     azure_endpoint=os.getenv("ENDPOINT_URL"),
        #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     api_version="2025-01-01-preview"
        # )
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

        # Phase / Task definitions
        self.phases = {
            "Section 1": {
                "name": "Business Process Analysis",
                "tasks": {
                    "Task 1": "Identify and Document Key Operational Workflows",
                    "Task 2": "Create Process Flow Diagrams"
                }
            },
            "Section 2": {
                "name": "Supply Chain Analysis",
                "tasks": {
                    "Task 3": "Analyze Supply Chain Structure",
                    "Task 4": "Map the Supply Chain",
                    "Task 5": "Assess Supply Chain Risks and Vulnerabilities"
                }
            },
            "Section 3": {
                "name": "Performance Assessment and Benchmarking",
                "tasks": {
                    "Task 6": "Identify Key Operational Performance Indicators (KPIs)",
                    "Task 7": "Benchmark Performance"
                }
            },
            "Section 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 8": "Synthesize Findings and Identify Strategic Operational Moves",
                    "Task 9": "Create Operational Assessment Report"
                }
            }
        }

        # DB column names holding prompts
        self.db_column = {
            "Section 1": "OAT_Section_1",
            "Section 2": "OAT_Section_2",
            "Section 3": "OAT_Section_3",
            "Section 4": "OAT_Section_4"
        }

    # ---------------- public API --------------------------------------------
    def generate(
        self,
        phase: str,
        task: str,
        *,
        industry_context: str = "",
        prompt_override: Optional[str] = None,
        persist_override: bool = False,
        save_to_file: bool = True
    ) -> str:
        """
        Returns the generated assessment as a string.

        Parameters
        ----------
        phase : one of "Section 1" … "Section 4"
        task  : one of the tasks inside that phase
        industry_context : optional string passed to the LLM
        prompt_override  : if supplied, use this prompt instead of DB value
        persist_override : when True, writes prompt_override back to DB
        save_to_file     : when True, writes the analysis to a txt file

        Raises
        ------
        ValueError if invalid phase / task supplied.
        """

        self._validate_phase_task(phase, task)

        # 1 ─ fetch prompt
        prompt = (
            prompt_override
            if prompt_override is not None
            else self._fetch_prompt_from_db(self.db_column[phase])
        )

        if prompt is None:
            prompt = self._default_prompt(phase, task)

        # 2 ─ optionally persist prompt_override
        if prompt_override is not None and persist_override:
            self._update_prompt_in_db(self.db_column[phase], prompt_override)

        # 3 ─ generate report through Azure OpenAI
        analysis = self._call_openai(prompt, phase, task, industry_context)

        # 4 ─ persist to file
        if save_to_file:
            self._save_to_disk(phase, task, analysis)

        return analysis

    def generate_report(self):
        """Automated method for pipeline - generates default operational assessment."""
        # Use default values for automated generation
        default_phase = "Section 1"
        default_task = "Task 1"
        default_industry = "General"
        
        return self.generate(
            phase=default_phase,
            task=default_task,
            industry_context=default_industry,
            save_to_file=False
        )

    # ---------------- internal helpers --------------------------------------
    def _validate_phase_task(self, phase: str, task: str) -> None:
        if phase not in self.phases:
            raise ValueError(f"Unknown phase: {phase}")
        if task not in self.phases[phase]["tasks"]:
            raise ValueError(f"Task '{task}' not part of {phase}")

    # ── DB helpers
    def _fetch_prompt_from_db(self, column: str) -> Optional[str]:
        q = text(f"SELECT [{column}] FROM prompt_valuation_reports WHERE id = :id")
        res = fetch_query(q, {"id": self.db_row_id})
        return res[0][column] if res else None

    def _update_prompt_in_db(self, column: str, prompt: str) -> None:
        upd = text(f"""
            UPDATE prompt_valuation_reports
            SET [{column}] = :prompt
            WHERE id = :id
        """)
        execute_query(upd, {"prompt": prompt, "id": self.db_row_id})

    # ── OpenAI call
    def _call_openai(
        self,
        prompt: str,
        phase: str,
        task: str,
        industry_context: str
    ) -> str:
        user_prompt = (
            f"As an MBB consultant specializing in Operational Assessment, analyse the following:\n"
            f"\nSection: {phase}\nTask: {task}\nIndustry Context: {industry_context}\n\n"
            f"Specific Instructions:\n{prompt}\n\n"
            "Provide a detailed analysis following MBB consulting standards with actionable, data-driven recommendations."
        )

        messages = [
            {
                "role": "system",
                "content": "You are an experienced MBB consultant specializing in operational strategy."
            },
            {"role": "user", "content": user_prompt}
        ]

        try:
            resp = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),
                messages=messages,
                temperature=0.7
            )
            return resp.choices[0].message.content
        except Exception as exc:
            return f"ERROR calling Azure OpenAI: {exc}"

    # ── Disk persistence
    def _save_to_disk(self, phase: str, task: str, analysis: str) -> None:
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"operational_analysis_{ts}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"Timestamp (UTC): {ts}\nPhase: {phase}\nTask: {task}\n\n{analysis}")
        print(f"📄 Report saved to {fname}")

    # ── Fallback prompt
    @staticmethod
    def _default_prompt(phase: str, task: str) -> str:
        return (
            f"Conduct a thorough analysis for {phase} – {task}.\n\n"
            "Consider the following aspects:\n"
            "1. Current state assessment\n"
            "2. Key challenges and opportunities\n"
            "3. Industry best practices and benchmarks\n"
            "4. Specific recommendations\n"
            "5. Implementation considerations\n\n"
            "Provide detailed insights and actionable recommendations focusing on operational excellence."
        )


# --------------------------- minimal CLI driver -----------------------------
if __name__ == "__main__":
    # Simple interactive usage when run directly
    oa = OperationalAssessmentTool()

    # choose phase
    print("\nPHASES:")
    for idx, p in enumerate(oa.phases, 1):
        print(f"{idx}. {p} – {oa.phases[p]['name']}")
    phase_idx = int(input("Select phase (1-4): "))
    phase = list(oa.phases)[phase_idx - 1]

    # choose task
    print(f"\nTASKS ({phase}):")
    for idx, t in enumerate(oa.phases[phase]["tasks"], 1):
        print(f"{idx}. {t} – {oa.phases[phase]['tasks'][t]}")
    task_idx = int(input("Select task: "))
    task = list(oa.phases[phase]["tasks"])[task_idx - 1]

    # optional industry context
    industry = input("Industry context (optional): ")

    # generate report
    print("\nGenerating report, please wait …\n")
    report = oa.generate(phase, task, industry_context=industry)
    print("\n========== GENERATED ANALYSIS ==========\n")
    print(report)
