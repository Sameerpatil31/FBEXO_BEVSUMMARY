from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
from sqlalchemy import text
import os
import json




class Page04ReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

    def fetch_page_04_prompt(self):
        try:
            query = text("SELECT [fla] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for page 04 prompt.")
                return None
            return result[0]['fla']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching page 04 prompt: {e}")
            return None
        


    def calculate_margins_for_pnl(self,data: dict) -> dict:
        """
        Compute Gross-Profit-Margin and Net-Profit-Margin for every year
        found in data["financial_metrics"]["yearly_data"].

        Expected data schema
        --------------------
        data = {
            "financial_metrics": {
                "yearly_data": [
                    {"year": "2023", "revenue": 171842, "cogs": 141330, ...},
                    ...
                ]
            },
            "cash_flow": {
                "yearly_data": [
                    {"year": "2023", "net_income": 10.127, ...},
                    ...
                ]
            }
        }

        Formulas
        --------
        gross_profit_margin = (revenue - cogs)  / revenue * 100
        net_profit_margin   = net_profit        / revenue * 100
        • If a “net_profit” field exists in the financial block we use it,
            otherwise we fall back to cash-flow’s net_income.
        """
        margins = {}

        try:
            # Parse JSON strings to dictionaries
            financial_metrics = json.loads(data["financial_metrics"])
            cash_flow = json.loads(data.get("cash_flow", "{}"))

            # Convert the two yearly_data lists into dicts keyed by year
            fin_rows = {str(row["year"]): row for row in financial_metrics["yearly_data"]}
            cf_rows = {str(row["year"]): row for row in cash_flow.get("yearly_data", [])}

            for year, fin in fin_rows.items():
                revenue = float(fin["revenue"])
                cogs    = float(fin["cogs"])

                # ----- Gross-profit margin -----------------------------------
                gross_profit_margin = ((revenue - cogs) / revenue) * 100 if revenue else None

                # ----- Net-profit (prefer financial_metrics, else cash_flow) ---
                net_profit = float(fin.get("net_profit", cf_rows.get(year, {}).get("net_income", 0)))

                # ----- Net-profit margin -------------------------------------
                net_profit_margin = (net_profit / revenue) * 100 if revenue else None

                # Store results (rounded to 2 dp)
                margins[year] = {
                    "revenue":               revenue,
                    "cogs":                  cogs,
                    "net_profit":            net_profit,
                    "gross_profit_margin":   round(gross_profit_margin, 2) if gross_profit_margin is not None else None,
                    "net_profit_margin":     round(net_profit_margin, 2)   if net_profit_margin   is not None else None,
                }

            return margins

        except Exception as exc:
            # Replace with your logging mechanism if required
            print(f"Error computing P&L margins: {exc}")
            return {}
    



    def generate_report(self):

        margins = self.calculate_margins_for_pnl(self.report_data)
        if not margins:
            logger.error("Failed to calculate margins for P&L.")
            return {"error": "Failed to calculate margins for P&L."}


        prompt_template = self.fetch_page_04_prompt()
        if not prompt_template:
            logger.error("Failed to fetch prompt template for page 04.")
            return {"error": "Failed to fetch prompt template."}
        

        messages = [
            {"role": "system", "content": "You are a financial report expert."},
            {"role": "user", "content": prompt_template + f" Here are the calculated margins: {json.dumps(margins, indent=2)}"}
        ]

        response = self.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

