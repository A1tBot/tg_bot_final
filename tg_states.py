from aiogram.fsm.state import StatesGroup, State

class Order(StatesGroup):
    pAge = State()
    language = State()
    level = State()
    purpose = State()
    phone = State()
    child = State()
    cProcess = State()
    cAge = State()
    end = State()