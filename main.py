from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging

# Вставь сюда свой токен
API_TOKEN = "7612081343:AAHNPmF8Mepb_Bl1Z817raoFy99wPOvd7ZM"

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь предложений
offers = {
    "Интервью в особенной локации": "🎥 - это самое дорогое из предложений в силу своей высокой затратной части. Это может быть интервью на воздушном шаре, в кабриолете на трассе, на яхте с выходом в залив, в бассейне на крыше, в Хогвартс экспрессе и т. д. Под каждого героя подбирается локация, костюмы, аксессуары. Интервью размещается в подкасте на Ютюб, в телеграм-канале и на ТВ. Стоимость от 150 000 руб.",
    "Интервью в студии": "📺 - обычное студийное интервью. Туда входит красивая студия, мейк, съемка на 3 камеры, монтаж и размещение на тех же платформах — от 65 000 руб.",
    "Репортаж на ТВ": "📻 - обсуждается персонально. Здесь нужен информационный повод. Но его можно и создать. От 100 000 руб.",
    "Радио-интервью": "🎙 - интервью на федеральной радиостанции с охватом на 50 млн слушателей. Хронометраж 10 минут.  120 000 руб.",
    "Рекламный пост": "📢 - рекламный пост в тг-канале + в инстаграм (50к подписчиков) — от 10 000 руб.",
    "Медиаконсультация": "🤝 2 часа вы отвечаете на вопросы Екатерины и получаете портрет личного бренда, ваши фишки и медиаплан продвижения и продаж — 15 000 руб.",
    "Онлайн-курсы": "📚 Курс по голосу — 50 000 руб., остальные — от 3 000 руб."
}

# Хранилище выбора пользователя
user_choices = {}

# Генерация кнопок с галочками
def generate_keyboard(user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    selected = user_choices.get(user_id, [])
    for item in offers:
        checked = "✅" if item in selected else "☐"
        kb.add(InlineKeyboardButton(f"{checked} {item}", callback_data=f"toggle_{item}"))
    kb.add(InlineKeyboardButton("✉️ Готово", callback_data="submit"))
    return kb

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_choices[user_id] = []
    await message.answer(
        "Привет, я бот Екатерины Седовой.\n\n"
        "Могу помочь вам с медиапродвижением и не только.\n"
        "Выберите интересующие направления (можно несколько) и затем нажмите кнопку готово для подробной информации:",
        reply_markup=generate_keyboard(user_id)
    )

# Обработка нажатия на чекбоксы
@dp.callback_query_handler(lambda c: c.data.startswith("toggle_"))
async def toggle_selection(callback_query: types.CallbackQuery):
    item = callback_query.data.replace("toggle_", "")
    uid = callback_query.from_user.id
    if uid not in user_choices:
        user_choices[uid] = []
    if item in user_choices[uid]:
        user_choices[uid].remove(item)
    else:
        user_choices[uid].append(item)
    await callback_query.message.edit_reply_markup(reply_markup=generate_keyboard(uid))
    await callback_query.answer()

# Обработка кнопки "Готово"
@dp.callback_query_handler(lambda c: c.data == "submit")
async def handle_submission(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    selected = user_choices.get(uid, [])

    if not selected:
        await callback_query.answer("Выберите хотя бы один пункт.", show_alert=True)
        return

    response = "📝 Вы выбрали:\n\n"
    for item in selected:
        response += f"{offers[item]}\n\n"

    await bot.send_message(uid, response.strip())

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✅ Да, интересно. Связаться с Екатериной", url="https://t.me/Hecate_Media"),
        InlineKeyboardButton("⏳ Подумать и вернуться позже", callback_data="later")
    )

    await bot.send_message(uid, "Продолжаем?", reply_markup=kb)

# Обработка кнопки "Подумать"
@dp.callback_query_handler(lambda c: c.data == "later")
async def handle_later(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Спасибо за уделённое время! Вы всегда можете вернуться к боту и пройти опрос повторно.")

# Точка входа
if __name__ == '__main__':
    print("Бот запущен. Ожидаю команду /start...")
    executor.start_polling(dp, skip_updates=True)
