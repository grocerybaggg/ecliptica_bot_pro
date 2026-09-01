import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
CONTACT_USERNAME = os.getenv("CONTACT_USERNAME", "https://t.me/EclipticaStudy").strip()
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/ecliptica_otzyvy").strip()

# Необязательно: Telegram ID администраторов через запятую.
# Пример: ADMIN_USER_IDS=123456789,987654321
ADMIN_USER_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",")
    if x.strip().isdigit()
}

MAX_UNIVERSITY = 100
MAX_FACULTY = 100
MAX_TASK = 2000
MAX_FILES = 10
REQUEST_COOLDOWN_SECONDS = 300

SERVICES = {
    "Промежуточные работы": [
        "задания по информатике",
        "работы в Word и Excel",
        "презентации",
        "цифровая грамотность",
        "юридическая информатика",
    ],
    "Конечные работы": [
        "курсовые",
        "рефераты",
        "практика",
        "отчёты по практике",
        "научные статьи",
    ],
}
