# ECLIPTICA Bot — production-ready

## Требования
Python 3.11+.

## Установка

Windows:
```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env`.

Заполните:
- BOT_TOKEN — токен от @BotFather
- ADMIN_CHAT_ID — ID группы/супергруппы, куда приходят заявки
- CONTACT_USERNAME — ваш Telegram username
- CHANNEL_URL — канал отзывов

Рекомендуется заполнить ADMIN_USER_IDS — Telegram ID людей, которым разрешены
админские кнопки.

## Получение ADMIN_CHAT_ID

Добавьте бота в нужную группу, отправьте туда сообщение и получите ID группы
через Telegram-инструмент/бот для определения chat ID. Для супергруппы ID обычно
начинается с -100.

Бот должен иметь право отправлять сообщения и документы.

## Запуск

Windows:
```powershell
py bot.py
```

Linux/macOS:
```bash
python bot.py
```

База `ecliptica.db` создастся сама.

## Что реализовано

- /start сбрасывает FSM из любого состояния
- /cancel отменяет текущую заявку
- inline-навигация без лишнего спама
- сбор университета, факультета, ТЗ и нескольких документов
- до 10 файлов на заявку
- ограничение длины ввода
- подтверждение перед отправкой
- SQLite
- уникальный ID заявки
- источник заявки: "из списка" / "своё ТЗ"
- отправка заявки и файлов в админ-чат
- админские статусы: new → accepted/rejected → done
- уведомления пользователя
- проверка прав администратора
- одна активная заявка на пользователя
- 5-минутный cooldown между заявками
- обработка ошибок отправки уведомлений клиенту
- секреты вынесены в .env

## Важно

Не публикуйте `.env` и не отправляйте BOT_TOKEN в чат/репозиторий.
