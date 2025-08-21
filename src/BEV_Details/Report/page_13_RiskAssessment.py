"""
Batch generator for MBB-Style Operational Assessment
Generates ALL phases & tasks for a chosen industry in one run.
No Streamlit. Just run: python operational_assessment_batch.py
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict
# from __future__ import annotations
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import text
from src.BEV_Details.sql_db_operation import execute_query, fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import random
from typing import Dict
import json
from pathlib import Path
from sqlalchemy import text
from dotenv import load_dotenv

# If DB prompts were required
# from src.db.sql_operation import execute_query  # Optional if updating DB

load_dotenv()


class RiskAssessmentTool:
    def __init__(self):
        # Azure OpenAI
        # self.client = AzureOpenAIClient(
        #     azure_endpoint=os.getenv("ENDPOINT_URL"),
        #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     api_version="2025-01-01-preview",
        # )
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()
        self.model_name = os.getenv("DEPLOYMENT_NAME")

        # Phase/task mappings from your original code
        self.phases = {
            "Phase 1": {
                "name": "Business Process Analysis",
                "tasks": {
                    "Task 1": "Identify and Document Key Operational Workflows",
                    "Task 2": "Create Process Flow Diagrams"
                }
            },
            "Phase 2": {
                "name": "Supply Chain Analysis",
                "tasks": {
                    "Task 3": "Analyze Supply Chain Structure",
                    "Task 4": "Map the Supply Chain",
                    "Task 5": "Assess Supply Chain Risks and Vulnerabilities"
                }
            },
            "Phase 3": {
                "name": "Performance Assessment and Benchmarking",
                "tasks": {
                    "Task 6": "Identify Key Operational Performance Indicators (KPIs)",
                    "Task 7": "Benchmark Performance"
                }
            },
            "Phase 4": {
                "name": "Synthesis and Output",
                "tasks": {
                    "Task 8": "Synthesize Findings and Identify Strategic Operational Moves",
                    "Task 9": "Create Operational Assessment Report"
                }
            }
        }

    # === INDUSTRY-SPECIFIC PROMPT BUILDER ===
    def get_default_prompt(self, phase: str, task: str, industry_type="Manufacturing") -> str:
        """Returns default industry-aware prompt (your original definition simplified here)."""
        # Keep your original detailed mapping for tasks exactly —
        # due to size, we omit here, but in your real code paste the full prompts dictionary.
        # For demonstration:
        prompts = {
            "Task 1": f"Analyze workflows for {industry_type}",
            "Task 2": f"Create process flow diagrams for {industry_type}",
            "Task 3": f"Analyze supply chain for {industry_type}",
            "Task 4": f"Map supply chain for {industry_type}",
            "Task 5": f"Assess supply chain risks for {industry_type}",
            "Task 6": f"Identify KPIs for {industry_type}",
            "Task 7": f"Benchmark KPIs for {industry_type}",
            "Task 8": f"Synthesize findings for {industry_type}",
            "Task 9": f"Create operational assessment report for {industry_type}",
        }
        return prompts.get(task, f"Conduct assessment for {phase} - {task} in {industry_type}")

    def generate_analysis(self, prompt: str, phase: str, task: str, industry_type: str) -> str:
        """Calls Azure OpenAI with system + user messages."""
        system_message = (
            f"You are a senior MBB consultant specializing in {industry_type} operational strategy. "
            f"Provide structured, data-driven insights and recommendations."
        )
        user_message = (
            f"Phase: {phase} - {self.phases[phase]['name']}\n"
            f"Task: {task} - {self.phases[phase]['tasks'][task]}\n"
            f"Industry: {industry_type}\n"
            f"Instructions:\n{prompt}"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"ERROR: {e}"

    # === MAIN LOOP ===
    def generate_all(self, industry_type="Manufacturing", save_individual=False) -> Dict[str, Dict[str, str]]:
        results: Dict[str, Dict[str, str]] = {}
        for phase, pdata in self.phases.items():
            results[phase] = {}
            for task in pdata["tasks"]:
                print(f"▶ Generating: {phase} | {task} | Industry: {industry_type}")
                prompt = self.get_default_prompt(phase, task, industry_type)
                analysis = self.generate_analysis(prompt, phase, task, industry_type)
                results[phase][task] = analysis

                if save_individual:
                    self._write_to_file(
                        f"{phase}_{task}_{industry_type}",
                        self._format_entry(phase, task, industry_type, prompt, analysis)
                    )

        # Save master combined file
        master_text = self._combine_results(results, industry_type)
        self._write_to_file(f"ALL_{industry_type}", master_text)
        return results

    def _format_entry(self, phase, task, industry_type, prompt, analysis) -> str:
        return (
            f"Phase: {phase} - {self.phases[phase]['name']}\n"
            f"Task: {task} - {self.phases[phase]['tasks'][task]}\n"
            f"Industry: {industry_type}\n"
            f"Prompt:\n{prompt}\n\n"
            f"Analysis:\n{analysis}\n"
        )

    def _combine_results(self, results: Dict[str, Dict[str, str]], industry_type: str) -> str:
        parts = []
        for phase in results:
            for task in results[phase]:
                entry = self._format_entry(
                    phase, task,
                    industry_type,
                    self.get_default_prompt(phase, task, industry_type),
                    results[phase][task]
                )
                parts.append(entry)
        return "\n" + ("=" * 80 + "\n").join(parts)

    def _write_to_file(self, name: str, content: str):
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"operational_assessment_{name}_{ts}.txt"
        Path(fname).write_text(content, encoding="utf-8")
        print(f"💾 Saved: {fname}")


if __name__ == "__main__":
    tool = RiskAssessmentTool()
    # Change industry_type as needed:
    result_ = tool.generate_all(industry_type="Technology", save_individual=False)
    print("✅ All phases and tasks generated successfully.")
    print(result_)
