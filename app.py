import requests
from dotenv import load_dotenv
import base64
import os
from flask import Flask, request, render_template, jsonify

import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
g_text=""
def upload_to_gemini(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{
            "parts": [
                {"text": "Solve the problem:"},  # Add a text prompt
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": encoded_image
                    }
                }
            ]
        }]
    }

    response = requests.post(url, json=data, headers=headers)

    return response.json()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    response = upload_to_gemini(file_path)
    global g_text
    g_text=response
    os.remove(file_path)  # Cleanup the uploaded image
    return jsonify(response)

@app.route("/view")
def view():
    global g_text
    #click photo button here
    return render_template("view.html", response=g_text)

if __name__ == "__main__":
    app.run(debug=True)
