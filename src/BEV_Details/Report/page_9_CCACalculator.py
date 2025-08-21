from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import os
from typing import Dict, List
import json
from sqlalchemy import text




class CCACalculator:
    def __init__(self, report_data):
        self.report_data = report_data
        # self.azure_client = AzureOpenAIClient()
        # self.client = self.azure_client.get_client()
        # self.client = AzureOpenAIClient(
        #     azure_endpoint=os.getenv("ENDPOINT_URL"),
        #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     api_version="2025-01-01-preview",
        # )
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()


    # def calculate_ebitda(self, revenue, cogs, operating_expenses, depreciation, amortization):
    #     """Calculate EBITDA."""
    #     return revenue - cogs - operating_expenses + depreciation + amortization

    # def calculate_valuation(self, ebitda, ev_ebitda_ratio):
    #     """Calculate valuation based on EBITDA."""
    #     return ebitda * ev_ebitda_ratio

    # def generate_dummy_ebitda_data(self):
    #     """Generate dummy data for EBITDA calculation."""
    #     # for year, data in self.report_data['financial_metrics'].items():
            
    #     #     cca_data = {
    #     #         "Revenue": data["Revenue"],
    #     #         "COGS": data["COGS"],
    #     #         "operating_expenses": data["operating_expenses"],
    #     #         "Depreciation": 0.5e6,
    #     #         "Amortization": 0.2e6
    #     #     }
    #     cca_data = {
    #         "Revenue": 5e6,
    #         "COGS": 2e6,
    #         "Operating Expenses": 1e6,
    #         "Depreciation": 0.5e6,
    #         "Amortization": 0.2e6
    #     }
    #     return cca_data

    # def CCA_DATA(self):
    #     """Generate complete CCA analysis data."""
    #     dummy_data = self.generate_dummy_ebitda_data()
        
    #     ebitda = self.calculate_ebitda(
    #         dummy_data["Revenue"],
    #         dummy_data["COGS"],
    #         dummy_data["Operating Expenses"],
    #         dummy_data["Depreciation"],
    #         dummy_data["Amortization"]
    #     )

    #     ev_ebitda_ratio = 8
    #     valuation = self.calculate_valuation(ebitda, ev_ebitda_ratio)

    #     data = {
    #         "Dummy Data": dummy_data,
    #         "EBITDA": ebitda,
    #         "EV/EBITDA Ratio": ev_ebitda_ratio,
    #         "Valuation": valuation
    #     }

    #     return json.dumps(data, indent=4)   

    
    

    def build_cca_report(self,data: Dict,                         # the big dict you posted earlier
                        ev_ebitda_multiple: float = 8.0,    # valuation multiple to apply
                        default_dep: float = 0.5e6,         # use these if no dep/amort in data
                        default_amort: float = 0.2e6) -> str:
        """
        Generate a Comparable-Company-Analysis (CCA) table.

        Returns
        -------
       
        """
        try:
            # Parse JSON strings if needed
            if isinstance(data.get("financial_metrics"), str):
                financial_data = json.loads(data["financial_metrics"])
            else:
                financial_data = data["financial_metrics"]

            # 1. Re-arrange the yearly_data list into a simple list sorted by year
            fin_rows: List[Dict] = sorted(
                financial_data["yearly_data"],
                key=lambda r: int(r["year"])
            )

            result: Dict[str, Dict] = {}

            for row in fin_rows:
                year               = row["year"]
                revenue            = float(row["revenue"])
                cogs               = float(row["cogs"])
                op_ex              = float(row["operating_expenses"])

                # Use defaults if the fields are absent
                depreciation       = float(row.get("depreciation",  default_dep))
                amortization       = float(row.get("amortization",  default_amort))

                # --- EBITDA & Valuation ----------------------------------------
                ebitda             = revenue - cogs - op_ex + depreciation + amortization
                valuation          = ebitda * ev_ebitda_multiple

                # Store per-year record
                result[year] = {
                    "revenue":           revenue,
                    "cogs":              cogs,
                    "operating_expenses":op_ex,
                    "depreciation":      depreciation,
                    "amortization":      amortization,
                    "ebitda":            round(ebitda, 2),
                    "ev_ebitda_multiple":ev_ebitda_multiple,
                    "valuation":         round(valuation, 2)
                }

            # 2. Wrap everything in the top-level payload and serialise to JSON
            payload = {
                "cca_results": result,
                "ev_ebitda_multiple_used": ev_ebitda_multiple
            }

            return json.dumps(payload, indent=4)
        
        except Exception as e:
            logger.error(f"Error building CCA report: {e}")
            return json.dumps({"error": f"Failed to build CCA report: {e}"}, indent=4)

        


    def fetch_cca_prompt(self):
        try:
            query = text("SELECT [cca] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for cca prompt.")
                return None
            return result[0]['cca']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching cca prompt: {e}")
            return None
        


    def generate_cca_report(self):

        cca_prompt = self.fetch_cca_prompt()
        if not cca_prompt:
            logger.error("No cca prompt found.")
            return None

        cca_data = self.build_cca_report(self.report_data)
        if not cca_data:
            logger.error("No cca data found.")
            return None

        messages = [
            {"role": "user", "content": f"{cca_prompt} :: Here are the company data: {cca_data}"},
        ]

        response = self.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content