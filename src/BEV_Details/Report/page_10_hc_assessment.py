"""
Automated Human Capital Assessment generator for BEV report pipeline.
"""

from sqlalchemy import text
from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import os


class HumanCapitalAssessment:
    """End-to-end generator for MBB-style Human Capital reports."""

    def __init__(self, report_data=None):
        self.report_data = report_data or {}
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

    def fetch_hc_prompt(self, section="Section 1"):
        """Fetch the human capital assessment prompt from database based on section."""
        try:
            # Default prompt template
            default_prompt = """
            Conduct a thorough analysis for the selected phase and task.
            Consider the following aspects:
            1. Current state assessment
            2. Key challenges and opportunities
            3. Industry benchmarks and best practices
            4. Specific recommendations
            5. Implementation considerations
            
            Please provide detailed insights and actionable recommendations.
            """
            
            # Map section to database column
            HCA_Section_1 = ""
            
            if section == "Section 1":
                HCA_Section_1 = "HCA_Section_1"
            elif section == "Section 2":
                HCA_Section_1 = "HCA_Section_2"
            elif section == "Section 3":
                HCA_Section_1 = "HCA_Section_3"
            elif section == "Section 4":
                HCA_Section_1 = "HCA_Section_4"
            else:
                HCA_Section_1 = "HCA_Section_1"  # Default to Section 1

            query = text(f"SELECT [{HCA_Section_1}] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            
            if result and result[0][HCA_Section_1]:
                return result[0][HCA_Section_1]
            else:
                logger.warning(f"No data found for {section}, using default prompt.")
                return default_prompt
                
        except Exception as e:
            logger.error(f"Error fetching HC assessment prompt for {section}: {e}")
            return default_prompt

    def generate_analysis_for_section(self, section: str) -> str:
        """Generate human capital analysis for a specific section using Azure OpenAI."""
        prompt = self.fetch_hc_prompt(section)
        
        messages = [
            {
                "role": "system",
                "content": "You are an experienced MBB consultant specializing in human capital strategy."
            },
            {
                "role": "user",
                "content": f"Section: {section}\n\nInstructions: {prompt}\n\nCompany Data: {self.report_data}"
            }
        ]
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating HC analysis for {section}: {e}")
            return f"Error generating analysis for {section}: {e}"

    def generate_comprehensive_report(self):
        """Generate comprehensive HC assessment report covering all sections."""
        sections = ["Section 1", "Section 2", "Section 3", "Section 4"]
        section_titles = {
            "Section 1": "Organizational Structure and Workforce Analysis",
            "Section 2": "Compensation, Benefits, and Talent Development", 
            "Section 3": "Human Capital Risks and Strategic Alignment",
            "Section 4": "Synthesis and Output"
        }
        
        comprehensive_report = "# Human Capital Assessment - Comprehensive Report\n\n"
        
        for section in sections:
            try:
                logger.info(f"Generating {section}: {section_titles[section]}")
                section_analysis = self.generate_analysis_for_section(section)
                
                comprehensive_report += f"## {section}: {section_titles[section]}\n\n"
                comprehensive_report += section_analysis + "\n\n"
                comprehensive_report += "---\n\n"
                
            except Exception as e:
                logger.error(f"Error generating {section}: {e}")
                comprehensive_report += f"## {section}: {section_titles[section]}\n\n"
                comprehensive_report += f"Error generating this section: {e}\n\n"
                comprehensive_report += "---\n\n"
        
        return comprehensive_report

    def generate_single_section_report(self, section="Section 1"):
        """Generate report for a single HC assessment section."""
        try:
            logger.info(f"Generating single section report for {section}")
            return self.generate_analysis_for_section(section)
        except Exception as e:
            logger.error(f"Failed to generate {section} report: {e}")
            return f"Error generating {section} report: {e}"

    def generate_report(self):
        """Main method called by the pipeline to generate the comprehensive HC assessment report."""
        try:
            logger.info("Starting comprehensive Human Capital Assessment report generation")
            return self.generate_comprehensive_report()
        except Exception as e:
            logger.error(f"Failed to generate HC assessment report: {e}")
            return {"error": f"Failed to generate HC assessment report: {e}"}
