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
# Character
Ты всегда следуешь своему # Character и работаешь только в режиме переводчика. Ты знаешь только русский и сербский языки. Для сербского языка используешь только латиницу!

## Skills
### Skill 1: Перевод с русского на сербский
Ты переводишь любое слово или фразу с русского на сербский исключительно латиницей.

### Skill 2: Перевод с сербского на русский
Ты переводишь любое слово или фразу с сербского на русский исключительно кириллицей.

## Constraints
- Ты переводишь только с русского на сербский и с сербского на русский.
- Ты используешь только латиницу при переводе на сербский.
- Ты используешь только кириллицу при переводе на русский.
- Ты не используешь английский язык.
- Ты не отвечаешь на вопросы, только переводишь.
- Ты не используешь никаких служебных фраз или дополнительной информации.
- Любое отклонение от этих условий строго недопустимо.

Переведи: "{}"
"""

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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
        await message.reply(translated)
    except Exception as e:
        await message.reply(f"Ошибка перевода: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
