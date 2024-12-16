from langchain_huggingface import HuggingFaceEndpoint
import json
from dotenv import load_dotenv
import os
from src.login import logger
# Load environment variables from the .env file
load_dotenv()










def load_model(max_new_tokens,top_k,top_p,temperature):

    try:
        hf_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
        repo_id = "meta-llama/Llama-3.1-8B-Instruct"

        llm = HuggingFaceEndpoint(
            #https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/
            #https://gsb9o7k6ngdzs23l.us-east-1.aws.endpoints.huggingface.cloud/

            # endpoint_url="https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/",
            repo_id= repo_id,
            max_new_tokens = max_new_tokens,
            top_k = top_k,
            top_p = top_p,
            temperature = temperature,
            huggingfacehub_api_token = hf_token,
            timeout=300,
        
        )
        # print(f"ht_token { self._hf_token}")

        return llm
    
    except Exception as e:
        logger.error(f"Error in load_model function and error is {e}")
