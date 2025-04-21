import json
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Command
from aiogram.utils.executor import start_webhook
from datetime import datetime, timedelta
import asyncio

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Вставь сюда свой токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Файл для хранения ответов
RESPONSES_FILE = "responses.json"

# Тематики и сложности
scenarios = [
    {"topic": "Бизнес", "difficulty": "🟡 Средний", "situation": "Конкурент запускает такой же продукт, как у тебя, но на 30% дешевле."},
    {"topic": "Политика", "difficulty": "🔴 Сложный", "situation": "Президент неожиданно уходит в отставку. Через 3 месяца — выборы."},
    {"topic": "Спорт", "difficulty": "🟢 Лёгкий", "situation": "Твоя любимая команда проигрывает финал. Ты — тренер. Что делаешь дальше?"},
    {"topic": "Жизнь", "difficulty": "🟢 Лёгкий", "situation": "Ты решаешь переехать в другой город без чёткого плана."},
    {"topic": "Экономика", "difficulty": "🔴 Сложный", "situation": "Цены на нефть резко падают до минимума за 10 лет. Ты — министр экономики."},
    {"topic": "Конфликт", "difficulty": "🟡 Средний", "situation": "Партнёр по бизнесу хочет выйти из проекта, угрожая судом."},
    {"topic": "Новости", "difficulty": "🟡 Средний", "situation": "Соцсети массово блокируют аккаунты, включая твой. Ты — публичная личность."}
]

# Загружаем ответы
try:
    with open(RESPONSES_FILE, "r") as f:
        responses = json.load(f)
except FileNotFoundError:
    responses = {}

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я буду присылать тебе ежедневные интеллектуальные задания. Напиши /brainboost, чтобы начать.")

@dp.message_handler(commands=["brainboost"])
async def daily_challenge(message: types.Message):
    scenario = random.choice(scenarios)
    text = f"🧠 <b>Интеллект-день</b>
"            f"📚 Тема: <b>{scenario['topic']}</b>
"            f"🔥 Сложность: <b>{scenario['difficulty']}</b>

"            f"✨ Ситуация:
<blockquote>{scenario['situation']}</blockquote>

"            f"▶️ Придумай 3 сценария (позитивный, негативный, нестандартный) по 3 шага. Напиши свой ответ через команду: /ответ"
    await message.reply(text, parse_mode=ParseMode.HTML)

@dp.message_handler(Command("ответ"))
async def save_response(message: types.Message):
    user_id = str(message.from_user.id)
    user_response = message.get_args()
    if not user_response:
        await message.reply("Напиши свой ответ после команды /ответ")
        return
    if user_id not in responses:
        responses[user_id] = []
    responses[user_id].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "response": user_response
    })
    with open(RESPONSES_FILE, "w") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    await message.reply("Ответ сохранён! 📝")

@dp.message_handler(commands=["моимышления"])
async def show_responses(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in responses or not responses[user_id]:
        await message.reply("У тебя пока нет сохранённых ответов.")
        return
    text = "📝 <b>Твои прошлые ответы:</b>
"
    for entry in responses[user_id][-5:]:  # последние 5
        text += f"
<b>{entry['date']}</b>
{entry['response']}
"
    await message.reply(text, parse_mode=ParseMode.HTML)

# Авторассылка (если хостинг поддерживает background tasks)
async def scheduled_challenge():
    await bot.wait_until_ready()
    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:
            scenario = random.choice(scenarios)
            text = f"🧠 <b>Интеллект-день</b>
"                    f"📚 Тема: <b>{scenario['topic']}</b>
"                    f"🔥 Сложность: <b>{scenario['difficulty']}</b>

"                    f"✨ Ситуация:
<blockquote>{scenario['situation']}</blockquote>

"                    f"▶️ Придумай 3 сценария (позитивный, негативный, нестандартный) по 3 шага. Напиши свой ответ через команду: /ответ"
            for user_id in responses.keys():
                try:
                    await bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.HTML)
                except:
                    continue
        await asyncio.sleep(60)  # проверка каждую минуту

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.create_task(scheduled_challenge())  # Включить, если на сервере поддерживаются фоновые задачи
    executor.start_polling(dp, skip_updates=True)
