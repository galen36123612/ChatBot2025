from flask import Flask, render_template, request, jsonify, Response, render_template_string
import requests
import json
from flask_cors import CORS  # 添加CORS支持，可能需要安裝: pip install flask-cors
import os  # 引入 os 模組來讀取環境變數

app = Flask(__name__)
CORS(app)  # 啟用跨域支持

#OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
#SITE_URL = os.getenv("SITE_URL", "https://chat-bot2025-olhn2cy9f-galens-projects-2dc1580a.vercel.app/")


@app.route('/')
def home():
    return render_template('index.html')  # 使用index.html作為模板

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')

    # 使用 OpenRouter API 發送請求
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
        },
        json={
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "stream": True  # 啟用串流模式
        },
        stream=True  # 啟用 requests 的串流模式
    )

    def generate():
        for line in response.iter_lines():
            if line:
                # 移除 "data: " 前綴並解析 JSON
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    json_str = line[6:]
                    if json_str.strip() == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        json_data = json.loads(json_str)
                        content = json_data['choices'][0]['delta'].get('content', '')
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue

    return Response(generate(), mimetype='text/event-stream')

# 添加路由來獲取語音合成語言和聲音選項
@app.route('/get_voices', methods=['GET'])
def get_voices():
    voices = [
        {"name": "預設中文女聲", "value": "zh-TW-Female"},
        {"name": "預設中文男聲", "value": "zh-TW-Male"}
    ]
    return jsonify(voices)

# 添加日誌記錄功能來跟踪對話歷史
@app.route('/log_conversation', methods=['POST'])
def log_conversation():
    data = request.json
    # 在這裡實現日誌記錄邏輯
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    app.run(debug=True)
