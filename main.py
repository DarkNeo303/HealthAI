"""
======================================
        HealthAI Telegram Бот
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
import ai
import os
import time
import telebot
import threading
from typing import Union
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from support import checkInt, Switch, ram, stringToBool
from database import Patient, Doctor, getUser, History, Admin

# Инициализация
ai.initAi()
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

'''
======================================
            ОТКЛИКИ БОТА      
======================================
'''


# Обработчик Inline запросов врача
def callCheckDoctor(message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к администратору!',
                        message['user'])
        elif case('doctorAnonim'):
            pass
        elif case('patient'):
            pass
        elif case('qualification'):
            pass
        elif case('patientKick'):
            pass
        elif case('passchangePhoto'):
            pass
        elif case('doctorKick'):
            pass


# Обработчик Inline запросов пациента
def callCheckPatient(message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к администратору!',
                        message['user'])
        elif case('contactDoctor'):
            pass
        elif case('anonContactDoctor'):
            pass
        elif case('patientExtract'):
            pass
        elif case('patientDoctorKick'):
            pass


# Обработчик Inline запросов админа
def callCheckAdmin(message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к разработчику!',
                        message['user'])
        elif case('makeAdmin'):
            pass
        elif case('removeAdmin'):
            pass
        elif case('removeDoctor'):
            pass


# Обработчик Inline запросов
@bot.callback_query_handler(func=lambda call: True)
def callCheck(call: telebot.types.CallbackQuery):
    # Получаем пользователя
    user: Union[Patient, Doctor, type(None)] = getUser(int(call.message.text.split('|')[1]))
    # Если пользователь найден
    if user is not None and user.isExsist():
        # Получаем сообщение
        message: dict = {
            'user': user,
            'message': call.message.text.split('|')[0],
            'params': call.message.text.split('|')[:2]
        }
        # Если пользователь - админ
        if Admin(user).getAdmin() is not None:
            # Передаём параметр
            callCheckAdmin(message)
        else:
            # Если пользователь - пациент
            if isinstance(user, Patient):
                # Передаём параметр
                callCheckPatient(message)
            elif isinstance(user, Doctor):
                # Передаём параметр
                callCheckDoctor(message)


'''
======================================
        СИСТЕМНЫЕ ФУНКЦИИ БОТА        
======================================
'''


# Отправка сообщения
def sendMessage(message: str, to: Union[Patient, Doctor, int], self: Union[Patient, Doctor, str, None] = None,
                reply: Union[telebot.types.InlineKeyboardMarkup, telebot.types.ReplyKeyboardMarkup,
                telebot.types.ReplyKeyboardRemove(), type(None)] = None, photo: Union[bytes, type(None)] = None,
                parse_mode: str = 'html'):
    # Проверка типов
    if isinstance(self, Patient) or isinstance(self, Doctor):
        # Проверка типов
        if isinstance(to, Patient) or isinstance(to, Doctor):
            # Проверка языка
            if self.get()['lang'] == to.get()['lang']:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'], message, parse_mode)
                    else:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo, message, parse_mode)
                    else:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'],
                                         GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                         parse_mode)
                    else:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'],
                                         GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                         parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo,
                                       GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                       parse_mode)
                    else:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo,
                                       GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                       parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    bot.send_message(to, message, parse_mode)
                else:
                    # Отправляем сообщение
                    bot.send_message(to, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    bot.send_photo(to, photo, message, parse_mode)
                else:
                    # Отправляем фото
                    bot.send_photo(to, photo, message, parse_mode, reply_markup=reply)
    elif isinstance(self, type(None)):
        # Проверка типов
        if isinstance(to, Patient) or isinstance(to, Doctor):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    bot.send_message(to.get()['id'], message, parse_mode)
                else:
                    # Отправляем сообщение
                    bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    bot.send_photo(to.get()['id'], photo, message, parse_mode)
                else:
                    # Отправляем фото
                    bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    bot.send_message(to, message, parse_mode)
                else:
                    # Отправляем сообщение
                    bot.send_message(to, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    bot.send_photo(to, photo, message, parse_mode)
                else:
                    # Отправляем фото
                    bot.send_photo(to, photo, message, parse_mode, reply_markup=reply)
    elif isinstance(self, str):
        # Проверка типов
        if isinstance(to, Patient) or isinstance(to, Doctor):
            # Проверка языка
            if self == to.get()['lang']:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'], message, parse_mode)
                    else:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo, message, parse_mode)
                    else:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'],
                                         GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                         parse_mode)
                    else:
                        # Отправляем сообщение
                        bot.send_message(to.get()['id'],
                                         GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                         parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo,
                                       GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                       parse_mode)
                    else:
                        # Отправляем фото
                        bot.send_photo(to.get()['id'], photo,
                                       GoogleTranslator(source='auto', target=to.get()['lang']).translate(message),
                                       parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    bot.send_message(to, GoogleTranslator(source='auto', target=self).translate(message), parse_mode)
                else:
                    # Отправляем сообщение
                    bot.send_message(to, GoogleTranslator(source='auto', target=self).translate(message),
                                     parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    bot.send_photo(to, photo, GoogleTranslator(source='auto', target=self).translate(message),
                                   parse_mode)
                else:
                    # Отправляем фото
                    bot.send_photo(to, photo, GoogleTranslator(source='auto', target=self).translate(message),
                                   parse_mode, reply_markup=reply)


# Регистрация врача
def registerDoctor(message, step: int = 0):
    # Проверка состояния
    for case in Switch(step):
        if case(0):
            # Записываем квалификацию
            ram[message.from_user.id]['qualification'] = message.text
            # Регистрируем ответ
            ram[message.from_user.id]['document'] = None
            # Отправляем сообщение
            sendMessage("✔ Квалификация записана",
                        message.chat.id, ram[message.from_user.id]['lang'], reply=telebot.types.ReplyKeyboardRemove())
            # Проверка значения
            if stringToBool(os.getenv('VERIFY')):
                # Отправляем сообщение
                sendMessage("📑 Подтвердите квалификацию документом.\nДокумент будет проверен нейросетью. "
                            "В случае ошибки сообщите разработчику бота", message.chat.id,
                            ram[message.from_user.id]['lang'])
            else:
                # Создаём аккаунт
                Doctor(message.from_user.id).create(ram[message.from_user.id]['name'],
                                                    ram[message.from_user.id]['qualification'],
                                                    ram[message.from_user.id]['document'],
                                                    ram[message.from_user.id]['lang'],
                                                    ram[message.from_user.id]['phone'])
                # Удаляем пользователя
                ram.pop(message.from_user.id)
                # Отправляем сообщение
                sendMessage('✔ Аккаунт успешно зарегистрирован!', message.chat.id,
                            getUser(message.from_user.id), reply=telebot.types.ReplyKeyboardRemove())
        # Ломаем функцию
        break
    # Ломаем функцию
    return None


# Регистрация пациента
def registerPatient(message, step: int = 0, invited: Doctor = None):
    # Проверка состояния
    for case in Switch(step):
        if case(0):
            # Проверка ответа
            if checkInt(message.text):
                ram[message.from_user.id]['age'] = int(message.text)
            else:
                # Отправляем сообщение
                sendMessage("😐 Ответ не распознан, повторите попытку",
                            message.chat.id, ram[message.from_user.id]['lang'],
                            reply=telebot.types.ReplyKeyboardRemove())
                # Отправляем сообщение
                sendMessage('🔞 Укажите возраст', message.chat.id, ram[message.from_user.id]['lang'])
                # Если есть врач
                if invited is not None:
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, registerPatient, 0, invited)
                    break
                else:
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, registerPatient)
                    break
            # Клавиатура
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.KeyboardButton(text="👨 Мужской"),
                         telebot.types.KeyboardButton(text="👩 Мужской"))
            # Отправляем сообщение
            sendMessage('🤔 Укажите пол', message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
            # Регистрируем следующее событие
            bot.register_next_step_handler(message, registerPatient, 1)
            break
        elif case(1):
            # Записываем пол
            ram[message.from_user.id]['sex'] = 'мужской' in message.text.lower()
            try:
                # Создаём пользователя
                Patient(message.from_user.id).create(ram[message.from_user.id]['name'],
                                                     ram[message.from_user.id]['age'],
                                                     ram[message.from_user.id]['sex'], invited,
                                                     ram[message.from_user.id]['lang'],
                                                     ram[message.from_user.id]['phone'])
                # Отправляем сообщение
                sendMessage('✔ Аккаунт успешно зарегистрирован!', message.chat.id,
                            ram[message.from_user.id]['lang'], reply=telebot.types.ReplyKeyboardRemove())
            except Exception as e:
                # Отправляем сообщение
                sendMessage(f'❌ Ошибка при регистрации!\n\n💬 Ошибка: {e}', message.chat.id,
                            ram[message.from_user.id]['lang'], reply=telebot.types.ReplyKeyboardRemove())
            # Удаляем пользователя
            ram.pop(message.from_user.id)
            # Ломаем функцию
            break
    # Ломаем функцию
    return None


# Регистрация
def register(message, step: int = -1, invited: Doctor = None):
    try:
        # Проверка состояния
        for case in Switch(step):
            if case(-1):
                # Проверка ответа
                if message.text.lower().split()[1] in ['русский', 'english', 'беларускі', '中文']:
                    # Проверка вариантов
                    for elem in Switch(message.text.lower().split()[1]):
                        if elem('русский'):
                            # Создаём оперативную запись
                            ram[message.from_user.id] = {'lang': 'ru'}
                            break
                        elif elem('english'):
                            # Создаём оперативную запись
                            ram[message.from_user.id] = {'lang': 'en'}
                            break
                        elif elem('беларускі'):
                            # Создаём оперативную запись
                            ram[message.from_user.id] = {'lang': 'by'}
                            break
                        elif elem('中文'):
                            # Создаём оперативную запись
                            ram[message.from_user.id] = {'lang': 'zh'}
                            break
                        elif elem():
                            # Отправляем сообщение
                            sendMessage("😐 Ответ не распознан, повторите попытку",
                                        message.chat.id, reply=telebot.types.ReplyKeyboardRemove())
                            # Клавиатура
                            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                            keyboard.add(telebot.types.KeyboardButton(text="🇷🇺 Русский"),
                                         telebot.types.KeyboardButton(text="🇺🇸 English"))
                            keyboard.add(telebot.types.KeyboardButton(text="🇧🇾 Беларускі"),
                                         telebot.types.KeyboardButton(text="🇨🇳 中文"))
                            # Отправляем сообщение
                            sendMessage('❗ Выберите язык', message.chat.id, getUser(message.from_user.id),
                                        reply=keyboard)
                            # Регистрируем следующее событие
                            bot.register_next_step_handler(message, register, invited)
                            break
                    # Клавиатура
                    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(telebot.types.KeyboardButton(text="✔ Да"),
                                 telebot.types.KeyboardButton(text="❌ Нет"))
                    # Отправляем сообщение
                    sendMessage("👋 Здравствуйте! Ваш аккаунт не был найден.\n😉 Хотите зарегистрироваться?",
                                message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, register, 0)
                    break
            elif case(0):
                # Проверка ответа
                if message.text.lower().split()[1] in ['да', 'нет']:
                    # Если ответ положительный
                    if 'да' in message.text.lower():
                        # Клавиатура
                        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                        keyboard.add(telebot.types.KeyboardButton(text="🤕 Пациента"),
                                     telebot.types.KeyboardButton(text="👨‍⚕️ Врача"))
                        # Отправляем сообщение
                        sendMessage("😉 Отлично! Регистрировать как...",
                                    message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
                        # Регистрируем следующее событие
                        bot.register_next_step_handler(message, register, 1)
                        break
                    else:
                        # Удаляем запись
                        ram.pop(message.from_user.id)
                        # Отправляем сообщение
                        sendMessage("💔 Регистрация отменена",
                                    message.chat.id, getUser(message.from_user.id),
                                    reply=telebot.types.ReplyKeyboardRemove())
                        # Ломаем функцию
                        break
                else:
                    # Отправляем сообщение
                    sendMessage("😐 Ответ не распознан, повторите попытку",
                                message.chat.id, ram[message.from_user.id]['lang'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, register, 0)
            elif case(1):
                # Сообщение
                msg: str = "% Начата регистрация как $\nУкажите имя пользователя!"
                # Проверка ответа
                if message.text.lower().split()[1] in ['врача', 'пациента']:
                    # Проверка ответа
                    if 'врач' in message.text.lower():
                        # Создаём пользователя
                        ram[message.from_user.id]['type'] = "doctor"
                        # Меняем сообщение
                        msg = msg.replace('%', '👨‍⚕️')
                        msg = msg.replace('$', 'врача')
                    else:
                        # Создаём пользователя
                        ram[message.from_user.id]['type'] = "patient"
                        # Меняем сообщение
                        msg = msg.replace('%', '🤕')
                        msg = msg.replace('$', 'пациента')
                else:
                    # Отправляем сообщение
                    sendMessage("😐 Ответ не распознан, повторите попытку",
                                message.chat.id, ram[message.from_user.id]['lang'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, register, 1)
                # Клавиатура
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(telebot.types.KeyboardButton(text="✔ Оставить от Telegram"))
                # Отправляем сообщение
                sendMessage(msg, message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
                # Регистрируем следующее событие
                bot.register_next_step_handler(message, register, 2)
                break
            elif case(2):
                # Проверка ответа
                if 'оставить' in message.text.lower():
                    # Добавляем имя пользователя
                    ram[message.from_user.id]['name'] = message.from_user.first_name
                else:
                    # Добавляем имя пользователя
                    ram[message.from_user.id]['name'] = message.text
                # Клавиатура
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(telebot.types.KeyboardButton(text="❌ Не оставлять"))
                # Отправляем сообщение
                sendMessage('📱 Оставите номер телефона?',
                            message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
                # Регистрируем следующее событие
                bot.register_next_step_handler(message, register, 3)
                break
            elif case(3):
                # Проверка ответа
                if checkInt(message.text):
                    # Добавляем номер телефона
                    ram[message.from_user.id]['phone'] = int(message.text)
                    # Отправляем сообщение
                    sendMessage('✔ Номер телефона привязан!', message.chat.id,
                                ram[message.from_user.id]['lang'])
                else:
                    # Добавляем номер телефона
                    ram[message.from_user.id]['phone'] = 0
                # Проверка типа
                if ram[message.from_user.id]['type'] == 'patient':
                    # Отправляем сообщение
                    sendMessage('🔞 Укажите возраст', message.chat.id, ram[message.from_user.id]['lang'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    # Если есть врач
                    if invited is not None:
                        # Регистрируем следующее событие
                        bot.register_next_step_handler(message, registerPatient, 0, invited)
                        break
                    else:
                        # Регистрируем следующее событие
                        bot.register_next_step_handler(message, registerPatient)
                        break
                else:
                    # Отправляем сообщение
                    sendMessage('🤔 Укажите врачебную квалификацию',
                                message.chat.id, ram[message.from_user.id]['lang'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, registerDoctor)
                    break
    except Exception:
        pass
    # Ломаем функцию
    return None


# Личный кабинет
def profile(message):
    # Получаем пользователя
    user: Union[Patient, Doctor, type(None)] = getUser(message.from_user.id)
    # Проверка категории
    if isinstance(user, Doctor):
        # Клавиатура
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("🕵 Принимать анонимно",
                                               callback_data=f"doctorAnonim|{user.get()['id']}"),
            telebot.types.InlineKeyboardButton("🤔 Выбрать пациента",
                                               callback_data=f"patient|{user.get()['id']}"),
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton("🔁 Смена квалификации",
                                               callback_data=f"qualification|{user.get()['id']}"),
            telebot.types.InlineKeyboardButton("💔 Уволиться", callback_data=f"leave|{user.get()['id']}")
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton("🤕 Отказ от пациента",
                                               callback_data=f"patientKick|{user.get()['id']}"),
            telebot.types.InlineKeyboardButton("📑 Смена документа",
                                               callback_data=f"changePhoto|{user.get()['id']}")
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton("💔 Уволить подчинённого",
                                               callback_data=f"doctorKick|{user.get()['id']}")
        )
        # Если есть вылеченные
        if user.get()["discharged"] is not None:
            # Если указан телефон
            if 'phone' in user.get():
                # Если есть фото
                if user.get()['document'] is not None:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: {user.get()["phone"]}\nКвалификация: '
                                f'{user.get()["qualification"]}'
                                f'\nВылеченные: {user.get()["discharged"]}', message.chat.id, user,
                                photo=user.get()['document'], reply=keyboard)
                else:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: {user.get()["document"]}\nКвалификация: '
                                f'{user.get()["qualification"]}\nВылеченные: {user.get()["discharged"]}',
                                message.chat.id, user, reply=keyboard)
            else:
                # Если есть фото
                if user.get()['document'] is not None:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:/<b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: ❌ Не указан\nКвалификация: {user.get()["qualification"]}\n'
                                f'Вылеченные: {user.get()["discharged"]}',
                                message.chat.id, user, photo=user.get()['document'], reply=keyboard)
                else:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: ❌ Не указан\nКвалификация: {user.get()["qualification"]}\n'
                                f'Вылеченные: {user.get()["discharged"]}',
                                message.chat.id, user, reply=keyboard)
        else:
            # Если указан телефон
            if 'phone' in user.get():
                # Если есть фото
                if user.get()['document'] is not None:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: {user.get()["phone"]}\nКвалификация: '
                                f'{user.get()["qualification"]}', message.chat.id, user,
                                photo=user.get()['document'],
                                reply=keyboard)
                else:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: {user.get()["document"]}\nКвалификация: '
                                f'{user.get()["qualification"]}', message.chat.id, user, reply=keyboard)
            else:
                # Если есть фото
                if user.get()['document'] is not None:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:/<b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: ❌ Не указан\nКвалификация: {user.get()["qualification"]}',
                                message.chat.id, user, photo=user.get()['document'], reply=keyboard)
                else:
                    # Отсылаем анкету
                    sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Врач\nИмя: '
                                f'{user.get()["username"]}'
                                f'\nТелефон: ❌ Не указан\nКвалификация: {user.get()["qualification"]}',
                                message.chat.id, user, reply=keyboard)
        # Если есть подчинённые
        if user.getSubordinates():
            # Сообщение
            msg: str = f'👨‍⚕️ Подчинённые: '
            # Перебор подчинённых
            for doctor in user.getSubordinates():
                # Формируем сообщение
                msg += f"[{doctor.get()['id']}] {doctor.get()['username']}, "
            # Отсылаем подчинённых
            sendMessage(msg[:-1], message.chat.id, user)
        # Если есть пациенты
        if user.getPatients():
            # Сообщение
            msg: str = f'🤕 Пациенты: '
            # Перебор подчинённых
            for patient in user.getPatients():
                # Формируем сообщение
                msg += f"[{patient.get()['id']}] {patient.get()['username']}, "
            # Отсылаем подчинённых
            sendMessage(msg[:-1], message.chat.id, user)
    elif isinstance(user, Patient):
        # Клавиатура
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("💬 Связь с врачом",
                                               callback_data=f"contactDoctor|{user.get()['id']}"),
            telebot.types.InlineKeyboardButton("🕵 Анонимный приём",
                                               callback_data=f"anonContactDoctor|{user.get()['id']}")
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton("❣ Выписаться",
                                               callback_data=f"patientExtract|{user.get()['id']}"),
            telebot.types.InlineKeyboardButton("💔 Отказаться от врача",
                                               callback_data=f"patientDoctorKick|{user.get()['id']}"),
        )
        # Если указан телефон
        if 'phone' in user.get():
            # Если мужской пол
            if user.get()['sex']:
                # Отсылаем анкету
                sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Пациент\nИмя: {user.get()["username"]}'
                            f'\nТелефон: ❌ Не указан\nВозраст: {user.get()["age"]}\nПол: 👨 Мужской',
                            message.chat.id, user, reply=keyboard)
            else:
                # Отсылаем анкету
                sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Пациент\nИмя: {user.get()["username"]}'
                            f'\nТелефон: ❌ Не указан\nВозраст: {user.get()["age"]}\nПол: 👩 Женский',
                            message.chat.id, user, reply=keyboard)
        else:
            # Если мужской пол
            if user.get()['sex']:
                # Отсылаем анкету
                sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Пациент\nИмя: {user.get()["username"]}'
                            f'\nТелефон: ❌ Не указан\nВозраст: {user.get()["age"]}\nПол: 👨 Мужской',
                            message.chat.id, user, reply=keyboard)
            else:
                # Отсылаем анкету
                sendMessage(f'💬 <b>Ваш профиль:</b>\n\nСтатус: Пациент\nИмя: {user.get()["username"]}'
                            f'\nТелефон: ❌ Не указан\nВозраст: {user.get()["age"]}\nПол: 👩 Женский',
                            message.chat.id, user, reply=keyboard)
        # Если есть история болезни
        if user.getHistory() is not None:
            # Получаем историю
            history: History = user.getHistory()
            # Сообщение
            msg: str = f'🤕 <b>История болезни:</b>\n\nОписание: {history.description}\nЖалобы: '
            f'{history.complaints}\nИстория заведена: {history.assigned}'
            # Если есть анализы
            if history.analyzes != 'undefined':
                # Формируем сообщение
                msg += f'\nАнализы: {history.analyzes}'
            # Если есть медикаменты
            if history.medicines != 'undefined':
                # Формируем сообщение
                msg += f'\nНазначенные медикаменты: {history.medicines}'
            # Отсылаем историю
            sendMessage(msg, message.chat.id, user)
            # Если есть диагнозы
            if history.diagnoses:
                # Сообщение
                msg: str = f"❣ <b>Диагнозы:</b>\n\nПредсказания: {history.predict}\nВыставленные диагнозы:"
                # Иттерация по списку
                for diagnose in history.diagnoses:
                    # Если выставленно нейросетью
                    if diagnose.neuralnetwork:
                        # Формируем сообщение
                        msg += (f'\n· <b>{diagnose.title}</b>\n{diagnose.description}\n🤖 '
                                f'Выставленно нейросетью!')
                    else:
                        # Формируем сообщение
                        msg += f'\n· <b>{diagnose.title}</b>\n{diagnose.description}'
                # Отсылаем диагнозы
                sendMessage(msg, message.chat.id, user)
            # Если есть врачи
            if history.doctors:
                # Сообщение
                msg: str = f"👨‍⚕️ <b>Врачи:</b>\n"
                # Иттерация по списку
                for doctor in history.doctors:
                    # Формируем сообщение
                    msg += f"\n· [{doctor.get()['id']}] {doctor.get()['username']}"
                # Отсылаем врачей
                sendMessage(msg, message.chat.id, user)
    else:
        # Выбрасываем ошибку
        raise KeyError(f"User with id {message.from_user.id} isn't exsist!")


'''
======================================
              ХОЛДЕРЫ
======================================
'''


# Холдер фотографий
@bot.message_handler(content_types=['photo'])
def photoHandler(message):
    # Если пользователь в оперативной памяти
    if message.from_user.id in ram.keys() and ram[message.from_user.id]['document'] is None:
        # Если необходима верефикация
        if stringToBool(os.getenv('VERIFY')):
            # Отправляем сообщение
            sendMessage("👌 Сканирование документа...", message.chat.id, ram[message.from_user.id]['lang'])
            # Проверка фотографии
            if ai.checkDocument(ai.ImageRecognize(bot.download_file(bot.get_file(
                    message.photo[-1].file_id).file_path)).textRecognize()):
                # Запоминаем фото
                ram[message.from_user.id]['document'] = bot.download_file(
                    bot.get_file(message.photo[-1].file_id).file_path)
                try:
                    # Создаём аккаунт
                    Doctor(message.from_user.id).create(ram[message.from_user.id]['name'],
                                                        ram[message.from_user.id]['qualification'],
                                                        ram[message.from_user.id]['document'],
                                                        ram[message.from_user.id]['lang'],
                                                        ram[message.from_user.id]['phone'])
                    # Отправляем сообщение
                    sendMessage('✔ Аккаунт успешно зарегистрирован и верифицирован!',
                                message.chat.id, ram[message.from_user.id]['lang'])
                except Exception as e:
                    # Отправляем сообщение
                    sendMessage(f'❌ Ошибка при регистрации!\n\n💬 Код: {e}',
                                message.chat.id, ram[message.from_user.id]['lang'])
                # Удаляем пользователя
                ram.pop(message.from_user.id)
            else:
                # Клавиатура
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.add(telebot.types.InlineKeyboardButton(text="💬 Обратная связь", url=os.getenv('ADMIN')))
                # Отправляем сообщение
                sendMessage('❌ Отказано в регистрации!\n\n☝ Если Вы считаете результат работы сети'
                            'некорректным, обратитесь за помощью к модерации или разработчикам',
                            message.chat.id, ram[message.from_user.id]['lang'], reply=keyboard)
                # Отправляем сообщение
                sendMessage("📑 Подтвердите квалификацию документом.\nДокумент будет проверен нейросетью. "
                            "В случае ошибки сообщите разработчику бота", message.chat.id,
                            ram[message.from_user.id]['lang'])


# Холдер команды админа
@bot.message_handler(commands=['admin'])
def adminPanel(message):
    # Если существует пользователь
    if getUser(message.from_user.id) is not None:
        # Получаем админа
        admin: Admin = Admin(getUser(message.from_user.id))
        # Если админ существует
        if admin.getAdmin() is not None and admin.getUser().isExsist():
            # Клавиатура
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton("💬 Связь с пользователем",
                                                   callback_data=f"contactUser|{admin.getUser().get()['id']}"),
            )
            keyboard.add(
                telebot.types.InlineKeyboardButton("🕵 Назначение админа",
                                                   callback_data=f"makeAdmin|{admin.getUser().get()['id']}"),
                telebot.types.InlineKeyboardButton("❌ Удаление админа",
                                                   callback_data=f"removeAdmin|{admin.getUser().get()['id']}")
            )
            keyboard.add(
                telebot.types.InlineKeyboardButton("💥 Разжаловать врача",
                                                   callback_data=f"removeDoctor|{admin.getUser().get()['id']}")
            )
            # Отправляем сообщение
            sendMessage(f'👋 <b>Админ-панель:</b>\n\nНик: {admin.getUser().get()["username"]}\nПрефикс: '
                        f'{admin.getAdmin()["prefix"]}\nУровень: {admin.getAdmin()["level"]}',
                        message.chat.id, admin.getUser(), reply=keyboard)
        else:
            # Отсылаем ошибку
            sendMessage('☝ Вы не администратор!', message.chat.id, admin.getUser())
    else:
        # Отсылаем ошибку
        sendMessage('☝ Вы не зарегистрированы!', message.chat.id, getUser(message.from_user.id))


# Холдер команды старт и профиль
@bot.message_handler(commands=['start', 'profile'])
def start(message):
    # Проверка аргументов
    if len(str(message.text).split()) == 1:
        # Если пользователь существует
        if getUser(message.from_user.id) is not None:
            # Открываем профиль
            profile(message)
        else:
            # Если пользователь регистрируется
            if message.from_user.id in ram.keys() and ram[message.from_user.id]['lang'] is not None:
                # Отправляем сообщение
                sendMessage('☝ Завершите регистрацию!', message.chat.id, ram[message.from_user.id]['lang'])
                # Удаляем запись
                ram.pop(message.from_user.id)
            else:
                # Клавиатура
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(telebot.types.KeyboardButton(text="🇷🇺 Русский"),
                             telebot.types.KeyboardButton(text="🇺🇸 English"))
                keyboard.add(telebot.types.KeyboardButton(text="🇧🇾 Беларускі"),
                             telebot.types.KeyboardButton(text="🇨🇳 中文"))
                # Отправляем сообщение
                sendMessage('❗ Выберите язык', message.chat.id, getUser(message.from_user.id), reply=keyboard)
                # Регистрируем следующее событие
                bot.register_next_step_handler(message, register)
    elif (len(str(message.text).split()) == 2 and checkInt(str(message.text).split()[1]) and
          message.from_user.id not in ram.keys()):
        # Если пользователь существует
        if getUser(message.from_user.id) is not None:
            # Открываем профиль
            profile(message)
        else:
            # Если пользователь регистрируется
            if message.from_user.id in ram.keys() and ram[message.from_user.id]['lang'] is not None:
                # Отправляем сообщение
                sendMessage('☝ Завершите регистрацию!', message.chat.id, ram[message.from_user.id]['lang'])
                # Удаляем запись
                ram.pop(message.from_user.id)
            else:
                # Пользователь
                user: Union[Patient, Doctor] = getUser(int(str(message.text).split()[1]))
                # Если пользователь с указанным ID - врач
                if user is not None and isinstance(user, Doctor):
                    # Клавиатура
                    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(telebot.types.KeyboardButton(text="🇷🇺 Русский"),
                                 telebot.types.KeyboardButton(text="🇺🇸 English"))
                    keyboard.add(telebot.types.KeyboardButton(text="🇧🇾 Беларускі"),
                                 telebot.types.KeyboardButton(text="🇨🇳 中文"))
                    # Отправляем сообщение
                    sendMessage('❗ Выберите язык', message.chat.id, getUser(message.from_user.id),
                                reply=keyboard)
                    # Регистрируем следующее событие
                    bot.register_next_step_handler(message, register, user)
                else:
                    # Отправляем сообщение
                    sendMessage("Пригласивший Вас не является доктором 😥",
                                message.chat.id, getUser(message.from_user.id))


'''
======================================
          СИСТЕМНЫЕ ФУНКЦИИ
======================================
'''


# Очистка ОЗУ
def clearRAM(ramDict: dict, patientKeysRequired: int = 6, doctorKeysRequired: int = 5):
    # Вечный цикл
    while True:
        # Разрешение
        doClear: bool = True
        # Проверка регистрирующихся
        for key in ramDict.keys():
            try:
                # Если есть ключ
                if ramDict[key]['type'] == 'doctor' and len(ramDict[key].keys()) < doctorKeysRequired:
                    # Возвращаем ошибку
                    doClear = False
                elif ramDict[key]['type'] == 'patient' and len(ramDict[key].keys()) < patientKeysRequired:
                    # Возвращаем ошибку
                    doClear = False
            except KeyError:
                pass
        # Если разрешено
        if doClear:
            # Если режим отладки
            if stringToBool(os.getenv('DEBUG')):
                # Выводим информацию
                print(f"Current RAM: {ram} was cleaned!\nCurrent cooldown: {os.getenv('TIMER')}")
            # Очищаем словарь
            ramDict.clear()
        # Задержка
        time.sleep(int(os.getenv('TIMER')))


# Запуск постоянной очистки
threading.Thread(target=clearRAM, args=(ram,)).start()

# Цикл
bot.infinity_polling()
