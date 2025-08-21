
from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
# from scrapegraph_py import Client
from sqlalchemy import text
import os
import json





class ExecutiveSummaryReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
   
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()
        # self.scrapegraph_client = Client(api_key=os.getenv("scrapegraph_api_key"))
        
    

    def calculate_finance_metrics(self, data: dict) -> dict:
        """
        Calculate key financial ratios from the supplied data object.

        Expected structure
        ------------------
        data = {
            "financial_metrics": "JSON string containing yearly_data",
            "balance_sheet": "JSON string containing yearly_data"
        }
        """
        metrics = {}

        try:
            # ------------------------------------------------------------------
            # 1. Parse JSON strings to dictionaries
            # ------------------------------------------------------------------
            financial_metrics = json.loads(data["financial_metrics"])
            balance_sheet = json.loads(data["balance_sheet"])
            
            # Convert yearly_data list → dict keyed by year for easier access
            yearly = {str(item["year"]): item for item in financial_metrics["yearly_data"]}

            latest_year = max(yearly, key=int)           # '2023'
            previous_year = str(int(latest_year) - 1)    # '2022'

            latest_row = yearly[latest_year]
            previous_row = yearly.get(previous_year)

            # ---------------------------------------------------------------
            # 2. Revenue growth (latest vs. previous year)
            # ---------------------------------------------------------------
            if previous_row:
                latest_rev = float(latest_row["revenue"])
                previous_rev = float(previous_row["revenue"])
                metrics["revenue_growth_rate"] = (latest_rev - previous_rev) / previous_rev
            else:
                metrics["revenue_growth_rate"] = None   # Not enough history

            # ---------------------------------------------------------------
            # 3. EBITDA margin (EBITDA ÷ revenue for latest year)
            # ---------------------------------------------------------------
            metrics["ebitda_margin"] = (
                float(latest_row["ebitda"]) / latest_row["revenue"]
                if latest_row["revenue"] else None
            )

            # ---------------------------------------------------------------
            # 4. Debt-to-equity ratio using latest year data from balance sheet
            # ---------------------------------------------------------------
            # Find the latest year in balance sheet data
            bs_yearly = {item["year"]: item for item in balance_sheet["yearly_data"]}
            latest_bs = bs_yearly.get(latest_year) or bs_yearly[max(bs_yearly.keys())]
            
            debt = latest_bs.get("debt", {})
            total_debt = float(debt.get("long_term", 0)) + float(debt.get("short_term", 0))
            equity = float(latest_bs.get("equity", 0))

            metrics["debt_to_equity"] = total_debt / equity if equity else None

            return metrics

        except Exception as exc:
            # Replace with your logging solution if desired
            logger.error(f"Error calculating metrics: {exc}")
            return {}

        

    def finance_report(self):
        try:

        
            finance_metrics = self.calculate_finance_metrics(self.report_data)

            if not finance_metrics:
                logger.error("Failed to calculate financial metrics.")
                return {"error": "Failed to calculate financial metrics."}
            
            

            query = text("SELECT [executive-summary] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            data = fetch_query(query, params)
            
            if data:
                prompt_finance = data[0]['executive-summary']
            else:
                prompt_finance = None

            if not prompt_finance:
                logger.error("Executive summary not found in the database.")
                return {"error": "Executive summary not found."}
        

            messages = [
                {"role": "system", "content": "You are financial report expert. Return your answer strictly as valid JSON."},
                {"role": "user", "content": f"{prompt_finance} :: here all related metrics data : {finance_metrics}"},
            ]

           

            response = self.client.chat.completions.create(
                    model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )

            response_content = response.choices[0].message.content
            if not response_content or response_content.strip() == "":
                logger.error("Empty response from OpenAI API")
                return {"error": "Empty response from OpenAI API"}
            
            return json.loads(response_content)
        except Exception as e:
            logger.error(f"Error generating finance report: {str(e)}")
            return {"error": str(e)}     

    


    