from flask import Flask, request, jsonify
import sqlite3
from src.LlamaApp import Response_Generation
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()





#'BevSummary2024'


obj = Response_Generation()

app = Flask(__name__)
CORS(app)
app.config['API_KEY'] =   os.getenv('bev-api-key')

@app.route("/")
def home():
    return 'BEV REPORT'



def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('bev-api-key')  # Frontend sends the key in headers

        if api_key and api_key == app.config['API_KEY']:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Invalid or missing API key"}), 401
    
    return decorated_function






@app.route("/bevsummary", methods = ['POST', 'GET'])
@require_api_key
def predict():
    try:
        if request.method == "POST":

            data = request.get_json()
            print(type(data))
            print(data)
            txt_result = obj.respone_result(data)
            # print(txt_result)
          
            return jsonify({"result":txt_result})
    except Exception as e:
        # Handle the OperationalError and return a valid response
        return jsonify({"error": str(e)}), 500
    




# API endpoint to return items for dropdown
@app.route('/businesstype', methods=['GET'])
@require_api_key
def get_dropdown_items():
    items = obj.get_items_from_db()  # Get items from the database
    return items  # Return the items as a JSON response    







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080,debug=True)