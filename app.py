from flask import Flask, render_template, request, jsonify
import asyncio
import re
import google.generativeai as genai
import uvicorn
import os
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from plagiarism import *
from jinja2 import FileSystemLoader, Environment



app = Flask(__name__)

# Get your API key from https://makersuite.google.com/u/0/app/apikey and replace API_KEY with your key
API_KEY = os.environ.get("API_KEY", "AIzaSyDCqvnBFvW-2qJfuKfzm6YUtJ8375aJFm4")

if API_KEY == "":
    print("Please get the api key from https://makersuite.google.com/u/0/app/apikey and set in env")
    sys.exit(1)

genai.configure(api_key=API_KEY)

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/plag")
def plag():
    return render_template("plag.html")

@app.route("/translate")
def translate():
    return render_template("translate.html")

@app.route("/grammar", methods=["GET"])
def grammar():
    return render_template("grammar.html")

@app.route("/sub", methods=["POST"])
def submit():
    prompt = """Rewrite the following sentence twice - first to fix grammar issues and second to fully rewrite the sentence to be more clear and enthusiastic.
    Original: There going to love opening they're present
    Fixed Grammar: They're going to love opening their present
    Fully Rewritten: They're going to be so excited to open their presents!
    Original: Your going to love NYC
    Fixed Grammar: You're going to love NYC
    Fully Rewritten: You're going to adore New York City.
    Original: {}
    Fixed Grammar:"""

    try:
        data = request.json
        text = data["textinput"]
        action = data["action"]
    except Exception as e:
        return jsonify({"error": "Invalid request"}), 400

    response = genai.generate_text(**defaults, prompt=prompt.format(text))
    response_text = re.sub(r'{', '', response.result)
    response_text = re.search(r'^(.*?)Fully Rewritten:(.*)$', response_text, re.DOTALL)
    response_text_correct = response_text.group(1).strip()
    response_text_rewritten = response_text.group(2).strip()

    if action == "correct":
        return jsonify({"textoutput": response_text_correct, "action": "correct"})
    elif action == "rewrite":
        return jsonify({"textoutput": response_text_rewritten, "action": "rewrite"})
    else:
        return jsonify({"textoutput": response_text, "action": "rewrite"})



@app.route('/plagiarism',methods=["GET","POST"])
def plagiarism_detect():
    error=False
    similarity_score = None
    links = []
    list_of_percentages = []
    if request.method=="POST":
        
        
        user_input=request.form.get('input_text')
        input_validation,sentences=get_text(user_input)
        
        if input_validation==True:
            links=get_links(url,sentences,driver)
            data_list,links_scrapped=get_data(links)
            
            similarity_score,list_of_percentages,links=plag_detector(user_input,data_list,links_scrapped)
        else:
            error="Input more text"
            

    return render_template('plagiarism.html',similarity_score=similarity_score,list_of_percentages=list_of_percentages,links=links,error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500)
