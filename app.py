# import datetime
from flask import Flask, request, jsonify,send_file
import requests
# import threading
# from quart import Quart, jsonify, request
import sqlite3
from src.BEV_SUMMARY.LlamaApp import Response_Generation
from src.Pipeline.Business_validation import BEV_Validation
from src.Pipeline.BEV_Detail_Report_Generation_Pipelene import BEVDetailReportGenerationPipeline
from src.BEV_Details.save_genrated_pdf_db import BEVDetailReportGenerationSaveDB
from src.login import logger
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
import os
import asyncio
import json
import gunicorn
import threading
from datetime import datetime
import uuid
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
    


# @app.route("/listbusinessforsale", methods = ['POST'])
# @require_api_key
# def listbusinessforsale():
#     try:
        
#         file_info=[]
#         obj= BEV_Validation()

#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Empty or invalid JSON provided"}), 400
        

        
#         all_params = data.get('all_params', {})
#         all_url = data.get('all_url', {})

#         filtered_urls = {key: value for key, value in all_url.items() if value}

#         # Debugging - Print the filtered data
#         print("All Params:", all_params)
#         print("Filtered URLs:", filtered_urls)


#         EIN_Value =    all_params['EIN'] 
#         validation_result = obj.return_result(EIN_Value)


#         # public_url = obj.return_public_url(ein=EIN_Value,url=filtered_urls)
        
#         # return jsonify({"validation":f"{validation_result}","public_url":f"{public_url}"})

#         if validation_result is not None:
#             public_url = obj.return_public_url(ein=EIN_Value,url=filtered_urls)
#             #to save pdf url  against EIN_Value
#             print("Public url:",public_url['Business_Incorporation'])

#             obj.save_pdf_url(ein=EIN_Value, url=json.dumps(public_url))

#             return jsonify({"validation": validation_result,"public_url":public_url})  
#         else:
#             return jsonify({"validation": validation_result})



#     except Exception as e:
#         logger.error(f"Error {e}")
#         # Consider returning an error response with a status code for failures
#         # return jsonify({'error': 'An error occurred during file upload'}), 500


@app.route("/listbusinessforsale", methods=['POST'])
@require_api_key
def listbusinessforsale():
    try:
        obj = BEV_Validation()
        
        data = request.get_json()
        print("data",data)
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
        
        all_params = data.get('all_params', {})
        all_url = data.get('all_url', {})
        
        # Filter non-empty URLs
        filtered_urls = {key: value for key, value in all_url.items() if value}
        
        # Validate required parameters
        if 'EIN' not in all_params:
            return jsonify({"error": "Missing required parameter: EIN"}), 400
        
        EIN_Value = all_params['EIN']
        
        # Perform validation
        validation_result = obj.return_result(EIN_Value)
        
        if validation_result is None:
            return jsonify({"error": "Validation failed or no result returned"}), 500

        compliant = validation_result.get("fatca_comliant", "Not Compliant")
        blacklist = validation_result.get("blacklist", "Not Blacklist")
        
        if compliant == "Not Compliant" and blacklist == "Not Blacklist":
            # Generate public URLs and save
            public_url = obj.return_public_url(ein=EIN_Value, url=filtered_urls)
            obj.save_pdf_url(ein=EIN_Value, url=json.dumps(public_url))
            
            return jsonify({
                "validation": validation_result,
                "public_url": public_url
            }), 200
        
        else:
            return jsonify({
                "validation": "Not validated",
                "validation_result": validation_result
            }), 200
    
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred during processing"}), 500




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
        if all_params:
            print("All Params:", all_params)
            EIN_Seller = all_params.get('EIN_Seller')
            Order_Id_Buyer = all_params.get('Order_Id_Buyer')
            bev_db = BEVDetailReportGenerationSaveDB(ein=EIN_Seller, order_id=Order_Id_Buyer)
            pdf_url = bev_db.get_generated_report_by_ein_order()
            if pdf_url is None:
                return jsonify({"error": "PDF URL not found"}), 404

        ## retirve report from db aginst EIN_Seller and Order_Id_Buyer and return pdf url

        # if all_params:
        report_url = pdf_url
        return jsonify({"report":report_url})
        

    except Exception as e:
        logger.error(f"Error in bevfullreport end ponit api and error is {e}")   



# @app.route("/pivgenerateequest", methods = ['POST'])
# @require_api_key
# def pivgenerateequest():

#     try:
        
#         data = request.get_json()
        
#         if not data:
#             return jsonify({"error": "Empty or invalid JSON provided"}), 400
    

#         all_params = data.get('all_params', {})

#         if all_params:
#             EIN_Seller = all_params.get('EIN_Seller')
#             Order_Id_Buyer = all_params.get('Order_Id_Buyer')
#             print(f"EIN_Seller: {EIN_Seller}, Order_Id_Buyer: {Order_Id_Buyer}")
#             bev_db = BEVDetailReportGenerationSaveDB(ein=EIN_Seller, order_id=Order_Id_Buyer)

#             pdf_url = bev_db.get_pdf_url_by_ein()
#             if pdf_url is None:
#                 return jsonify({"error": "PDF URL not found"}), 404

#             print("pdf_url:", pdf_url)

#             report_generation_pipeline = BEVDetailReportGenerationPipeline(file_path_or_url=pdf_url, ein=EIN_Seller)
#             pdf_url = report_generation_pipeline.run_pipeline()
#             bev_db.insert_report_generated( generated_report_url=pdf_url)

#         ## select two values from all_params one is EIN_Seller and Order_Id_Buyer. retrieve pdf url against EIN_Seller then start generate report and saved generated report against Order_Id_Buyer
#         ## and EIN_Seller.
#             return jsonify({"message":"request accepted"})
        

#     except Exception as e:
#         logger.error(f"Error in pevgenerateequest end ponit api and error is {e}")   
# 


JOBS = {}

def long_job(job_id, ein, order_id):
    try:
        JOBS[job_id]["status"] = "running"
        bev_db = BEVDetailReportGenerationSaveDB(ein=ein, order_id=order_id)
        pdf_url = bev_db.get_pdf_url_by_ein()
        if not pdf_url:
            raise RuntimeError("PDF URL not found")
        pipeline = BEVDetailReportGenerationPipeline(file_path_or_url=pdf_url, ein=ein)
        result_url = pipeline.run_pipeline()
        bev_db.insert_report_generated(result_url)
        send_report(result_url, order_id)
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result_url"] = result_url
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)

def send_report(url_report: str, order_id):
    url = "https://fbexo.com/wp-json/fbexo-webhook/v1/report"
    headers = {
        "X-Webhook-Token": "BevSummary2024",
        "Content-Type": "application/json"
    }
    payload = {
        "order_id": str(order_id),
        "report": url_report
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for bad status
        logger.info("✅ Report sent for Notification successfully!")
        logger.info("Response: %s", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("❌ Error sending report: %s", e)
        return None


@app.route("/pivgenerateequest", methods=["POST"])
@require_api_key
def pivgenerateequest():
    logger.info("Received /pivgenerateequest request")
    data = request.get_json(silent=True)
    if not data or "all_params" not in data:
        return jsonify({"error": "Invalid JSON"}), 400
    ein = data["all_params"].get("EIN_Seller")
    order_id = data["all_params"].get("Order_Id_Buyer")
    if not ein or not order_id:
        return jsonify({"error": "Missing EIN_Seller or Order_Id_Buyer"}), 400

    job_id = str(len(JOBS) + 1)
    JOBS[job_id] = {"status": "queued"}
    logger.info(f"Starting job {job_id} for EIN {ein} and Order ID {order_id}")
    threading.Thread(target=long_job, args=(job_id, ein, order_id), daemon=True).start()
    logger.info(f"Job {job_id} started in background")  

    return jsonify({"message": "request accepted", "job_id": job_id}), 202        


@app.route("/pivreport", methods = ['POST'])
@require_api_key
def pivreport():

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON provided"}), 400
    

        all_params = data.get('all_params', {})
        if all_params:
            print("All Params:", all_params)
            EIN_Seller = all_params.get('EIN_Seller')
            Order_Id_Buyer = all_params.get('Order_Id_Buyer')
            bev_db = BEVDetailReportGenerationSaveDB(ein=EIN_Seller, order_id=Order_Id_Buyer)
            pdf_url = bev_db.get_generated_report_by_ein_order()
            if pdf_url is None:
                return jsonify({"error": "PDF URL not found"}), 404

        ## retirve report from db aginst EIN_Seller and Order_Id_Buyer and return pdf url

        # if all_params:
        report_url = pdf_url
        return jsonify({"report":report_url})
        
    
    except Exception as e:
        logger.error(f"Error in pivreport end ponit api and error is {e}")   
                       







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,threaded =True)
