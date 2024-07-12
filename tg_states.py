from aiogram.fsm.state import StatesGroup, State

class Order(StatesGroup):
    pType = State()
    pAge = State()
    language = State()
    level = State()
    purpose = State()
    end = State()