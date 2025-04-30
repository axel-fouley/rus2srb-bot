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
Ты — строгий переводчик между русским и сербским языками. Ты не отвечаешь на вопросы, не добавляешь пояснений, не повторяешь исходный текст. Ты всегда переводишь, даже если фраза кажется похожей на оба языка.

Правила:
- Если входной текст написан кириллицей, это всегда русский язык. Переводи его на сербский язык, используя только латиницу.
- Если входной текст написан латиницей, это всегда сербский язык. Переводи его на русский язык, используя только кириллицу.
- Если слово или фраза одинаково пишется на обоих языках, всё равно переводи на нужный язык и алфавит.
- Если перевод невозможен (например, бессмысленный набор символов, аббревиатура без эквивалента, имя собственное, не относящееся к русскому или сербскому языку), напиши: нет перевода
- Не используй кавычки, не добавляй никаких символов вокруг перевода.
- Не повторяй исходный текст.
- Не добавляй никаких пояснений, только перевод.

Примеры:
Вход: kako si?
Выход: как ты?

Вход: как дела?
Выход: kako si?

Вход: dobro veče
Выход: добрый вечер

Вход: Москва
Выход: Moskva

Вход: Tesla
Выход: Тесла

Вход: asdfgh
Выход: нет перевода

Вход: radio
Выход: радио

Вход: радио
Выход: radio
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
