from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from src.login import logger
from scrapegraph_py import Client

from sqlalchemy import text
import os
import json





class AboutIndustryReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
    #     self.client  = AzureOpenAI(
    #     azure_endpoint= os.getenv("ENDPOINT_URL"),
    #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     api_version="2025-01-01-preview"
    # )
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()
        self.scrapegraph_client = Client(api_key=os.getenv("scrapegraph_api_key"))


    def fetch_industry_prompt(self):
        try:
            query = text("SELECT [about_company_report_generation] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                company_info = json.loads(self.report_data['company_info'])
                logger.error(f"❌ No data found for industry: {company_info['name']}")
                return None
            return result[0]['about_company_report_generation']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"❌ Error fetching industry data: {e}")
            return None   



    def fetch_webscrap_prompt(self):   
        try:
            query = text("SELECT [about_company_webscraping] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                company_info = json.loads(self.report_data['company_info'])
                logger.error(f"❌ No webscrap prompt found for industry: {company_info['name']}")
                return None
            return result[0]['about_company_webscraping']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"❌ Error fetching webscrap prompt: {e}")
            return None



    def scrape_website_data(self, website_url: str, user_prompt: str):
        """Scrape website data using SmartScraper"""
        # Reverted to original arguments as per user's code and error message
        response = self.scrapegraph_client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt
        )
        # Assuming the relevant data is in response['result'] as per original code.
        # This needs to be verified if scraping still fails.
        if isinstance(response, dict) and 'result' in response:
            return response['result']
        elif isinstance(response, (dict, list)): # If response itself is the data
            logger.warning("Scrapegraph returned data directly, not in 'result' key. Using direct response.")
            return response
        else:
            logger.error(f"Unexpected response format from scrapegraph: {type(response)}")
            logger.json(response) # Show what was returned
        return {"error": "Failed to parse scrapegraph response", "details": "Unexpected format"}
    
        

    def generate_report(self, data_company, report_prompt_template):
        """Generate report using HuggingFace model, expecting JSON output."""
        
        # data_company_json_str = json.dumps(data_company, indent=2)

        messages = [
            {"role": "system", "content": "You are a financial report expert. Your task is to generate a comprehensive due diligence report. The report should be structured as a single JSON object. Each key in this JSON object will correspond to a section of the report (e.g., 'companyOverview', 'people', 'swotAnalysis'). The value for each key should be a string containing the detailed HTML content for that section, following the formatting guidelines provided in the user prompt. For the 'swotAnalysis' section, the value should be a nested JSON object with keys 'strengths', 'weaknesses', 'opportunities', 'threats', each holding an HTML string."},
            {"role": "user", "content": f"{report_prompt_template}\n\nHere is the scraped data to use:\n{data_company} "},
        ]

        raw_content = ""
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("DEPLOYMENT_NAME"),  # Use the deployment name instead of model name
                messages=messages,
                temperature=0.7
            )
            
            raw_content = response.choices[0].message.content
            
            cleaned_content = raw_content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
            
            if not cleaned_content.strip():
                logger.error("LLM returned empty content after cleaning.")
                return {"error": "LLM returned empty content"}

            return json.loads(cleaned_content.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}")
            return {"error": "JSONDecodeError", "details": str(e), "raw_response": raw_content}
        except Exception as e:
            logger.error(f"Error during LLM call or processing: {e}")
            if 'response' in locals() and hasattr(response, '__str__'):
                logger.error("LLM API Response object (on error): %s", str(response))
            logger.error("LLM Raw Response (if available): %s", raw_content)
            return {"error": "LLMProcessingError", "details": str(e)}
        

    def generate_report_for_industry(self):
        try:
            report_prompt_template = self.fetch_industry_prompt()
            if not report_prompt_template:
                return {"error": "Failed to fetch industry prompt"}

            webscrap_prompt = self.fetch_webscrap_prompt()
            if not webscrap_prompt:
                return {"error": "Failed to fetch webscrap prompt"}

            # Parse the JSON string to get the actual data
            company_info = json.loads(self.report_data['company_info'])
            url = company_info['website']
            print(f"Scraping data from: {url}")

            scraped_data = self.scrape_website_data(str(url), webscrap_prompt)
            if 'error' in scraped_data:
                return scraped_data

            report = self.generate_report(scraped_data, report_prompt_template)
            if 'error' in report:
                return report

            return report

        except Exception as e:
            logger.error(f"❌ Error generating industry report: {e}")
            return {"error": "Error generating industry report", "details": str(e)}