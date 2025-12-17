from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Убедитесь, что это валидный токен (полученный через OAuth)
API_KEY = "MDE5YjI2YTctM2I1MC03OTMwLWJmYWQtZWY4N2Y2ZmM5MWE2OjU0MDdkNzFmLTczYzAtNDI5Yy04MzAxLTA4N2FjMjlhNTM1YQ=="
BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL_NAME = "GigaChat-2-Max"  # или "giga-large", если нужно

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

    app.logger.info(f"Вопрос: {question}")

    system_message = (
        "Ты эксперт по медицинским тестам. "
        "Выбери все подходящие варианты ответов ИЗ ПРЕДЛОЖЕННЫХ, если это вопрос с несколькими ответами, "
        "или один вариант, если это вопрос с одним ответом. "
        "Ответь только вариантами через запятую, каждый вариант в кавычках, в точности как в списке, без изменений. "
        f"Некорректные комбинации ответов: {[f'\"{', '.join(combo)}\"' for combo in incorrect_combinations]}."
    )

    user_message = (
        f"Вопрос: {question}\n"
        f"Варианты ответов:\n{'\\n'.join(options)}\n\n"
        f"Выбери {'все подходящие варианты' if is_multiple_choice else 'наиболее подходящий вариант'} ответа ИЗ ПРЕДЛОЖЕННЫХ.\n"
        f"Некорректные комбинации ответов: {[f'\"{', '.join(combo)}\"' for combo in incorrect_combinations]}."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_message, "created_at": int(time.time())},
            {"role": "user", "content": user_message, "created_at": int(time.time())}
        ],
        "profanity_check": True  # если нужно
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        app.logger.info(f"Отправляю запрос к GigaChat...")
        response = requests.post(BASE_URL, json=payload, headers=headers)
        app.logger.info(f"Статус ответа: {response.status_code}")
        response.raise_for_status()
        response_data = response.json()
        app.logger.info(f"Ответ от GigaChat: {response_data}")
        return jsonify(response_data), 200
    except Exception as e:
        app.logger.error(f"Ошибка при запросе к GigaChat: {str(e)}")
        return jsonify({"error": f"Ошибка при запросе к GigaChat: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
