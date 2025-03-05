import os
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import google.generativeai as genai
import json

app = Flask(__name__)
CORS(app)

# 配置 Gemini API 密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    def generate():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            chat = model.start_chat()
            
            response = chat.send_message(user_message, stream=True)
            
            for chunk in response:
                content = chunk.text
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield "data: [DONE]\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/get_voices', methods=['GET'])
def get_voices():
    voices = [
        {"name": "預設中文女聲", "value": "zh-TW-Female"},
        {"name": "預設中文男聲", "value": "zh-TW-Male"}
    ]
    return jsonify(voices)

@app.route('/log_conversation', methods=['POST'])
def log_conversation():
    data = request.json
    return jsonify({"status": "logged"})

# 对于 Vercel，我们不需要 app.run()
# Vercel 将使用 gunicorn 运行应用
