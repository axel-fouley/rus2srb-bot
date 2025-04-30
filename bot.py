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

PROMPT = (
    "Ты профессиональный переводчик с сербского на русский и с русского на сербский. "
    "Определи язык входного текста (русский или сербский) и переведи его на другой язык. "
    "Для сербского используй только латиницу, для русского — только кириллицу. "
    "Не добавляй никаких пояснений, кавычек или исходного текста, только перевод.\n"
)

WELCOME_MESSAGE = (
    "Что может делать этот бот?\n\n"
    "Простой и удобный переводчик с русского на сербский и наоборот.\n"
    "Jednostavan i udoban prevodilac sa ruskog na srpski i obrnuto.\n\n"
    "by @AX_sites"
)

def clean_translation(text):
    return text.strip().strip('"').strip("'").strip()

def translate_ai(text):
    prompt = PROMPT + text
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": prompt}
        ],
        max_tokens=256,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(WELCOME_MESSAGE)

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
