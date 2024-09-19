
from langchain_huggingface import HuggingFaceEndpoint
from src.Prompt import PROMPT_SYSTEM_USER_ASSISTANT
from langchain import PromptTemplate, LLMChain
import sqlite3
import pandas as pd
import json
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()



   
   



class Response_Generation:
    def __init__(self) -> None:
     
        self._sqlite_DB_Path = os.path.join('artifacts','BEV_database.db')
        self._hf_token =  os.getenv('HUGGINGFACEHUB_API_TOKEN')






    def get_items_from_db(self):
        conn = sqlite3.connect(self._sqlite_DB_Path)
        c = conn.cursor()
        
        # Fetch all items
        c.execute('SELECT Industry_Name FROM BEV')
        items = c.fetchall()
        
        conn.close()
        
        # Convert data to a list of dictionaries
        return [{"Industry_Name(PE_Ratio)": item[0]} for item in items]    







    def parse_json(self,data_json:json) -> list:

        """ 
        Prosses json data and return as list
        
        """

        try:

            print(data_json)

            # data_json = json.loads(f"{json_data}")
            # print(data_json)
            zip_code = data_json['zipCode'],
            business_type = data_json['businessType'],
            revenue = data_json['financialMetrics']['revenue'],
            expenses = data_json['financialMetrics']['expenses'],
            ebitda = data_json['financialMetrics']['ebitda'],
            current_assets = data_json['financialMetrics']['assets']['current'],
            fixed_assets = data_json['financialMetrics']['assets']['fixed'],
            current_liabilities = data_json['financialMetrics']['liabilities']['current'],
            long_term_liabilities = data_json['financialMetrics']['liabilities']['longTerm']

            User_Data_list = {"zip_code":zip_code,
                              "business_type":business_type,
                              "revenue":revenue,
                              "expenses":expenses,
                              "ebitda":ebitda,
                              "current_assets":current_assets,
                              "fixed_assets":fixed_assets,
                              "current_liabilities":current_liabilities,
                              "long_term_liabilities":long_term_liabilities}
            # data = [item[0] if isinstance(item, tuple) else item for item in User_Data_list]
            # print(data)
            print(User_Data_list)

            return User_Data_list
        
        except Exception as e:
            raise e
        

    def ratio_data(self,bussinesstype)->list:

        """
        Retrive data from sqlite and return as list
        """

        try:
            conn = sqlite3.connect(self._sqlite_DB_Path)
            query = 'SELECT * FROM BEV WHERE Industry_Name = ?'
            df_from_db = pd.read_sql(sql=query,con= conn,params=(bussinesstype,))
            conn.close()

            print(df_from_db)

            Discount_Rate = df_from_db[['Cost_of_Capital(Discount_rate)']].iloc[0,0]
            PE_Ratio = df_from_db[['Trailing_PE(PE_Ratio)']].iloc[0,0]
            Industry_Multiplier = df_from_db[['PBV(Industry_multiplier)']].iloc[0,0]
            Earnings_Multiplier = df_from_db[['EV/EBITDA(Earning_multiplier)']].iloc[0,0]

            list_ratio_data = [Discount_Rate,PE_Ratio,Industry_Multiplier,Earnings_Multiplier]
            print(list_ratio_data)
            # data = [item[0] if isinstance(item, tuple) else item for item in list_ratio_data]
            # print(data)

            return list_ratio_data

        except Exception as e:
            raise e    
        

    def all_imput_data(self,userdata:list,ratiodata:list)->dict:

        input_data = {

            "zip_code": userdata['zip_code'],
            "business_type": userdata['business_type'],
            "revenue": userdata['revenue'],
            "expenses": userdata['expenses'],
            "ebitda": userdata['ebitda'],
            "current_assets": userdata['current_assets'],
            "fixed_assets": userdata['fixed_assets'],
            "current_liabilities": userdata['current_liabilities'],
            "long_term_liabilities": userdata['long_term_liabilities'],
            "Discount_Rate": ratiodata[0],
            "PE_Ratio" : ratiodata[1],
            "Industry_Multiplier": ratiodata[2],
            "Earnings_Multiplier" : ratiodata[3]

        }

        return input_data
    
    
    def load_model(self,repo_id,max_new_tokens,top_k,top_p,temperature,huggingfacehub_api_token):

        llm = HuggingFaceEndpoint(

            # endpoint_url= self._endpoint_url,
            repo_id= repo_id,
            max_new_tokens = max_new_tokens,
            top_k = top_k,
            top_p = top_p,
            temperature = temperature,
            huggingfacehub_api_token = huggingfacehub_api_token
        )

        return llm
    




    
    def respone_result(self,jsondata):

        try:
           

            llm = self.load_model(repo_id='meta-llama/Meta-Llama-3.1-8B-Instruct',
                            
                            max_new_tokens=1200,
                            top_k=10,
                            top_p=0.25,
                            temperature=0.20,
                            huggingfacehub_api_token=self._hf_token
                            )

            user_data = self.parse_json(jsondata)
            bussnesstype = user_data['business_type']

            

            print(bussnesstype[0])
            ratio_data_list = self.ratio_data(bussnesstype[0])

            input_param = self.all_imput_data(userdata=user_data,ratiodata=ratio_data_list)

            promt= PromptTemplate.from_template(PROMPT_SYSTEM_USER_ASSISTANT)

            ll_chain = LLMChain(llm = llm, prompt = promt)
            data  = ll_chain.invoke(input_param)
            response = data['text']
            return response
        
        except Exception as e:
            raise e

    



