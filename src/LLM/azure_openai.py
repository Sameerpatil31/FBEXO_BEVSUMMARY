from openai import AzureOpenAI 
import os
from dotenv import load_dotenv


from src.login import logger

class AzureOpenAIClient:
    def __init__(self):
        try:
            load_dotenv()  # Load environment variables from .env file
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("ENDPOINT_URL"),
                azure_deployment=os.getenv("DEPLOYMENT_NAME"),
                api_key= os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-12-01-preview"
            )
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI client: {e}")
            raise e

    def get_client(self):
        return self.client