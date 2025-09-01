from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from src.login import logger
# Load environment variables from the .env file
load_dotenv()




class Load_llm:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = None
        

    def openai_llm(self,max_new_tokens,top_k,top_p,temperature):
        # Initialize the LLM with the API key
        ChatOpenAI.model_rebuild()
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            model="gpt-4o-2024-11-20",
            # temperature=temperature,
            max_completion_tokens=max_new_tokens,
            top_p=top_p,
            # top_k=top_k,
           
        )
        return self.llm
    
   
    
    def huggingface_llm(self,max_new_tokens,top_k,top_p,temperature):

        try:

            self.llm = HuggingFaceEndpoint(
                #https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/
                #https://gsb9o7k6ngdzs23l.us-east-1.aws.endpoints.huggingface.cloud/

                # endpoint_url="https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/",
                repo_id= "meta-llama/Llama-3.3-70B-Instruct",
                max_new_tokens = max_new_tokens,
                top_k = top_k,
                top_p = top_p,
                temperature = temperature,
                huggingfacehub_api_token = self.api_key,
                timeout=300,
            
            )
            # print(f"ht_token { self._hf_token}")

            return self.llm
        
        except Exception as e:
            logger.error(f"Error in load_model function and error is {e}")


    def azure_llm(self, max_new_tokens, top_k, top_p, temperature):

        try:

            
           
            pass

        except Exception as e:
            logger.error(f"Error in load_model function and error is {e}")