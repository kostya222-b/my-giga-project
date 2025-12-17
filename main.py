from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Разрешаем CORS для всех доменов

# Ваш API-ключ GigaChat
API_KEY = "your_giga_chat_api_key"
BASE_URL = "https://api.giga.chat/v1/chat/completions"
MODEL_NAME = "giga-large"

@app.route('/')
def home():
    return "Backend for GigaChat Extension"

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.json
    question = data.get('question')
    options = data.get('options')
    is_multiple_choice = data.get('isMultipleChoice', False)
    incorrect_combinations = data.get('incorrectCombinations', [])

    print(f"[LOG] Вопрос: {question}")
    print(f"[LOG] Варианты: {options}")
    print(f"[LOG] Множественный выбор: {is_multiple_choice}")
    print(f"[LOG] Некорректные комбинации: {incorrect_combinations}")

    # Формируем системное сообщение для GigaChat
    system_message = (
        "Ты эксперт по медицинским тестам. "
        "Выбери все подходящие варианты ответов ИЗ ПРЕДЛОЖЕННЫХ, если это вопрос с несколькими ответами, "
        "или один вариант, если это вопрос с одним ответом. "
        "Ответь только вариантами через запятую, каждый вариант в кавычках, в точности как в списке, без изменений. "
        f"Некорректные комбинации ответов: {[f'\"{", ".join(combo)}\"' for combo in incorrect_combinations]}."
    )

    # Формируем пользовательское сообщение
    user_message = (
        f"Вопрос: {question}\n"
        f"Варианты ответов:\n{'\\n'.join(options)}\n\n"
        f"Выбери {'все подходящие варианты' if is_multiple_choice else 'наиболее подходящий вариант'} ответа ИЗ ПРЕДЛОЖЕННЫХ.\n"
        f"Некорректные комбинации ответов: {[f'\"{", ".join(combo)}\"' for combo in incorrect_combinations]}."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print(f"[LOG] Ответ от GigaChat: {response_data}")
        return jsonify(response_data), 200
    except Exception as e:
        print(f"[LOG] Ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
