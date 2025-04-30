import os
import requests
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = os.getenv('API_TOKEN')

if not API_TOKEN:
    raise ValueError("API_TOKEN не найден! Задайте переменную окружения API_TOKEN.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def is_cyrillic(text):
    return any('А' <= c <= 'я' or c == 'ё' or c == 'Ё' for c in text)

def translate(text, source, target):
    url = "https://libretranslate.com/translate"
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    response = requests.post(url, data=payload)
    return response.json()['translatedText']

@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text.strip()
    if is_cyrillic(text):
        # Русский -> Сербский (латиница)
        translated = translate(text, "ru", "sr")
        await message.reply(translated)
    else:
        # Сербский (латиница) -> Русский (кириллица)
        translated = translate(text, "sr", "ru")
        await message.reply(translated)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)