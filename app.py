from flask_cors import CORS
from flask import Flask, request, jsonify
from performAI import performAI,formatting
import os
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Hello World"

@app.route('/ask', methods=['GET','POST'])
def ask_question():    
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        question = data.get('question')
        print(question)
    if not question:
        return jsonify({"error": "Question not provided"}), 400
    
    result1 = performAI(question)
    print(result1)
    # json_string = result1.to_markdown(index=False)
    # print(json_string)
    # result=formatting(result1)
    # print(result)
    # json_data = result.to_json(orient="records", indent=4)
    # print(json_data)
    return result1

if __name__ == '__main__':    
     app.run(host='127.0.0.3', port=5000)
