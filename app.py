# import datetime
from flask import Flask, request, jsonify,send_file
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
            #to save pdf url  against EIN_Value
            obj.save_pdf_url(ein=EIN_Value, pdf_url=public_url)

           

            return jsonify({"validation": validation_result,"public_url":public_url})  
        else:
            return jsonify({"validation": validation_result})



    except Exception as e:
        logger.error(f"Error {e}")
        # Consider returning an error response with a status code for failures
        # return jsonify({'error': 'An error occurred during file upload'}), 500

# report_status = {}

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

#         EIN_Value = all_params['EIN'] 
#         validation_result = obj.return_result(EIN_Value)


#         if validation_result is not None:
#             public_url = obj.return_public_url(ein=EIN_Value, url=filtered_urls)
            
#             # Generate unique task ID
#             task_id = str(uuid.uuid4())
            
#             # Initialize status
#             report_status[task_id] = {
#                 "status": "processing",
#                 "message": "Report generation started",
#                 "created_at": datetime.now().isoformat(),
#                 "ein": EIN_Value,
#                 "public_url": public_url,
#                 "report_url": None,
#                 "error": None
#             }
            
#             # Start background task
#             thread = threading.Thread(
#                 target=generate_report_background,
#                 args=(task_id, public_url, EIN_Value)
#             )
#             thread.daemon = True
#             thread.start()
            
#             return jsonify({
#                 "validation": validation_result,
#                 "public_url": public_url,
#                 "task_id": task_id,
#                 "status": "processing",
#                 "message": "Report generation started. Use task_id to check status.",
#                 "estimated_time": "5-7 minutes"
#             })
#         else:
#             return jsonify({"validation": validation_result})



#     except Exception as e:
#         logger.error(f"Error {e}")
#         return jsonify({'error': 'An error occurred during file upload'}), 500

# def generate_report_background(task_id, public_url, ein_value):
#     """Background function to generate the report"""
#     try:
#         logger.info(f"Starting background report generation for task: {task_id}")
        
#         # Update status to processing
#         report_status[task_id]["status"] = "processing"
#         report_status[task_id]["message"] = "Generating report..."
        
#         # Run the report generation pipeline
#         report_generation_pipeline = BEVDetailReportGenerationPipeline(file_path_or_url=public_url, ein=ein_value)
#          # Assuming run_pipeline returns the report URL
#         result = report_generation_pipeline.run_pipeline()
        
#         # Update status to completed
#         report_status[task_id]["status"] = "completed"
#         report_status[task_id]["message"] = "Report generated successfully"
#         report_status[task_id]["report_url"] = result  # Assuming run_pipeline returns the report URL
#         report_status[task_id]["completed_at"] = datetime.now().isoformat()
        
#         logger.info(f"Background report generation completed for task: {task_id}")
        
#     except Exception as e:
#         logger.error(f"Error in background report generation for task {task_id}: {e}")
        
#         # Update status to failed
#         report_status[task_id]["status"] = "failed"
#         report_status[task_id]["message"] = f"Report generation failed: {str(e)}"
#         report_status[task_id]["error"] = str(e)
#         report_status[task_id]["failed_at"] = datetime.now().isoformat()

# # Add endpoint to check report status
# @app.route("/reportstatus/<task_id>", methods=['GET'])
# @require_api_key
# def check_report_status(task_id):
#     """Check the status of report generation"""
#     try:
#         if task_id not in report_status:
#             return jsonify({"error": "Task ID not found"}), 404
        
#         status_info = report_status[task_id]
        
#         # Clean up old completed/failed tasks (optional)
#         # You might want to implement a cleanup mechanism
        
#         return jsonify(status_info)
        
#     except Exception as e:
#         logger.error(f"Error checking report status: {e}")
#         return jsonify({"error": "Internal server error"}), 500



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
            bev_db = BEVDetailReportGenerationSaveDB()
            pdf_url = bev_db.get_generated_report_by_ein_order(EIN_Seller, Order_Id_Buyer)
            if pdf_url is None:
                return jsonify({"error": "PDF URL not found"}), 404

        ## retirve report from db aginst EIN_Seller and Order_Id_Buyer and return pdf url

        # if all_params:
        report_url = pdf_url
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

        if all_params:
            EIN_Seller = all_params.get('EIN_Seller')
            Order_Id_Buyer = all_params.get('Order_Id_Buyer')

            bev_db = BEVDetailReportGenerationSaveDB()
            pdf_url = bev_db.get_pdf_url_by_ein(EIN_Seller)
            if pdf_url is None:
                return jsonify({"error": "PDF URL not found"}), 404

            report_generation_pipeline = BEVDetailReportGenerationPipeline(file_path_or_url=pdf_url)
            pdf_url = report_generation_pipeline.run_pipeline()
            bev_db.insert_report_generated(ein=EIN_Seller, order_id=Order_Id_Buyer, generated_report_url=pdf_url)

        ## select two values from all_params one is EIN_Seller and Order_Id_Buyer. retrieve pdf url against EIN_Seller then start generate report and saved generated report against Order_Id_Buyer
        ## and EIN_Seller.
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
    