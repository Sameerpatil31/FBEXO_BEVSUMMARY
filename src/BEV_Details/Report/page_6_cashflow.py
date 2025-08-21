from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
from sqlalchemy import text
import os
import json







class Page06CashFlowReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

    def fetch_page_06_prompt(self):
        try:
            query = text("SELECT cash_flow FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for page 06 prompt.")
                return None
            return result[0]['cash_flow']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching page 06 prompt: {e}")
            return None
        

    def calculate_cash_flow_metrics(self, data: dict) -> dict:
        """
        Calculate three cash-flow metrics for every year contained in
        data["cash_flow"]["yearly_data"].

        Formulas
        --------
        • operating_cash_flow (OCF) ................. cash_from_operating_activities
        • capital_expenditures (CapEx) .............. absolute value of cash_from_investing_activities
                                                    (a negative number in the data means a cash out-flow)
        • free_cash_flow (FCF) ......................  OCF – CapEx
        • cash_flow_coverage_ratio ..................  OCF ÷ total_debt
            total_debt = long_term_debt + short_term_debt  (from balance-sheet)

        All results are rounded to two decimal places; if a denominator is zero
        the ratio is returned as None.
        """
        metrics = {}

        try:
            # Parse JSON strings to dictionaries
            cash_flow = json.loads(data["cash_flow"])
            balance_sheet = json.loads(data["balance_sheet"])

            # --- 1. Convert yearly_data lists → dicts keyed by year -------------
            cf_rows = {str(row["year"]): row for row in cash_flow["yearly_data"]}
            bs_rows = {str(row["year"]): row for row in balance_sheet["yearly_data"]}

            # --- 2. Iterate through each year present in the cash-flow block ----
            for year, cf in cf_rows.items():
                ocf = float(cf.get("cash_from_operating_activities", 0))

                # Capital expenditures (CapEx) — treat investing cash-outflow as positive spend
                investing_cf = float(cf.get("cash_from_investing_activities", 0))
                capex = abs(investing_cf)     # equivalent to  -investing_cf  if investing_cf is negative

                fcf = ocf - capex

                # ----- Total debt from the matching balance-sheet row ------------
                bs = bs_rows.get(year, {})
                debt_info = bs.get("debt", {})
                total_debt = float(debt_info.get("long_term", 0)) + float(debt_info.get("short_term", 0))

                cash_flow_coverage_ratio = (ocf / total_debt) if total_debt else None

                # ----- Store results --------------------------------------------
                metrics[year] = {
                    "operating_cash_flow":       round(ocf, 2),
                    "capital_expenditures":      round(capex, 2),
                    "free_cash_flow":            round(fcf, 2),
                    "cash_flow_coverage_ratio":  round(cash_flow_coverage_ratio, 2) if cash_flow_coverage_ratio is not None else None
                }

            return metrics

        except Exception as e:
            logger.error(f"Error calculating cash flow metrics: {e}")
            return {}

    
    def generate_report(self):


        cash_flow_data = self.calculate_cash_flow_metrics(self.report_data)
        if not cash_flow_data:
            logger.error("Failed to calculate cash flow metrics.")
            return {"error": "Failed to calculate cash flow metrics."}
        
        prompt_template = self.fetch_page_06_prompt()
        if not prompt_template:
            logger.error("Failed to fetch prompt template for page 06.")
            return {"error": "Failed to fetch prompt template."}

        messages = [
            {"role": "system", "content": "You are a financial report expert."},
            {"role": "user", "content": f"{prompt_template} :: Here are the cash flow metrics: {cash_flow_data}"},
        ]

        # response = client.chat_completion(
        #     model=os.getenv("hf_model"),
        #     messages=messages,
        #     max_tokens=8000,
        #     temperature=0.1,
        # )

        response = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
                messages=messages,
                temperature=0.7
            )

        return response.choices[0].message.content
