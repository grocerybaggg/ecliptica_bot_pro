from aiogram.fsm.state import State, StatesGroup

class RequestForm(StatesGroup):
    university = State()
    faculty = State()
    task = State()
    contact = State()
    confirm = State()
