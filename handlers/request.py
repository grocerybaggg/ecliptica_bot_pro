import json
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import (
    ADMIN_CHAT_ID,
    CONTACT_USERNAME,
    CHANNEL_URL,
    MAX_UNIVERSITY,
    MAX_FACULTY,
    MAX_TASK,
    MAX_FILES,
    REQUEST_COOLDOWN_SECONDS,
)
from states import RequestForm
from keyboards import (
    task_kb,
    contact_kb,
    confirm_kb,
    final_kb,
    services_kb,
    faculty_kb,
    university_kb,
)
from database import (
    create_request,
    has_active_request,
    get_last_request_time,
)

router = Router()


async def answer_back(target, text, reply_markup):
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text,
            reply_markup=reply_markup,
        )
    else:
        await target.answer(
            text,
            reply_markup=reply_markup,
        )


# ============================================================
# УНИВЕРСИТЕТ
# ============================================================

@router.message(RequestForm.university)
async def university(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Напиши название университета текстом, пожалуйста."
        )
        return

    text = message.text.strip()

    if not 1 <= len(text) <= MAX_UNIVERSITY:
        await message.answer(
            f"Название университета: от 1 до {MAX_UNIVERSITY} символов."
        )
        return

    await state.update_data(university=text)
    await state.set_state(RequestForm.faculty)

    await message.answer(
        "Какой факультет или направление?",
        reply_markup=faculty_kb(),
    )


@router.callback_query(
    RequestForm.university,
    F.data == "back:services",
)
async def back_from_university(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()

    from handlers.services import services_text

    await callback.message.edit_text(
        services_text(),
        reply_markup=services_kb(),
    )

    await callback.answer()


# ============================================================
# ФАКУЛЬТЕТ
# ============================================================

@router.message(RequestForm.faculty)
async def faculty(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Напиши факультет или направление текстом, пожалуйста."
        )
        return

    text = message.text.strip()

    if not 1 <= len(text) <= MAX_FACULTY:
        await message.answer(
            f"Факультет / направление: от 1 до {MAX_FACULTY} символов."
        )
        return

    await state.update_data(
        faculty=text,
        task="",
        file_ids=[],
    )

    await state.set_state(RequestForm.task)

    await message.answer(
        "Какая услуга тебе нужна? Опиши ТЗ и прикрепи файл или фотографию.\n\n"
        "Напиши, что нужно сделать, объём и срок сдачи.\n"
        "Если есть методичка, пример или скриншот — прикрепи его.\n\n"
        "Когда закончишь — нажми «Готово».",
        reply_markup=task_kb(),
    )


@router.callback_query(
    RequestForm.faculty,
    F.data == "back:university",
)
async def back_from_faculty(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(RequestForm.university)

    await callback.message.edit_text(
        "С какого ты университета?",
        reply_markup=university_kb(),
    )

    await callback.answer()


# ============================================================
# ФОТОГРАФИИ
# ============================================================

@router.message(
    RequestForm.task,
    F.photo,
)
async def task_photo(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    attachments = data.get("file_ids", [])

    if len(attachments) >= MAX_FILES:
        await message.answer(
            f"Можно прикрепить не больше {MAX_FILES} файлов и фотографий."
        )
        return

    # Берём фотографию максимального доступного качества
    photo_id = message.photo[-1].file_id

    attachment = {
        "type": "photo",
        "id": photo_id,
    }

    attachments.append(attachment)

    await state.update_data(
        file_ids=attachments,
    )

    await message.answer(
        f"📷 Фотография добавлена "
        f"({len(attachments)}/{MAX_FILES}).\n\n"
        "Можешь добавить ещё фото, файл или текст, "
        "либо нажать «Готово».",
        reply_markup=task_kb(),
    )


# ============================================================
# ДОКУМЕНТЫ
# ============================================================

@router.message(
    RequestForm.task,
    F.document,
)
async def task_document(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    attachments = data.get("file_ids", [])

    if len(attachments) >= MAX_FILES:
        await message.answer(
            f"Можно прикрепить не больше {MAX_FILES} файлов и фотографий."
        )
        return

    attachment = {
        "type": "document",
        "id": message.document.file_id,
    }

    attachments.append(attachment)

    await state.update_data(
        file_ids=attachments,
    )

    await message.answer(
        f"📎 Файл добавлен "
        f"({len(attachments)}/{MAX_FILES}).\n\n"
        "Можешь добавить ещё фото, файл или текст, "
        "либо нажать «Готово».",
        reply_markup=task_kb(),
    )


# ============================================================
# ТЕКСТ ТЗ
# ============================================================

@router.message(RequestForm.task)
async def task_text(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer(
            "Прикрепи фотографию/документ или напиши ТЗ текстом."
        )
        return

    text = message.text.strip()

    data = await state.get_data()

    old = data.get("task", "")

    combined = (
        f"{old}\n{text}".strip()
        if old
        else text
    )

    if len(combined) > MAX_TASK:
        await message.answer(
            f"ТЗ слишком длинное. Максимум — {MAX_TASK} символов."
        )
        return

    await state.update_data(
        task=combined,
    )

    await message.answer(
        "Текст ТЗ сохранён.\n\n"
        "Можешь добавить фото/файл/текст "
        "или нажать «Готово».",
        reply_markup=task_kb(),
    )


# ============================================================
# ГОТОВО С ТЗ
# ============================================================

@router.callback_query(
    RequestForm.task,
    F.data == "task:done",
)
async def task_done(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    if not data.get("task", "").strip():
        await callback.answer(
            "Опиши хотя бы в двух словах, что нужно сделать.",
            show_alert=True,
        )
        return

    await state.set_state(RequestForm.contact)

    await callback.message.edit_text(
        "Оставь почту или другой контакт для связи — "
        "или пропусти, тогда напишем тебе в Telegram.",
        reply_markup=contact_kb(),
    )

    await callback.answer()


@router.callback_query(
    RequestForm.task,
    F.data == "back:faculty",
)
async def back_from_task(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(RequestForm.faculty)

    await callback.message.edit_text(
        "Какой факультет или направление?",
        reply_markup=faculty_kb(),
    )

    await callback.answer()


# ============================================================
# КОНТАКТ
# ============================================================

@router.callback_query(
    RequestForm.contact,
    F.data == "contact:skip",
)
async def contact_skip(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(
        contact=CONTACT_USERNAME,
    )

    await show_confirm(
        callback,
        state,
    )


@router.message(RequestForm.contact)
async def contact_text(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer(
            "Напиши почту или другой контакт текстом, "
            "либо нажми «Пропустить»."
        )
        return

    contact = message.text.strip()

    if len(contact) > 200:
        await message.answer(
            "Контакт слишком длинный. Максимум — 200 символов."
        )
        return

    await state.update_data(
        contact=contact,
    )

    await show_confirm(
        message,
        state,
    )


@router.callback_query(
    RequestForm.contact,
    F.data == "back:task",
)
async def back_from_contact(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(RequestForm.task)

    await callback.message.edit_text(
        "Какая услуга тебе нужна? Опиши ТЗ и прикрепи "
        "файл или фотографию.\n\n"
        "Напиши, что нужно сделать, объём и срок сдачи.\n"
        "Если есть методичка, пример или скриншот — "
        "прикрепи его.\n\n"
        "Когда закончишь — нажми «Готово».",
        reply_markup=task_kb(),
    )

    await callback.answer()


# ============================================================
# ПОДТВЕРЖДЕНИЕ
# ============================================================

async def show_confirm(
    target,
    state: FSMContext,
):
    data = await state.get_data()

    task = data.get(
        "task",
        "",
    )

    short_task = (
        task
        if len(task) <= 200
        else task[:200] + "…"
    )

    attachments = data.get(
        "file_ids",
        [],
    )

    text = (
        "Проверь заявку:\n\n"
        f"Университет: {data.get('university')}\n"
        f"Факультет: {data.get('faculty')}\n"
        f"Задание: {short_task}\n"
        f"Вложения: {len(attachments)}\n"
        f"Контакт: "
        f"{data.get('contact', CONTACT_USERNAME)}\n"
        "Цена: назовём после просмотра ТЗ\n\n"
        "Всё верно? Отправляем заявку?"
    )

    await state.set_state(
        RequestForm.confirm,
    )

    await answer_back(
        target,
        text,
        confirm_kb(),
    )


# ============================================================
# РЕДАКТИРОВАНИЕ
# ============================================================

@router.callback_query(
    RequestForm.confirm,
    F.data == "req:edit",
)
async def req_edit(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    await state.set_state(
        RequestForm.university,
    )

    await callback.message.edit_text(
        "С какого ты университета?\n\n"
        f"Сейчас указано: "
        f"{data.get('university', '—')}",
        reply_markup=university_kb(),
    )

    await callback.answer()


# ============================================================
# ОТМЕНА
# ============================================================

@router.callback_query(
    RequestForm.confirm,
    F.data == "req:cancel",
)
async def req_cancel(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()

    await callback.message.edit_text(
        "Спасибо за уделённое время\n\n"
        "Если передумаешь или появится другая задача — "
        "просто нажми /start, мы на связи."
    )

    await callback.answer()


# ============================================================
# ОТПРАВКА ЗАЯВКИ
# ============================================================

@router.callback_query(
    RequestForm.confirm,
    F.data == "req:send",
)
async def req_send(
    callback: CallbackQuery,
    state: FSMContext,
):
    if ADMIN_CHAT_ID == 0:
        await callback.answer(
            "Бот ещё не настроен: ADMIN_CHAT_ID.",
            show_alert=True,
        )
        return

    user = callback.from_user

    if await has_active_request(user.id):
        await callback.answer(
            "У тебя уже есть активная заявка. "
            "Дождись её обработки.",
            show_alert=True,
        )
        return

    last = await get_last_request_time(user.id)

    if last:
        try:
            created = datetime.fromisoformat(last)

            elapsed = (
                datetime.now(timezone.utc) - created
            ).total_seconds()

            if elapsed < REQUEST_COOLDOWN_SECONDS:
                left = int(
                    REQUEST_COOLDOWN_SECONDS - elapsed
                )

                await callback.answer(
                    f"Новая заявка будет доступна "
                    f"через {left // 60 + 1} мин.",
                    show_alert=True,
                )
                return

        except ValueError:
            pass

    data = await state.get_data()

    attachments = data.get(
        "file_ids",
        [],
    )

    request_id = await create_request(
        user.id,
        user.username,
        data["university"],
        data["faculty"],
        data["task"],
        attachments,
        data.get(
            "contact",
            CONTACT_USERNAME,
        ),
        data.get(
            "source",
            "из списка",
        ),
    )

    username = (
        f"@{user.username}"
        if user.username
        else "без username"
    )

    created_at = datetime.now().strftime(
        "%d.%m.%Y %H:%M"
    )

    admin_text = (
        f"📥 <b>Заявка #{request_id} · "
        f"{created_at}</b>\n\n"
        f"Клиент: {username} "
        f"(id: <code>{user.id}</code>)\n"
        f"Университет: {data['university']}\n"
        f"Факультет: {data['faculty']}\n\n"
        f"<b>Задание:</b>\n"
        f"{data['task']}\n\n"
        f"Контакт: "
        f"{data.get('contact', 'не указан')}\n"
        f"Источник: "
        f"{data.get('source', 'из списка')}\n"
        f"Вложений: {len(attachments)}"
    )

    await callback.bot.send_message(
        ADMIN_CHAT_ID,
        admin_text,
        reply_markup=__import__(
            "keyboards"
        ).admin_kb(request_id),
    )

    # Отправляем вложения правильным методом
    for attachment in attachments:

        # Новый формат:
        # {"type": "photo", "id": "..."}
        # {"type": "document", "id": "..."}
        if isinstance(attachment, dict):

            attachment_type = attachment.get(
                "type"
            )

            attachment_id = attachment.get(
                "id"
            )

            if not attachment_id:
                continue

            if attachment_type == "photo":
                await callback.bot.send_photo(
                    ADMIN_CHAT_ID,
                    attachment_id,
                )

            elif attachment_type == "document":
                await callback.bot.send_document(
                    ADMIN_CHAT_ID,
                    attachment_id,
                )

        # Совместимость со старыми заявками,
        # где file_ids были обычными строками.
        elif isinstance(attachment, str):
            await callback.bot.send_document(
                ADMIN_CHAT_ID,
                attachment,
            )

    await state.clear()

    await callback.message.edit_text(
        "Ваша заявка отправлена!\n\n"
        f"С вами свяжутся о заказе, "
        f"или вы можете написать напрямую: "
        f"{CONTACT_USERNAME}\n\n"
        "Более того, вы можете подписаться "
        "на наш ТГК и узнать о скидках "
        "и основных ценах, а также почитать отзывы:\n"
        f"{CHANNEL_URL}",
        reply_markup=final_kb(),
    )

    await callback.answer(
        "Заявка отправлена!"
    )