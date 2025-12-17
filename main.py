from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
import uuid
import base64
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Укажите ваши учетные данные для OAuth
client_id = "da9683f7-7f85-4cef-944d-0dfef3227e31"
client_secret = "da9683f7-7f85-4cef-944d-0dfef3227e31"

def get_access_token():
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {encoded_credentials}'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        token_info = response.json()
        return token_info['access_token']
    except Exception as e:
        app.logger.error(f"Ошибка при получении токена: {str(e)}")
        raise

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

    try:
        access_token = get_access_token()
    except Exception as e:
        app.logger.error(f"Ошибка получения токена: {str(e)}")
        return jsonify({"error": f"Ошибка получения токена: {str(e)}"}), 500

    payload = {
        "model": "GigaChat-2-Max",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    try:
        app.logger.info(f"Отправляю запрос к GigaChat...")
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            json=payload,
            headers=headers,
            verify=False,  # Используйте только для тестового окружения
            timeout=10
        )
        app.logger.info(f"Статус ответа: {response.status_code}")
        app.logger.info(f"Ответ от сервера: {response.text}")
        response.raise_for_status()
        response_data = response.json()
        app.logger.info(f"Ответ от GigaChat: {response_data}")
        return jsonify(response_data), 200
    except requests.exceptions.HTTPError as e:
        app.logger.error(f"Ошибка HTTP: {str(e)}")
        return jsonify({"error": f"Ошибка HTTP: {str(e)}"}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Ошибка запроса: {str(e)}")
        return jsonify({"error": f"Ошибка запроса: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
