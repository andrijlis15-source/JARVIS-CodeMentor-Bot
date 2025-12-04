
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from google import genai
from google.genai.errors import APIError
from aiogram.fsm.state import State 

from .config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT
from .states import JarvisStates
from .keyboards import DIFFICULTY_CHOICE, CODE_MENU, get_confirm_keyboard # Оновлено!

router = Router()

client = genai.Client(api_key=GEMINI_API_KEY)


async def generate_response(prompt: str) -> str:
    """Функція для взаємодії з Gemini API"""
    try:
        response_task = asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=[SYSTEM_PROMPT, prompt],
        )
        response = await asyncio.wait_for(response_task, timeout=30.0)
        return response.text
    except APIError as e:
        print(f"Gemini API Error: {e}")
        return " Виникла системна помилка (API). Спробуйте пізніше."
    except asyncio.TimeoutError:
        return " Час очікування відповіді від AI вичерпано. Спробуйте скоротити запит."


# --- 1. Обробник /start, /help та Звіт Про Стан ---
@router.message(F.text.in_({"/start", "/help", "Звіт Про Стан (Допомога)"}))
async def cmd_start_help(message: Message, state: FSMContext):
    await state.clear() 
    await message.answer(
        "Вітаю. Я J.A.R.V.I.S., ваш відданий помічник. \n\n"
        "Оберіть тип завдання, яке ви хочете виконати:",
        reply_markup=DIFFICULTY_CHOICE # Виводимо нове меню
    )

# --- 2. НОВИЙ: Перехід до меню складних завдань ---
@router.message(F.text == "Складне завдання (Код, Дебагінг)")
async def cmd_show_code_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ви обрали роботу з кодом. Оберіть функцію:",
        reply_markup=CODE_MENU
    )

# --- 3. НОВИЙ: Перехід до стану простого питання ---
@router.message(F.text == "Просте питання (Загальна допомога)")
async def cmd_start_simple_question(message: Message, state: FSMContext):
    await state.set_state(JarvisStates.waiting_for_simple_question)
    await message.answer(
        "Надішліть ваше запитання. Я спробую дати точну та лаконічну відповідь."
    )

# --- 4. НОВИЙ: Обробка простого питання ---
@router.message(JarvisStates.waiting_for_simple_question)
async def process_simple_question(message: Message, state: FSMContext):
    user_query = message.text
    
    prompt = f"Ти — J.A.R.V.I.S. Дай точну, лаконічну та вичерпну відповідь українською мовою на наступне загальне питання: '{user_query}'"
    
    await message.answer(" Аналізую ваше питання. Зачекайте...")
    
    ai_response = await generate_response(prompt)
    await message.answer(ai_response, reply_markup=DIFFICULTY_CHOICE) # Повертаємось до вибору складності
    
    await state.clear()

# --- 5. Обробник Initiate Debugging (FSM - Крок 1) ---
@router.message(F.text == "Розпочати Дебагінг (FSM)")
async def cmd_start_debug(message: Message, state: FSMContext):
    await state.set_state(JarvisStates.waiting_for_debug_code)
    await message.answer("Будь ласка, надішліть фрагмент коду для аналізу.")

# --- 6. Обробник FSM (Крок 2: отримання коду) ---
@router.message(JarvisStates.waiting_for_debug_code)
async def process_debug_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await state.set_state(JarvisStates.waiting_for_debug_description)
    await message.answer("= Тепер надайте короткий опис спостережуваної помилки або небажаної поведінки.")

# --- 7. Обробник FSM (Крок 3: отримання опису та фінальний виклик AI) ---
@router.message(JarvisStates.waiting_for_debug_description)
async def process_debug_description(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data.get("code")
    description = message.text
    
    prompt = f"Як J.A.R.V.I.S., виконай дебагінг наступного коду. Точний опис помилки: '{description}'. Код:\n\n```\n{code}\n```"
    
    await message.answer(" Аналізую структуру та опис несправності. Зачекайте...")
    
    ai_response = await generate_response(prompt)
    await message.answer(ai_response, reply_markup=DIFFICULTY_CHOICE) # Повертаємось до вибору складності
    
    await state.clear() 


# --- 8. Обробник Analyze Code (Review) та Deconstruct Logic (Explain) ---
@router.message(F.text.in_({"Аналіз Коду (Огляд)", "Деконструкція Логіки (Пояснення)"}))
async def cmd_start_single_step_action(message: Message, state: FSMContext):
    action = "review" if "Огляд" in message.text else "explain"
    
    if action == "review":
        await state.set_state(JarvisStates.waiting_for_review_code)
        instruction = "Надішліть код для детального огляду (Code Review)."
    else:
        await state.set_state(JarvisStates.waiting_for_explain_code)
        instruction = "Надішліть код, який потрібно пояснити (Deconstruct Logic)."
                   
    await message.answer(f" {instruction}")


@router.message(F.state.in_([JarvisStates.waiting_for_review_code, JarvisStates.waiting_for_explain_code]))
async def process_single_step_code(message: Message, state: FSMContext):
    current_state = await state.get_state()
    action = "review" if current_state == JarvisStates.waiting_for_review_code.state else "explain"
    
    await state.update_data(code=message.text)
    
    await message.answer(
        f"Отримано код. Підтверджуєте відправку на {action.upper()}?",
        reply_markup=get_confirm_keyboard(action)
    )

# --- 9. Обробник Inline-Callbacks (Кнопки підтвердження/скасування) ---
@router.callback_query(F.data == "cancel_action")
async def cb_cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(" Дія скасована. Оберіть тип завдання.", reply_markup=DIFFICULTY_CHOICE) # Повертаємось до вибору складності
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_"))
async def cb_confirm_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    data = await state.get_data()
    code = data.get("code")
    
    if not code:
        await callback.message.edit_text("Помилка: Код не знайдено.", reply_markup=DIFFICULTY_CHOICE)
        await state.clear()
        return await callback.answer()
        
    await callback.message.edit_text(f" {action.upper()} розпочато. Аналізую...")
    await callback.answer()
    
    # Створення промпту для Gemini
    if action == "review":
        prompt = f"Виконай детальний огляд (Code Review) наступного коду, зосереджуючись на найкращих практиках, ефективності та потенційних вразливостях безпеки. Відповідай українською:\n\n```\n{code}\n```"
    elif action == "explain":
        prompt = f"Поясни наступний код простою та зрозумілою українською мовою, розбираючи логіку покроково. Код:\n\n```\n{code}\n```"
    
    ai_response = await generate_response(prompt)
    await callback.message.edit_text(f" Результат {action.upper()}:\n\n{ai_response}", reply_markup=DIFFICULTY_CHOICE) # Повертаємось до вибору складності
    
    await state.clear()
