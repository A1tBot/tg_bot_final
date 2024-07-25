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
@router.message(F.text == 'Старт')
async def botStart(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(id=message.from_user.id)
    await state.update_data(fName = message.from_user.first_name)
    await message.answer(text=messages['non_QA']['introduction'], reply_markup=tg_keyboard.IKBStart)
    await state.set_state(tg_states.Order.pAge)
    #print(f'LOG: User: {message.from_user.id} STARTED test')


#Выбор возраста
@router.callback_query(tg_states.Order.pAge)
async def botPAge(call: CallbackQuery, state: FSMContext):
    await call.message.answer_poll(question=messages['QA']['QA_age']['question'],
                                    options=messages['QA']['QA_age']['answer'],
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
    await call.message.answer_poll(question=messages['QA']['QA_level']['question'].format(messages['QA']['QA_level']['cases'][data['languagesTemp'][0]]),
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
    await call.message.answer_poll(question=messages['QA']['QA_purpose']['question'],
                                    options=messages['QA']['QA_purpose']['answer'],
                                    is_anonymous=False,
                                    allows_multiple_answers=True,
                                    reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.purpose)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(purpose = poll.option_ids)
    await state.set_state(tg_states.Order.phone)


#Попытка попросить номер телефона
@router.callback_query(tg_states.Order.phone)
async def botPhone(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text=messages['QA']['QA_phone']['question'], reply_markup=tg_keyboard.KBPhone)
    await state.set_state(tg_states.Order.child)


#Обработка получения номера телефона и Попытка узнать есть ли ребенок
@router.message(tg_states.Order.child)
async def botChild(message: Message, state: FSMContext):
    if message.text == None:
        await state.update_data(phone = message.contact.phone_number)
    else:
        await state.update_data(phone = 'Не указано')

    await message.answer(text=messages['QA']['QA_child']['question'], reply_markup=tg_keyboard.IKBChild)
    await state.set_state(tg_states.Order.cProcess)


#Обработка данных о ребенке
@router.callback_query(tg_states.Order.cProcess)
async def botChildProcess(call: CallbackQuery, state: FSMContext):
    if call.data == 'True':
        await state.set_state(tg_states.Order.cAge)
        await botCAge(call, state)
    else:
        await state.update_data(child = 'Не указано')
        await state.set_state(tg_states.Order.end)
        await botEnd(call, state)


#Если есть ребенок, то узнаем возраст
@router.callback_query(tg_states.Order.cAge)
async def botCAge(call: CallbackQuery, state: FSMContext):
    await call.message.answer_poll(question=messages['QA']['QA_child_age']['question'],
                                    options=messages['QA']['QA_child_age']['answer'],
                                    is_anonymous=False,
                                    allows_multiple_answers=False,
                                    reply_markup=tg_keyboard.IKBNext)
@router.poll_answer(tg_states.Order.cAge)
async def pollProcess(poll: PollAnswer, state: FSMContext):
    await state.update_data(child = poll.option_ids)
    await state.set_state(tg_states.Order.end)


#Обработка данных
@router.callback_query(tg_states.Order.end)
async def botEnd(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text=messages['non_QA']['end'].format('\n', '\n'))
    await state.update_data(date = f'{str(datetime.now().strftime("%d.%m.%Y"))} {str(datetime.now().strftime("%H:%M:%S"))}')
    
    #print(f'LOG: User: {message.from_user.id} ENDED test')
    
    data = await state.get_data()

    #Преобразование индексов Возраста, Языка, Уровней, Цели, Возраста ребенка в текст
    data['pAge'] = messages['QA']['QA_age']['answer'][data['pAge'][0]]
    data['languages'] = [messages['QA']['QA_language']['answer'][i] for i in data['languages']]
    data['levels'] = [messages['QA']['QA_level']['answer'][i] for i in data['levels']]
    data['purpose'] = [messages['QA']['QA_purpose']['answer'][i] for i in data['purpose']]
    if data['child'] != 'Не указано': data['child'] = messages['QA']['QA_child_age']['answer'][data['child'][0]]

    #print(f'LOG: User {message.from_user.id} data FORMATTED:\n{data}')
    await formatData(data)
    await state.clear()
    #print(f'LOG: User {message.from_user.id} data CLEAR')
    
    