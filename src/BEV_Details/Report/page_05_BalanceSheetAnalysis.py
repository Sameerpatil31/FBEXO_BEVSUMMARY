from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
from sqlalchemy import text
import os
import json



class Page05ReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()




    def fetch_page_05_prompt(self): 
        try:
            query = text("SELECT [balance_sheet] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for page 05 prompt.")
                return None
            return result[0]['balance_sheet']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching page 05 prompt: {e}")
            return None  



    def calculate_financial_ratios(self,data: dict) -> dict:
        """
        Return Current-Ratio and Debt-to-Equity for every year contained in
        data["balance_sheet"]["yearly_data"].

        Assumptions
        -----------
        • current_assets      → use the cash balance (best proxy available).
        • current_liabilities → use short-term debt.
        • debt-to-equity      → total_liabilities ÷ equity
        (this is what your KPI table appears to use).

        All ratios are rounded to 2 decimal places; if a denominator is zero
        the ratio is returned as None.
        """
        results = {}

        try:
            # Parse JSON string to dictionary
            balance_sheet = json.loads(data["balance_sheet"])
            
            # Turn yearly_data (list) into a dict keyed by year for easy access
            bs_rows = {str(row["year"]): row for row in balance_sheet["yearly_data"]}

            for year, row in bs_rows.items():
                total_assets       = float(row["total_assets"])
                total_liabilities  = float(row["total_liabilities"])
                equity             = float(row["equity"])

            # “Current” figures (best available proxies)
            current_assets     = float(row.get("current_assets", row.get("cash", 0)))
            current_liabilities= float(row.get("current_liabilities",
                                            row.get("debt", {}).get("short_term", 0)))

            # ---- Ratios ----------------------------------------------------
            current_ratio      = (current_assets / current_liabilities
                                if current_liabilities else None)
            debt_to_equity     = (total_liabilities / equity
                                if equity else None)

            results[year] = {
                "total_assets":          total_assets,
                "total_liabilities":     total_liabilities,
                "equity":                equity,
                "current_ratio":         round(current_ratio, 2) if current_ratio is not None else None,
                "debt_to_equity_ratio":  round(debt_to_equity, 2) if debt_to_equity is not None else None,
            }

            return results
        
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {e}")
            return {}
         
        



    def generate_report(self):

        financial_ratios = self.calculate_financial_ratios(self.report_data)
        if not financial_ratios:
            logger.error("Failed to calculate financial ratios.")
            return {"error": "Failed to calculate financial ratios."}

        prompt_template = self.fetch_page_05_prompt()
        if not prompt_template:
            logger.error("Failed to fetch prompt template for page 05.")
            return {"error": "Failed to fetch prompt template."}

        messages = [
            {"role": "system", "content": "You are a financial report expert. Your task is to generate a comprehensive balance sheet analysis report. The report should be structured as a single JSON object with detailed HTML content for each section."},
            {"role": "user", "content": f"{prompt_template}\n\nHere are the calculated financial ratios: {financial_ratios}"},
        ]

        raw_content = ""
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=os.getenv("DEPLOYMENT_NAME"),
                
                temperature=0.7
            )
            raw_content = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"error": str(e)}

        try:
            report_data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {e}")
            return {"error": "Invalid JSON response from the model."}

        return report_data     