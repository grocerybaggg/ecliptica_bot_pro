from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import ADMIN_CHAT_ID, ADMIN_USER_IDS
from database import set_status, get_request

router = Router()

async def authorized(callback: CallbackQuery):
    if callback.message.chat.id != ADMIN_CHAT_ID:
        return False
    # Если ADMIN_USER_IDS пуст, доступ ограничивается самим админ-чатом.
    return not ADMIN_USER_IDS or callback.from_user.id in ADMIN_USER_IDS

@router.callback_query(F.data.startswith("admin:"))
async def admin_action(callback: CallbackQuery):
    if not await authorized(callback):
        await callback.answer("Недостаточно прав.", show_alert=True)
        return

    _, action, request_id_raw = callback.data.split(":")
    request_id = int(request_id_raw)
    request = await get_request(request_id)

    if not request:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    status_text = {
        "accept": ("accepted", "принята в работу", "Ваша заявка #{id} принята в работу."),
        "reject": ("rejected", "отклонена", "По заявке #{id} пока не можем оказать услугу. "
                    "Если появится другая задача — нажмите /start."),
        "done": ("done", "завершена", "Работа по заявке #{id} завершена."),
    }

    if action in status_text:
        status, admin_label, user_text = status_text[action]
        await set_status(request_id, status)
        try:
            await callback.bot.send_message(
                request["user_id"], user_text.format(id=request_id)
            )
        except Exception:
            # Клиент мог запретить боту писать или удалить аккаунт.
            pass

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer(f"Заявка {admin_label}.")
        return

    if action == "contact":
        username = request.get("username")
        if username:
            await callback.answer(
                f"Клиент: @{username.lstrip('@')}", show_alert=True
            )
        else:
            await callback.answer(
                f"У клиента нет username.\nTelegram ID: {request['user_id']}",
                show_alert=True
            )
