from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

#Начало теста
start_test = InlineKeyboardButton(text="Пройти тест", callback_data="start")
start_rows = [[start_test]]
IKBStart = InlineKeyboardMarkup(inline_keyboard=start_rows)

#Кнопка перехода на следующий вопрос
next_test = InlineKeyboardButton(text="Далее", callback_data="next")
next_rows = [[next_test]]
IKBNext = InlineKeyboardMarkup(inline_keyboard=next_rows)

#Кнопки для отправки номера
phone_true = KeyboardButton(text="Отправить номер", request_contact=True)
phone_false = KeyboardButton(text="Не отправлять")
phone_rows = [[phone_true], [phone_false]]
KBPhone = ReplyKeyboardMarkup(keyboard=phone_rows, resize_keyboard=True, one_time_keyboard=True)

#Кнопки для указания, есть ли ребенок
child_true = InlineKeyboardButton(text="Хочу также получать материалы для детей", callback_data="True")
child_false = InlineKeyboardButton(text="Спасибо, не нужно", callback_data="False")
child_rows = [[child_true], [child_false]]
IKBChild = InlineKeyboardMarkup(inline_keyboard=child_rows)