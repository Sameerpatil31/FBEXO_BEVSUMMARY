from flask import Flask, request, jsonify,send_file
# from quart import Quart, jsonify, request
import sqlite3
from src.BEV_SUMMARY.LlamaApp import Response_Generation
from src.Pipeline.Business_validation import BEV_Validation
from src.login import logger
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
import os
import asyncio
import json
import gunicorn
# Load environment variables from the .env file
load_dotenv()





#'BevSummary2024'
hf_key = os.getenv('HUGGINGFACEHUB_API_TOKEN')
openai_key = os.getenv('OPENAI_API_KEY')

obj = Response_Generation(openai_key)

app = Flask(__name__)
# CORS(app)
app.config['API_KEY'] =   os.getenv('bev-api-key')

@app.route("/")
def home():
    return 'BEV'



def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            api_key = request.headers.get('bev-api-key')  # Frontend sends the key in headers

            if api_key and api_key == app.config['API_KEY']:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid or missing API key"}), 401
        
    return decorated_function






@app.route("/bevsummary", methods = ['POST'])
@require_api_key
def predict():
    try:
        if request.method == "POST":

            data =request.get_json()
            json_string = json.dumps(data, indent=None)
            # print(json_string)
            
            txt_result = obj.respone_result(json_string)
            # print(txt_result)
            app.logger.info(f"Response result: {txt_result} (type: {type(txt_result)})")
            logger.info("Report generated")
          
            return jsonify({"result":txt_result})
    except Exception as e:
        # Handle the OperationalError and return a valid response
        app.logger.error(f"Error {e}")
        logger.error(f" Error in /bevsummary end point and error is {e}")
        return jsonify({"error": str(e)})
    


# API endpoint to return items for dropdown
@app.route('/businesstype', methods=['GET'])
@require_api_key
def get_dropdown_items():
    try:
        items = obj.get_items_from_db()
        # llm = (obj.load_model(max_new_tokens=10,top_k=1,top_p=0.5,temperature=0.5))
        # print(llm) # Get items from the database
        return items  # Return the items as a JSON response    
    except Exception as e:
        logger.error(f" Error in /businesstype end point and error is {e}")
        
    



@app.route("/llmwakeupcall", methods = ['POST'])
@require_api_key
def llmwakeupcall():
    try:
        if request.method == "POST":

            
            llm = obj.load_model(max_new_tokens=10,top_k=2,top_p=0.5,temperature=0.1)
            result = llm.invoke(input="What is capital of India")
            print(result)

            app.logger.info(f"Response result: {result} (type: {type(result)})")
            logger.info("llm_Wakeup_call initiated")
          
            return jsonify({"result":result}),200
    except Exception as e:
        # Handle the OperationalError and return a valid response
        app.logger.error(f"Error {e}")
        logger.error(f" Error in /llmwakeupcall end point and error is {e}")
        return jsonify({"error": str(e)}),500    
    


@app.route("/listbusinessforsale", methods = ['POST'])
@require_api_key
def listbusinessforsale():
    try:
        
        file_info=[]
        obj= BEV_Validation()

        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
        

        
        all_params = data.get('all_params', {})
        all_url = data.get('all_url', {})

        filtered_urls = {key: value for key, value in all_url.items() if value}

        # Debugging - Print the filtered data
        print("All Params:", all_params)
        print("Filtered URLs:", filtered_urls)


        EIN_Value =    all_params['EIN'] 
        validation_result = obj.return_result(EIN_Value)


        # public_url = obj.return_public_url(ein=EIN_Value,url=filtered_urls)
        
        # return jsonify({"validation":f"{validation_result}","public_url":f"{public_url}"})

        if validation_result is not None:
            public_url = obj.return_public_url(ein=EIN_Value,url=filtered_urls)
            
            return jsonify({"validation": validation_result,"public_url":public_url})  
        else:
            return jsonify({"validation": validation_result})



    except Exception as e:
        logger.error(f"Error {e}")
        # Consider returning an error response with a status code for failures
        # return jsonify({'error': 'An error occurred during file upload'}), 500



@app.route("/bevfullreportpurchase", methods = ['POST'])
@require_api_key
def bevfullreportpurchase():
    try:

        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400



        all_params = data.get('all_params', {})
        all_url = data.get('all_url', {})

        filtered_urls = {key: value for key, value in all_url.items() if value}

        # Debugging - Print the filtered data
        print("All Params:", all_params)
        print("Filtered URLs:", filtered_urls)    

        EIN_Value =    all_params['EIN'] 



        return jsonify({"public_url":{

            "Business_Incorporation": "null",
            "Profit_Loss_Latest": "null",
            "Profit_Loss_2_Latest": "null",
            "Profit_Loss_3_Latest": "null",
            "Balance_Sheet_Latest": "null",
            "Balance_Sheet_2_Latest": "null",
            "Balance_Sheet_3_Latest": "null",
            "Cash_Flow_Latest": "null",
            "Cash_Flow_2_Latest": "null",
            "Cash_Flow_3_Latest": "null"
        }
        }
        
        )
    
    except Exception as e:
        logger.error(f"Error in bevfullreportpurchase end ponit api and error is {e}")
    



@app.route("/bevfullreport", methods = ['POST'])
@require_api_key
def bevfullreport():

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
    

        all_params = data.get('all_params', {})

        # if all_params:
        report_url = "https://fbexofile.s3.eu-north-1.amazonaws.com/BEV_FULL_REPORT/123456789/BEV+Full+Report+for+Austin+Small+Business.pdf"
        return jsonify({"report":report_url})
        

    except Exception as e:
        logger.error(f"Error in bevfullreport end ponit api and error is {e}")   



@app.route("/pivgenerateequest", methods = ['POST'])
@require_api_key
def pivgenerateequest():

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
    

        all_params = data.get('all_params', {})

        # if all_params:
       
        return jsonify({"message":"request accepted"})
        

    except Exception as e:
        logger.error(f"Error in pevgenerateequest end ponit api and error is {e}")          


@app.route("/pivreport", methods = ['POST'])
@require_api_key
def pivreport():

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
    

        all_params = data.get('all_params', {})

        # if all_params:
       
        report_url = "https://fbexofile.s3.eu-north-1.amazonaws.com/PIV_Full_Report/123456789/orderid123456/PIV_Full_Report_for_Chicago_Small_Business.pdf"
        return jsonify({"report":report_url})
        

    except Exception as e:
        logger.error(f"Error in pivreport end ponit api and error is {e}")                       







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,threaded =True,debug=True)
    