
from langchain_huggingface import HuggingFaceEndpoint
from src.Prompt import PROMPT_SYSTEM_USER_ASSISTANT,system_promt
from src.utils import *
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
        return [item[0] for item in items]    







    def parse_json(self,jdata):

        """ 
        Prosses json data and return as list
        
        """

        try:

            # print(f"This is from json parse function{jdata}")

            # jdata = json.loads(f"""{jdata}""")
            print(type(jdata))
            zipCode = jdata['zipCode']
            businessType = jdata['businessType']
            currency = jdata['currency']
            financial_year_1 = jdata['financialMetrics']['years'][0]
            financial_year_2 = jdata['financialMetrics']['years'][1]
            financial_year_3 = jdata['financialMetrics']['years'][2]
            revenues=jdata['financialMetrics']['revenue']
            expenses=jdata['financialMetrics']['expenses']
        
            current_assets_financial_year=jdata['financialMetrics']['assets']['current']
        
            total_assets_financial_year= jdata['financialMetrics']['assets']['total']
        
            current_liabilities_financial_year= jdata['financialMetrics']['liabilities']['current']
        
            total_liabilities_financial_year= jdata['financialMetrics']['liabilities']['total']

            User_Data_list = {"zipCode":zipCode,
                              "businessType":businessType,
                              "currency":currency,
                              "expenses":expenses,
                              "financial_year_1":financial_year_1,
                              "financial_year_2":financial_year_2,
                              "financial_year_3":financial_year_3,
                              "revenues":revenues,
                              "current_assets_financial_year":current_assets_financial_year,
                              "total_assets_financial_year":total_assets_financial_year,
                              "current_liabilities_financial_year":current_liabilities_financial_year,
                              "total_liabilities_financial_year":total_liabilities_financial_year}
            # data = [item[0] if isinstance(item, tuple) else item for item in User_Data_list]
            print(type(User_Data_list))
            print(f"This is return of json parse data {dict(User_Data_list)}")

            return User_Data_list
        
        except Exception as e:
            print(f"error: {e}")
            raise e
        

    
        

    def all_imput_data(self,userdata)->dict:
            print(userdata)
            df_dat = get_data_sql(userdata["businessType"])
            Discount_Rate =float(df_dat[1].replace("%",""))
            PE_Ratio =float(df_dat[2].replace("%",""))
            Industry_Multiplier = float(df_dat[3].replace("%",""))
            Earnings_Multiplier = float(df_dat[4].replace("%",""))
            Result_1,Result_2,Result_3,Result_Final = method_1(userdata["current_assets_financial_year"],userdata["total_assets_financial_year"],userdata["current_liabilities_financial_year"],userdata["total_liabilities_financial_year"])
            Net_Profit_Year,Net_Profit_result = method_3(userdata["revenues"],userdata["expenses"],PE_Ratio)
            print(f"Method 3 :{Net_Profit_Year,Net_Profit_result}")
            Net_Profit_Year_1 =Net_Profit_Year[0]
            Net_Profit_Year_2 =Net_Profit_Year[1]
            Net_Profit_Year_3 =Net_Profit_Year[2]
            Net_Profit_result_1 = Net_Profit_result[0]
            Net_Profit_result_2 = Net_Profit_result[1]
            Net_Profit_result_3 = Net_Profit_result[2]
            Gross_revenu_result =method_4(userdata["revenues"],Industry_Multiplier)
            print(f"Method 4 :{Gross_revenu_result}")
            Gross_revenu_Year_1 = userdata["revenues"][0]
            Gross_revenu_Year_2 = userdata["revenues"][1]
            Gross_revenu_Year_3 = userdata["revenues"][2]
            Gross_revenu_result_1 = Gross_revenu_result[0]
            Gross_revenu_result_2 = Gross_revenu_result[1]
            Gross_revenu_result_3 = Gross_revenu_result[2]
            Net_earning_result= method_5(userdata["revenues"],userdata["expenses"],Earnings_Multiplier)
            print(f"Method 5 :{Net_earning_result}")
            Net_earning_result_1 = Net_earning_result[0]
            Net_earning_result_2 = Net_earning_result[1] 
            Net_earning_result_3 = Net_earning_result[2]  
            Liquidation_Value  = method_6(userdata["current_assets_financial_year"],userdata["current_liabilities_financial_year"])
            print(f"Method 6 :{Liquidation_Value}")
            Liquidation_Value_1 = Liquidation_Value[0]
            Liquidation_Value_2 = Liquidation_Value[1]
            Liquidation_Value_3 = Liquidation_Value[2]

            input_params = {
            "zipCode" : userdata["zipCode"],
            "businessType" : userdata["businessType"],
            "currency" : userdata["currency"],
            "Year_1" : userdata['financial_year_1'],
            "Year_2" : userdata['financial_year_2'],
            "Year_3" : userdata['financial_year_3'],
            "Result_1" : Result_1,
            "Result_2" : Result_2,
            "Result_3" : Result_3,
            "Result_Final" : Result_Final,
            "Net_Profit_Year_1" : Net_Profit_Year_1,
            "Net_Profit_Year_2" : Net_Profit_Year_2,
            "Net_Profit_Year_3" : Net_Profit_Year_3,
            "Net_Profit_result_1" : Net_Profit_result_1,
            "Net_Profit_result_2" : Net_Profit_result_2,  
            "Net_Profit_result_3" : Net_Profit_result_3,  
            "Gross_revenu_Year_1" : Gross_revenu_Year_1,
            "Gross_revenu_Year_2" : Gross_revenu_Year_2,
            "Gross_revenu_Year_3" : Gross_revenu_Year_3,
            "Gross_revenu_result_1" : Gross_revenu_result_1,
            "Gross_revenu_result_2" : Gross_revenu_result_2,
            "Gross_revenu_result_3" : Gross_revenu_result_3,
            "Net_Profit_Year_1" : Net_Profit_Year_1,
            "Net_Profit_Year_2" : Net_Profit_Year_2,
            "Net_Profit_Year_3" : Net_Profit_Year_3,
            "Net_earning_result_1" : Net_earning_result_1,
            "Net_earning_result_2" : Net_earning_result_2,
            "Net_earning_result_3" : Net_earning_result_3,
            "Liquidation_Value_1" : Liquidation_Value_1,
            "Liquidation_Value_2" : Liquidation_Value_2,
            "Liquidation_Value_3" : Liquidation_Value_3,
            "Discount_Rate": Discount_Rate,
            "PE_Ratio" : PE_Ratio,
            "Industry_Multiplier": Industry_Multiplier,
            "Earnings_Multiplier" :Earnings_Multiplier

        }

            return input_params
    
    
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
                            
                            max_new_tokens=5000,
                            top_k=9,
                            top_p=0.30,
                            temperature=0.10,
                            huggingfacehub_api_token=self._hf_token
                            )

            user_data = self.parse_json(jsondata)
            # bussnesstype = user_data['business_type']

            

            # print(bussnesstype[0])
            # ratio_data_list = self.ratio_data(bussnesstype[0])

            input_param = self.all_imput_data(userdata=user_data)

            promt= PromptTemplate.from_template(system_promt)

            ll_chain = LLMChain(llm = llm, prompt = promt)
            data  = ll_chain.invoke(input_param)
            response = data['text']
            return response
        
        except Exception as e:
            raise e

    



