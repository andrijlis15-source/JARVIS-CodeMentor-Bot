import os
from dotenv import load_dotenv

# Завантаження змінних оточення з файлу .env (якщо він є)
load_dotenv()

# --- Налаштування Telegram та Gemini ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Налаштування AI ---
GEMINI_MODEL = "gemini-2.5-flash"

# --- Налаштування Бота ---
# Шлях до файлу для збереження ролей (це файл буде створений на Render)
CONFIG_FILE_PATH = "user_role_config.txt" 

# Системний промпт за замовчуванням (тепер він єдиний)
DEFAULT_SYSTEM_PROMPT = "Ти — J.A.R.V.I.S., високоінтелектуальний помічник, що надає точні та вичерпні відповіді українською мовою. Твій стиль професійний, лаконічний та дружній."
