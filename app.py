from flask import Flask, request, jsonify
import sqlite3
from src.LlamaApp import Response_Generation
from flask_cors import CORS







obj = Response_Generation()

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return 'BEV REPORT'





@app.route("/response", methods = ['POST', 'GET'])
def predict():
    try:
        if request.method == "POST":

            data = request.get_json()
            print(data)
            txt_result = obj.respone_result(data)
            print(txt_result)
          
            return txt_result,200
    except Exception as e:
        raise e
    




# API endpoint to return items for dropdown
@app.route('/dropdown', methods=['GET'])
def get_dropdown_items():
    items = obj.get_items_from_db()  # Get items from the database
    return jsonify(items)  # Return the items as a JSON response    
























if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug= True)