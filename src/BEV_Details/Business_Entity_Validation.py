from src.LLM.llama import load_model
from src.login import logger
import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd






class BEV:
    def __init__(self,ein:int):
        self._ein = ein
        self._FFILIST = os.path.join('artifacts','FFIListFull.csv')
        self._sdn = os.path.join('artifacts','sdn.csv')




    def einlookup(self):

        try:


            url = "https://eintaxid.com/search-ajax.php" 
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }

            
            data = {
                "query": str(self._ein)
            }

            logger.info(f"Checking ein details")

            # Send POST request
            response = requests.post(url, data=data, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            panel_body = soup.find('div', class_='panel-body fixed-panel')
            returndata = {
            "company_name" : panel_body.find('a').text.strip(),
            "ein_number" : panel_body.find('strong').text.strip().split(":")[-1].strip(),
            "Doing_Business_As" : panel_body.find('strong', text='Doing Business As: ').find_next_sibling().text.strip(),
            "address" : panel_body.find('strong', text='Address: ').next_sibling.strip(),
            "phone" : panel_body.find('strong', text='Phone: ').next_sibling.strip()

                }
            
            return json.dumps(returndata)   

        except Exception as e:
            logger.error(f"Error in function einlookup and error is : {e} ")




    def fatcacheck(self,business_name) -> str:
        """ 
        
        
        """
        try:
          logger.info("fatca chechecking")

          df_ffi= pd.read_csv(self._FFILIST)
          exists = business_name in df_ffi['FINm'].values
          if exists:
              return "Compliant"
          else:
              return "Not Compliant"

        except Exception as e:
            logger.error(f"Error in function fatcacheck and error is {e}")  




    def Sanctions_Blacklist_Check(self,business_name):   

        try:
            logger.info("Sanctions Blacklist chechecking")

            df_sdn= pd.read_csv(self._sdn,header=None)
            exists = business_name in df_sdn[1].values
            if exists:
                return "Blacklist"
            else:
                return "Not Blacklist"

        except Exception as e:
            logger.error(f"Error in function Sanctions_Blacklist_Check and error is {e}")  



    def return_validation_json(self):
        try:

            ein_details_json = self.einlookup()
            business = json.loads(ein_details_json) 
            fatca= self.fatcacheck(business['company_name'])   
            blacklist = self.Sanctions_Blacklist_Check(fatca)   

            business['fatca_comliant'] = fatca
            business['blacklist'] = blacklist

            data = json.dumps(business,indent=4)
            return data

        except Exception as e:
            logger.error(f"Error is {e}")    





    



        
        