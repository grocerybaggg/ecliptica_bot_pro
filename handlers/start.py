from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards import home_kb

router = Router()

TEXT = """E C L I P T I C A — это бот для помощи в учёбе.

Далее ты можешь найти услугу, которая подойдёт тебе, и посмотреть отзывы наших клиентов."""

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXT, reply_markup=home_kb())

@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущая заявка отменена.", reply_markup=home_kb())

@router.callback_query(F.data == "menu:home")
async def home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(TEXT, reply_markup=home_kb())
    await callback.answer()
