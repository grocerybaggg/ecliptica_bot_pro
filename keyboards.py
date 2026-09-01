from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_URL, CONTACT_USERNAME

def home_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать услугу", callback_data="menu:services")],
        [InlineKeyboardButton(text="Отзывы", url=CHANNEL_URL)],
    ])

def services_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Нашёл нужное", callback_data="svc:found")],
        [InlineKeyboardButton(text="Не нашёл нужное", callback_data="svc:notfound")],
        [InlineKeyboardButton(text="Назад", callback_data="back:start")],
    ])

def custom_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, продолжим", callback_data="custom:yes")],
        [InlineKeyboardButton(text="Нет, спасибо", callback_data="custom:no")],
        [InlineKeyboardButton(text="Назад", callback_data="back:services")],
    ])

def university_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back:services")]
    ])

def faculty_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back:university")]
    ])

def task_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="task:done")],
        [InlineKeyboardButton(text="Назад", callback_data="back:faculty")],
    ])

def contact_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="contact:skip")],
        [InlineKeyboardButton(text="Назад", callback_data="back:task")],
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, отправить", callback_data="req:send")],
        [InlineKeyboardButton(text="Исправить", callback_data="req:edit")],
        [InlineKeyboardButton(text="Нет, отменить", callback_data="req:cancel")],
    ])

def final_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Написать напрямую",
            url=f"https://t.me/{CONTACT_USERNAME.lstrip('@')}"
        )],
        [InlineKeyboardButton(text="Наш канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="В начало", callback_data="menu:home")],
    ])

def thanks_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В начало", callback_data="menu:home")],
        [InlineKeyboardButton(text="Наш канал", url=CHANNEL_URL)],
    ])

def admin_kb(request_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data=f"admin:accept:{request_id}"),
            InlineKeyboardButton(text="Уточнить", callback_data=f"admin:contact:{request_id}"),
        ],
        [
            InlineKeyboardButton(text="Отклонить", callback_data=f"admin:reject:{request_id}"),
            InlineKeyboardButton(text="Завершить", callback_data=f"admin:done:{request_id}"),
        ],
    ])
