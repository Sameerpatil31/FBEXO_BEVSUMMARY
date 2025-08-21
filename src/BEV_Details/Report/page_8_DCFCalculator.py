from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
import os
import json
from sqlalchemy import text


class DCFCalculator:
    def __init__(self, report_data):
        self.report_data = report_data
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()

    def generate_dcf_data(self, data: dict, discount_rate: float = 0.10) -> str:
        """
        Build a Discounted-Cash-Flow (DCF) report from the supplied data object.

        Parameters
        ----------
        data : dict
            Must contain  data["cash_flow"]["yearly_data"][{ "year": ..., "net_cash_flow": ... }, … ]
        discount_rate : float, optional
            The discount rate r to use in PV = CF / (1+r)^N  (default 10%).

        """
        try:
            # Parse JSON string if it's a string, otherwise use as dict
            if isinstance(data.get("cash_flow"), str):
                cash_flow_data = json.loads(data["cash_flow"])
            else:
                cash_flow_data = data["cash_flow"]

            # ------------------------------------------------------------------
            # 1. Collect (and order) the cash-flows we'll discount
            # ------------------------------------------------------------------
            cf_rows = cash_flow_data["yearly_data"]

            # Sort chronologically (oldest → newest) so that Year 1 = first future period
            cf_rows = sorted(cf_rows, key=lambda row: int(row["year"]))

            projected_flows = [float(row["net_cash_flow"]) for row in cf_rows]

            # ------------------------------------------------------------------
            # 2. Discount each cash-flow
            # ------------------------------------------------------------------
            present_values = []
            for n, cf in enumerate(projected_flows, start=1):        # N = 1 … len(flows)
                pv = cf / ((1 + discount_rate) ** n)
                present_values.append(round(pv, 2))

            # ------------------------------------------------------------------
            # 3. Build the output payload
            # ------------------------------------------------------------------
            payload = {
                "projected_cash_flows": projected_flows,
                "discount_rate": discount_rate,
                "present_values": {f"Year {i+1}": pv for i, pv in enumerate(present_values)},
                "total_dcf": round(sum(present_values), 2)
            }

            return json.dumps(payload, indent=4)
        except Exception as e:
            logger.error(f"Error generating DCF data: {e}")
            return json.dumps({"error": f"Failed to generate DCF data: {e}"}, indent=4)

    def fetch_dcf_prompt(self):
        try:
            query = text("SELECT dcf FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for DCF prompt.")
                return None
            return result[0]['dcf']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching DCF prompt: {e}")
            return None

    def dcf_report_generation(self):
        prompt_template = self.fetch_dcf_prompt()
        if not prompt_template:
            logger.error("Failed to fetch DCF prompt template.")
            return {"error": "Failed to fetch DCF prompt template."}

        dcf_data = self.generate_dcf_data(self.report_data)

        messages = [
            {"role": "user", "content": f"{prompt_template} :: Here are the company data: {dcf_data}"},
        ]

        response = self.client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_report(self):
        """Main method called by the pipeline to generate the DCF report."""
        return self.dcf_report_generation()