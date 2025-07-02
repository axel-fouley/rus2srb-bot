import os
import openai
import requests
from flask import Flask, request

# Загрузка переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
URL_SECRET = os.getenv("URL_SECRET")  # например: abc123xyz

# Проверка переменных
if not TOKEN:
    raise ValueError("Переменная TELEGRAM_TOKEN не задана")
if not OPENROUTER_API_KEY:
    raise ValueError("Переменная OPENROUTER_API_KEY не задана")
if not URL_SECRET:
    raise ValueError("Переменная URL_SECRET не задана")

# Инициализация Flask-приложения
app = Flask(__name__)

# Инициализация OpenRouter клиента
client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Промпт для перевода
PROMPT = (
    "Ты профессиональный переводчик с сербского на русский и с русского на сербский. "
    "Определи язык входного текста (русский или сербский) и переведи его на другой язык. "
    "Для сербского используй только латиницу, для русского — только кириллицу. "
    "Не добавляй никаких пояснений, кавычек или исходного текста, только перевод.\n"
)

# Приветственное сообщение при /start
WELCOME_MESSAGE = (
    "Добрый день! Введите слово на русском или сербском языке.\n"
    "Dobar dan! Unesite reč na ruskom ili srpskom jeziku.\n"
    "*Для лучшего понимания текст на сербском вводите латиницей."
)

# Главная страница для Render
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# Webhook
@app.route(f"/{URL_SECRET}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if not text:
        return "ok"

    # Обработка команды /start
    if text == "/start":
        send_message(chat_id, WELCOME_MESSAGE)
        return "ok"

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=256,
            temperature=0.2,
        )
        translated = response.choices[0].message.content.strip()
        send_message(chat_id, translated)
    except Exception as e:
        send_message(chat_id, f"Ошибка перевода: {e}")

    return "ok"

# Отправка сообщений в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# Запуск на нужном порту (для Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
