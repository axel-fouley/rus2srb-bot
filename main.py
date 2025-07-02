import os
import openai
import requests
from flask import Flask, request

# Загружаем переменные окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
URL_SECRET = os.getenv("URL_SECRET")  # пример: abc12345xyz

# Проверка наличия переменных
if not TOKEN:
    raise ValueError("Переменная TELEGRAM_TOKEN не задана")
if not OPENROUTER_API_KEY:
    raise ValueError("Переменная OPENROUTER_API_KEY не задана")
if not URL_SECRET:
    raise ValueError("Переменная URL_SECRET не задана")

# Инициализация Flask-приложения
app = Flask(__name__)

# Инициализация OpenRouter
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

# Webhook
@app.route(f"/{URL_SECRET}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text")

    if not text:
        return "ok"

    prompt = PROMPT + text.strip()

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini-2024-07-18",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=256,
            temperature=0.2,
        )
        translated = response.choices[0].message.content.strip()
        send_message(chat_id, translated)
    except Exception as e:
        send_message(chat_id, f"Ошибка перевода: {e}")

    return "ok"

# Функция отправки сообщения в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# Главная страница для Render проверки
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# Запуск приложения на нужном порту
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render задаёт переменную PORT
    app.run(host="0.0.0.0", port=port)
