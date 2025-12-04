from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. НОВЕ: Початкове меню вибору складності ---
DIFFICULTY_CHOICE = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Складне завдання (Код, Дебагінг)"), 
            KeyboardButton(text="Просте питання (Загальна допомога)")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="J.A.R.V.I.S., оберіть тип завдання..."
)

# --- 2. ІСНУЮЧЕ (ПЕРЕЙМЕНОВАНО): Меню для складних завдань (Код) ---
CODE_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Аналіз Коду (Огляд)"), 
            KeyboardButton(text="Розпочати Дебагінг (FSM)")
        ],
        [
            KeyboardButton(text="Деконструкція Логіки (Пояснення)"), 
            KeyboardButton(text="Звіт Про Стан (Допомога)")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="J.A.R.V.I.S., оберіть функцію..."
)

# --- Вбудовані клавіатури (Для підтвердження дії) ---
def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Генерує клавіатуру підтвердження для Code Review або Explain."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=" Підтвердити", callback_data=f"confirm_{action}"),
                InlineKeyboardButton(text=" Скасувати", callback_data="cancel_action")
            ]
        ]
    )
    
