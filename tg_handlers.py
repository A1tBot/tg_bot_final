from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PollAnswer, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from datetime import datetime

import tg_states
import tg_keyboard
from tg_firebase import formatData

import json

router = Router()

with open('QA_options.json', encoding='utf-8') as f:
    messages = json.load(f)


#Вступление. При выполнении команды /start
@router.message(F.text == '/start')
async def botStart(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(id=message.from_user.id)
    await state.update_data(fName = message.from_user.first_name)
    await state.update_data(lName = message.from_user.last_name)
    await message.answer(text=messages['non_QA']['introduction'], 
                         reply_markup=tg_keyboard.IKBStart)
    await state.set_state(tg_states.Order.pType)
    print(f'LOG: User: {message.from_user.id} STARTED test')


#Выбор типа. Для себя, Для ребенка
@router.callback_query(tg_states.Order.pType)
async def botPType(call: CallbackQuery, state: FSMContext):
    await call.message.answer_poll(question=messages['QA']['QA_type']['question'],
                                   options=messages['QA']['QA_type']['answer'],
                                   is_anonymous=False,
                                   allows_multiple_answers=False,
                                   reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.pType)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(pType = poll.option_ids)
    await state.set_state(tg_states.Order.pAge)


#Выбор возраста. Взависимости от типа.
@router.callback_query(tg_states.Order.pAge)
async def botPAge(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['pType'][0] == 0:
        await call.message.answer_poll(question=messages['QA']['QA_age_me']['question'],
                                       options=messages['QA']['QA_age_me']['answer'],
                                       is_anonymous=False,
                                       allows_multiple_answers=False,
                                       reply_markup=tg_keyboard.IKBNext)
    elif data['pType'][0] == 1:
        await call.message.answer_poll(question=messages['QA']['QA_age_child']['question'],
                                       options=messages['QA']['QA_age_child']['answer'],
                                       is_anonymous=False,
                                       allows_multiple_answers=False,
                                       reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.pAge)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(pAge = poll.option_ids)
    await state.set_state(tg_states.Order.language)


#Выбор языков
@router.callback_query(tg_states.Order.language)
async def botLanguage(call: CallbackQuery, state: FSMContext):
    await call.message.answer_poll(question=messages['QA']['QA_language']['question'],
                                   options=messages['QA']['QA_language']['answer'],
                                   is_anonymous=False,
                                   allows_multiple_answers=True,
                                   reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.language)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(languages = poll.option_ids)
    await state.update_data(languagesTemp = poll.option_ids.copy())
    data = await state.get_data()
    data['languagesTemp'].append(9999)
    await state.set_state(tg_states.Order.level)


#Выбор уровня владения определнным языком. Взависимости от выбранных языков
@router.callback_query(tg_states.Order.level)
async def botLevel(call: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await call.message.answer_poll(question=' '.join([messages['QA']['QA_level']['question'], 
                                                      messages['QA']['QA_level']['cases'][data['languagesTemp'][0]]]),
                                   options=messages['QA']['QA_level']['answer'],
                                   is_anonymous=False,
                                   allows_multiple_answers=False,
                                   reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.level)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    data = await state.get_data()
    data['languagesTemp'].pop(0)

    if 'levels' in data:
        data['levels'].append(poll.option_ids[0])
    else:
        await state.update_data(levels=poll.option_ids)

    if data['languagesTemp'][0] != 9999:
        await state.set_state(tg_states.Order.level)
    else:
        await state.set_state(tg_states.Order.purpose)


#Выбор целей изучения языка. Взависимости от типа.
@router.callback_query(tg_states.Order.purpose)
async def botPurpose(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if data['pType'][0] == 0:
        await call.message.answer_poll(question=messages['QA']['QA_purpose_me']['question'],
                                       options=messages['QA']['QA_purpose_me']['answer'],
                                       is_anonymous=False,
                                       allows_multiple_answers=True,
                                       reply_markup=tg_keyboard.IKBNext)
    elif data['pType'][0] == 1:
        await call.message.answer_poll(question=messages['QA']['QA_purpose_child']['question'],
                                       options=messages['QA']['QA_purpose_child']['answer'],
                                       is_anonymous=False,
                                       allows_multiple_answers=True,
                                       reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.purpose)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(purpose = poll.option_ids)
    await state.set_state(tg_states.Order.end)


#Попытка попросить номер телефона
@router.callback_query(tg_states.Order.end)
async def botPhone(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text=messages['QA']['QA_phone']['question'],
                              reply_markup=tg_keyboard.KBPhone)
    await state.set_state(tg_states.Order.end)


#Обработка данных
@router.message(tg_states.Order.end)
async def botEnd(message: Message, state: FSMContext):
    if message.text != 'Не отправлять':
        await state.update_data(phone = message.contact.phone_number)
    else:
        await state.update_data(phone = None)
    await message.answer(text=messages['QA']['QA_end']['answer'],
                         reply_markup=ReplyKeyboardRemove())
    
    await state.update_data(date = f'{str(datetime.now().strftime("%d.%m.%Y"))} {str(datetime.now().strftime("%H:%M:%S"))}')
    
    print(f'LOG: User: {message.from_user.id} ENDED test')
    
    #Если имя или фамилия пользователя не указано
    data = await state.get_data()

    #Преобразование индексов для Возраста и Цели изучения в текст
    if data['pType'][0] == 0:
        data['pAge'] = messages['QA']['QA_age_me']['answer'][data['pAge'][0]]
        data['purpose'] = [messages['QA']['QA_purpose_me']['answer'][i] for i in data['purpose']]
    elif data['pType'][0] == 1:
        data['pAge'] = messages['QA']['QA_age_child']['answer'][data['pAge'][0]]
        data['purpose'] = [messages['QA']['QA_purpose_child']['answer'][i] for i in data['purpose']]

    #Преобразование индексов для типа пользователя в текст
    data['pType'] = messages['QA']['QA_type']['answer'][data['pType'][0]]

    #Преобразование индексов выбранных языков в текст
    data['languages'] = [messages['QA']['QA_language']['answer'][i] for i in data['languages']]

    #Преобразование индекосв уровней знаний выбранных языков в текст
    data['levels'] = [messages['QA']['QA_level']['answer'][i] for i in data['levels']]

    print(f'LOG: User {message.from_user.id} data FORMATTED:\n{data}')

    await formatData(data)
    await state.clear()
    print(f'LOG: User {message.from_user.id} data CLEAR')
    
    