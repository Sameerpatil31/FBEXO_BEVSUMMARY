from src.LLM.azure_openai import AzureOpenAIClient
from langchain_huggingface import HuggingFaceEndpoint
# from langchain_community.llms import HuggingFaceEndpoint,huggingface_endpoint
from src.BEV_SUMMARY.Prompt import PROMPT_SYSTEM_USER_ASSISTANT,createpromt
from src.BEV_SUMMARY.utils import *
from langchain import PromptTemplate, LLMChain
import sqlite3
import pandas as pd
import json
from dotenv import load_dotenv
import os
from src.login import logger
from src.BEV_SUMMARY.llm import Load_llm
# Load environment variables from the .env file
load_dotenv()



   




class Response_Generation:
    def __init__(self,api_key):
     
        self._sqlite_DB_Path = os.path.join('artifacts','BEV_database.db')
        # self._hf_token = hf_token
        self._system_promt = createpromt()
        self.load_llm = Load_llm(api_key)
        self.azure_client = AzureOpenAIClient()
        self.client = self.azure_client.get_client()






    def get_items_from_db(self):

        try:
            conn = sqlite3.connect(self._sqlite_DB_Path)
            c = conn.cursor()
            
            # Fetch all items
            c.execute('SELECT Industry_Name FROM BEV')
            items = c.fetchall()
            
            conn.close()
            logger.info("Business type list fetched:")
            
            # Convert data to a list of dictionaries
            return [item[0] for item in items]    
        except Exception as e:
            logger.error(f"Error in get_items_from_db function and error is {e}")






    def parse_json(self,jdata):

        """ 
        Prosses json data and return as list
        
        """

        try:

            # print(f"This is from json parse function{jdata}")

            jdata = json.loads(f"""{jdata}""")
            print(type(jdata))
            zipCode = jdata['zipCode']
            businessType = jdata['businessType']
            currency = jdata['currency']
            financial_year_1 = jdata['financialMetrics']['years'][0]
            financial_year_2 = jdata['financialMetrics']['years'][1]
            financial_year_3 = jdata['financialMetrics']['years'][2]
            revenues=jdata['financialMetrics']['revenue']
            expenses=jdata['financialMetrics']['expenses']
            annual_growth = jdata["financialMetrics"]["annual_growth"]
            ebitda = jdata["financialMetrics"]["ebitda"]
        
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
                              "total_liabilities_financial_year":total_liabilities_financial_year,
                              "annual_growth":annual_growth,
                              "ebitda":ebitda}
            # data = [item[0] if isinstance(item, tuple) else item for item in User_Data_list]
            print(f"parse json data {User_Data_list}")
            # print(f"This is return of json parse data {dict(User_Data_list)}")
            logger.info("Parsed json data")

            return User_Data_list
        
        except Exception as e:
            print(f"error: {e}")
            logger.error(f"Error in parse_json function and error is {e}")
            raise e
        

    
        

    def all_imput_data(self,userdata)->dict:
            # print(userdata)
            try:
                df_dat = get_data_sql(userdata["businessType"])
                Discount_Rate =float(df_dat[1].replace("%",""))
                PE_Ratio =float(df_dat[2].replace("%",""))
                Industry_Multiplier = float(df_dat[3].replace("%",""))
                Earnings_Multiplier = float(df_dat[4].replace("%",""))

                Result_1,Result_2,Result_3,Result_Final = method_1(userdata["current_assets_financial_year"],userdata["total_assets_financial_year"],userdata["current_liabilities_financial_year"],userdata["total_liabilities_financial_year"])

                DCF_result, project_fcf, turminal_value = method_2(userdata["ebitda"],float(Discount_Rate),float(userdata["annual_growth"]),int(len(userdata["ebitda"])),userdata["current_liabilities_financial_year"]) 
                print(f"DCF Value {DCF_result}")   

                Net_Profit_Year,Net_Profit_result = method_3(userdata["revenues"],userdata["expenses"],PE_Ratio)
                # print(f"Method 3 :{Net_Profit_Year,Net_Profit_result}")
                Net_Profit_Year_1 =Net_Profit_Year[0]
                Net_Profit_Year_2 =Net_Profit_Year[1]
                Net_Profit_Year_3 =Net_Profit_Year[2]
                Net_Profit_result_1 = Net_Profit_result[0]
                Net_Profit_result_2 = Net_Profit_result[1]
                Net_Profit_result_3 = Net_Profit_result[2]
                Gross_revenu_result =method_4(userdata["revenues"],Industry_Multiplier)
                # print(f"Method 4 :{Gross_revenu_result}")
                Gross_revenu_Year_1 = userdata["revenues"][0]
                Gross_revenu_Year_2 = userdata["revenues"][1]
                Gross_revenu_Year_3 = userdata["revenues"][2]
                Gross_revenu_result_1 = Gross_revenu_result[0]
                Gross_revenu_result_2 = Gross_revenu_result[1]
                Gross_revenu_result_3 = Gross_revenu_result[2]
                Net_earning_result,net_valuation= method_5(userdata["revenues"],userdata["expenses"],Earnings_Multiplier)
                # print(f"Method 5 :{Net_earning_result}")
                Net_earning_result_1 = Net_earning_result[0]
                Net_earning_result_2 = Net_earning_result[1] 
                Net_earning_result_3 = Net_earning_result[2]  
                net_valuation_1 = net_valuation[0]
                net_valuation_2 = net_valuation[1] 
                net_valuation_3 = net_valuation[2] 
                Liquidation_Value  = method_6(userdata["total_assets_financial_year"],userdata["total_liabilities_financial_year"])
                # print(f"Method 6 :{Liquidation_Value}")
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
                "net_valuation_1": net_valuation_1,
                "net_valuation_2": net_valuation_2,
                "net_valuation_3": net_valuation_3,
                "Liquidation_Value_1" : Liquidation_Value_1,
                "Liquidation_Value_2" : Liquidation_Value_2,
                "Liquidation_Value_3" : Liquidation_Value_3,
                "Discount_Rate": Discount_Rate,
                "PE_Ratio" : PE_Ratio,
                "Industry_Multiplier": Industry_Multiplier,
                "Earnings_Multiplier" :Earnings_Multiplier,
                "DCF" : DCF_result,
                "pf_1": project_fcf[0],
                "pf_2": project_fcf[1],
                "pf_3": project_fcf[2],
                "Terminal_vale": turminal_value,
            

            }

                return input_params
            
            except Exception as e:
                logger.error(f"Error in all_imput_data function and erro is {e}")
    
    
    
    # def load_model(self,max_new_tokens,top_k,top_p,temperature):

    #     try:

    #         llm = HuggingFaceEndpoint(
    #             #https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/
    #             #https://gsb9o7k6ngdzs23l.us-east-1.aws.endpoints.huggingface.cloud/

    #             # endpoint_url="https://xstk0cq74upa2tv9.us-east-1.aws.endpoints.huggingface.cloud/",
    #             repo_id= "meta-llama/Llama-3.3-70B-Instruct",
    #             max_new_tokens = max_new_tokens,
    #             top_k = top_k,
    #             top_p = top_p,
    #             temperature = temperature,
    #             huggingfacehub_api_token = self._hf_token,
    #             timeout=300,
            
    #         )
    #         # print(f"ht_token { self._hf_token}")

    #         return llm
        
    #     except Exception as e:
    #         logger.error(f"Error in load_model function and error is {e}")
    




    
    def respone_result(self,jsondata):

        try:
           

            # llm = self.load_llm.openai_llm(                            
            #                 max_new_tokens=4000,
            #                 top_k=10,
            #                 top_p=0.25,
            #                 temperature=0.10,
                            
            #                 )


            user_data = self.parse_json(jsondata)
            # bussnesstype = user_data['business_type']

            

            # print(bussnesstype[0])
            # ratio_data_list = self.ratio_data(bussnesstype[0])

            input_param = self.all_imput_data(userdata=user_data)

            print(f"Inpput parameter {input_param}")

            promt= PromptTemplate.from_template(self._system_promt )

            ll_chain = LLMChain(llm = self.client, prompt = promt)
            data  = ll_chain.invoke(input_param)
            response = data['text']
            
            return response
        
        except Exception as e:
            logger.error(f"Error in respone_result and erro is {e}")

    



