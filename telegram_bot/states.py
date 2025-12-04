from aiogram.fsm.state import State, StatesGroup

class JarvisStates(StatesGroup):
    # FSM States для складних завдань
    waiting_for_debug_code = State()
    waiting_for_debug_description = State()
    waiting_for_review_code = State()
    waiting_for_explain_code = State()
    
    #  СТАН для простих загальних питань
    waiting_for_simple_question = State()