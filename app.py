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


obj = Response_Generation(os.getenv('HUGGINGFACEHUB_API_TOKEN'))

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

        all_files = ["Business_Incorporation",
                     "Profit_Loss_Latest",
                     "Profit_Loss_2_Latest",
                     "Profit_Loss_3_Latest",
                     "Balance_Sheet_Latest",
                     "Balance_Sheet_2_Latest",
                     "Balance_Sheet_3_Latest",
                     "Cash_Flow_Latest",
                     "Cash_Flow_2_Latest",
                     "Cash_Flow_3_Latest"
                     ] 


        all_params = [ "Company_Name",
                 "Email",
                 "Phone",
                 "EIN",
                 "Business_Type",
                 "Address",
                 "State",
                 "City",
                 "Zipcode"

                ]     

        received_params = {}
        for param_key in all_params:
            if param_key in request.form:
                received_params[param_key] = request.form[param_key]       
        for file_key in all_files:
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename != '': 
                    obj.upload_bev_files_s3(
                        file=file,
                        object_name=file.filename,
                        content_type=file.content_type
                        )

                    
                    file_info.append(file.filename)
                else:
                    # return jsonify({'error': f'{file_key} is empty'}), 400  
                    logger.info("There are no any files") 

        EIN_Value =    received_params['EIN'] 
        
        validation_result = obj.return_result(EIN_Value)    

        return jsonify({"Validation":f"{validation_result}"})          


    except Exception as e:
        logger.error(f"Error {e}")
        # Consider returning an error response with a status code for failures
        # return jsonify({'error': 'An error occurred during file upload'}), 500







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,threaded =True,debug=True)
    