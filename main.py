# main.py
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='templates')

# Ваш API-ключ GigaChat
API_KEY = "your_giga_chat_api_key"
BASE_URL = "https://api.giga.chat/v1/chat/completions"
MODEL_NAME = "giga-large"

@app.route('/')
def home():
    """Главная страница"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Обрабатываем запрос к GigaChat и возвращаем ответ.
    """
    message = request.form['message']
    print(f"[LOG] Входящее сообщение: {message}")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", content: message}
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response_data = response.json()
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)