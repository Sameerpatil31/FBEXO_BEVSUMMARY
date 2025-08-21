from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import os
from sqlalchemy import text





class ValuationAnalyzer:
    def __init__(self, report_data):
        self.report_data = report_data
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

    def analyze_valuation_prompt(self):
        # Fetch property details from the database
        try:
            query = text("SELECT [valuation_analyzer] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for page 07 prompt.")
                return None
            return result[0]['valuation_analyzer']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching page 07 prompt: {e}")
            return None
        

    # def generate_valuation_dummy_data(self):
    #     """Generate dummy data for different valuation methods."""
    #     data = {
    #         "asset_based": {
    #             "total_assets": 15000000,
    #             "total_liabilities": 10000000,
    #             "net_asset_value": 5000000,
    #             "adjusted_book_value": 5500000
    #         },
    #         "dcf": {
    #             "projected_cash_flows": [2500000, 3000000, 3500000],
    #             "discount_rate": 0.10,
    #             "terminal_value": 45000000,
    #             "total_dcf_value": 7380000
    #         },
    #         "comparable_company": {
    #             "ebitda": 1500000,
    #             "industry_ev_ebitda_multiple": 8,
    #             "peer_companies": [
    #                 {"name": "Peer1", "ev_ebitda": 7.8},
    #                 {"name": "Peer2", "ev_ebitda": 8.2},
    #                 {"name": "Peer3", "ev_ebitda": 7.9}
    #             ],
    #             "calculated_value": 12000000
    #         },
    #         "rule_of_thumb": {
    #             "annual_revenue": 10000000,
    #             "industry_multiplier": 1.5,
    #             "calculated_value": 15000000
    #         },
    #         "earnings_multiplier": {
    #             "annual_earnings": 2000000,
    #             "pe_ratio": 12,
    #             "calculated_value": 24000000
    #         },
    #         "monte_carlo": {
    #             "simulations": 1000,
    #             "mean_value": 18500000,
    #             "min_value": 16000000,
    #             "max_value": 21000000
    #         }
    #     }
    #     return data



    def generate_report(self):

        # valuation_data = self.generate_valuation_dummy_data()
        

        prompt_template = self.analyze_valuation_prompt()



        messages = [
        {"role": "system", "content": "You are a financial report expert."},
        {"role": "user", "content": f"{prompt_template} :: Here are the company data: {self.report_data}"},
    ]

        response = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
                messages=messages,
                temperature=0.7
            )

        return response.choices[0].message.content
