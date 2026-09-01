from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from config import SERVICES
from keyboards import services_kb, custom_kb, home_kb, university_kb
from states import RequestForm

router = Router()

def services_text():
    parts = ["Промежуточные работы:"]
    parts.append("\n".join(f"• {x}" for x in SERVICES["Промежуточные работы"]))
    parts += ["", "Конечные работы:"]
    parts.append("\n".join(f"• {x}" for x in SERVICES["Конечные работы"]))
    parts += ["", "Цена зависит от ТЗ вашей работы."]
    return "\n".join(parts)

@router.callback_query(F.data == "menu:services")
async def services(callback: CallbackQuery):
    await callback.message.edit_text(services_text(), reply_markup=services_kb())
    await callback.answer()

@router.callback_query(F.data == "svc:notfound")
async def not_found(callback: CallbackQuery):
    await callback.message.edit_text(
        "Если ты не нашёл ничего подходящего в списке, то ты можешь "
        "написать ТЗ своего задания — и мы его сделаем.\n\nПродолжим?",
        reply_markup=custom_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "custom:no")
async def custom_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Спасибо за уделённое время\n\n"
        "Если передумаешь или появится другая задача — просто нажми /start, мы на связи.",
        reply_markup=home_kb()
    )
    await callback.answer()

@router.callback_query(F.data.in_({"svc:found", "custom:yes"}))
async def begin_request(callback: CallbackQuery, state: FSMContext):
    source = "из списка" if callback.data == "svc:found" else "своё ТЗ"
    await state.clear()
    await state.update_data(source=source, file_ids=[], task="")
    await state.set_state(RequestForm.university)
    await callback.message.edit_text(
        "Тогда заполни заявку для выполнения задания:\n\n"
        "С какого ты университета?",
        reply_markup=university_kb()
    )
    await callback.answer()

@router.callback_query(F.data == "back:start")
async def back_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from handlers.start import TEXT
    await callback.message.edit_text(TEXT, reply_markup=home_kb())
    await callback.answer()

@router.callback_query(F.data == "back:services")
async def back_services(callback: CallbackQuery):
    await callback.message.edit_text(services_text(), reply_markup=services_kb())
    await callback.answer()
