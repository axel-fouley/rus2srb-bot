import os
import openai
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = os.getenv("API_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_TOKEN:
    raise ValueError("API_TOKEN не найден! Задайте переменную окружения API_TOKEN.")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY не найден! Задайте переменную окружения OPENROUTER_API_KEY.")

client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

PROMPT = """
Ты — профессиональный переводчик между русским и сербским языками.

- Если текст на кириллице — это русский, переводи на сербский (латиница).
- Если текст на латинице — это сербский, переводи на русский (кириллица).
- Не повторяй исходный текст.
- Не используй тире, кавычки и другие символы вокруг перевода.
- Если перевод невозможен, напиши: нет перевода.
- Ответь только переводом, без исходного текста, тире, кавычек и пояснений.

Примеры:
kako si? — как ты?
kako je život? — как жизнь?
как дела? — kako si?
dobro veče — добрый вечер
Москва — Moskva
Tesla — Тесла
asdfgh — нет перевода
radio — радио
радио — radio
Переведи: "{}"
"""

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def clean_translation(text):
    # Убирает кавычки и пробелы в начале и конце строки
    return text.strip().strip('"').strip("'").strip()

def translate_ai(text):
    prompt = PROMPT.format(text)
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": prompt}
        ],
        max_tokens=256,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text.strip()
    try:
        translated = translate_ai(text)
        translated = clean_translation(translated)
        await message.reply(translated)
    except Exception as e:
        await message.reply(f"Ошибка перевода: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
