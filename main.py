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
from typing import Union, List
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from database import getRandomPatient, getAllUserList
from support import checkInt, Switch, ram, stringToBool
from database import Patient, Doctor, getUser, History, Admin, Operations

# Инициализация
ai.initAi()
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))


'''
======================================
          ШАБЛОНЫ КЛАВИАТУР    
======================================
'''

# Клавиатура отмены
cancel = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add(telebot.types.KeyboardButton(text="❌ Отменить"))


'''
======================================
        ОБРАБОТЧИКИ ОТКЛИКОВ    
======================================
'''


# Обработчик функций врача
def doctorHandler(call: telebot.types.Message, message: dict, step: int = 0):
    # Иттерация по вариантам
    for case in Switch(step):
        if case(0):
            # Ломаем блок
            break


# Обработчик функций пациента
def patientHandler(call: telebot.types.Message, message: dict, step: int = 0):
    # Иттерация по вариантам
    for case in Switch(step):
        if case(0):
            # Ломаем блок
            break


# Обработчик функций админа
def adminHandler(call: telebot.types.Message, message: dict, step: int = 0):
    # Иттерация по вариантам
    for case in Switch(step):
        if case(0):
            # Принимаем ответ
            ram[call.text] = {'type': 'system'}
            ram[call.text]['operation'] = Operations.MakeAdmin
            # Отсылаем сообщение
            sendMessage('🤔 Отправьте желаемый уровень.\nУровень не должен привышать ваш собственный!',
                        message['user'])
            # Регистрируем событие
            bot.register_next_step_handler(call, adminHandler, message, 4)
            # Ломаем блок
            break
        elif case(1):
            # Создаём контакт
            debugValue: bool = makeContact(call, message)
            # Если режим отладки
            if stringToBool(os.getenv('DEBUG')):
                # Выводим информацию
                print(f'Chat started with {call.text} and {message["user"].get()["id"]} with result: {debugValue}')
            # Ломаем блок
            break
        elif case(2):
            # Если не нажата отмена
            if 'отменить' not in call.text.lower():
                # Если админ существует
                if Admin(message['user']).getAdmin()['level'] > 0:
                    try:
                        # Если уровень админа соответствует
                        if Admin(getUser(call.text)).getAdmin()['level'] < Admin(message['user']).getAdmin()['level']:
                            # Удаляем админа
                            Admin(getUser(call.text)).removeAdmin()
                            # Информируем пользователей
                            sendMessage(f'✔ Админ с ID {call.text} снят с должности', message['user'],
                                        reply=telebot.types.ReplyKeyboardRemove())
                            sendMessage(f'❌ Вы были сняты с должности админом '
                                        f'{message['user'].get()["username"]}',
                                        getUser(call.text))
                    except AttributeError:
                        # Если уровень админа соответствует
                        if (Admin(getUser(int(call.text))).getAdmin()['level'] <
                                Admin(message['user']).getAdmin()['level']):
                            # Удаляем админа
                            Admin(getUser(int(call.text))).removeAdmin()
                            # Информируем пользователей
                            sendMessage(f'✔ Админ с ID {call.text} снят с должности', message['user'],
                                        reply=telebot.types.ReplyKeyboardRemove())
                            sendMessage(f'❌ Вы были сняты с должности админом '
                                        f'{message['user'].get()["username"]}',
                                        getUser(int(call.text)))
                else:
                    # Информируем пользователя
                    sendMessage('❌ Вы не можете снять админа своего ранга или рангом выше!', message['user'])
            else:
                # Информируем пользователя
                sendMessage('✔ Операция отменена', message['user'], reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case(3):
            # Если не нажата отмена
            if 'отменить' not in call.text.lower():
                # Если такой пользователь существует и он - врач
                if isinstance(getUser(call.text), Doctor):
                    # Удаляем запись
                    getUser(call.text).remove()
                    # Информируем пользователей
                    sendMessage(f'✔ Пользователь с ID {call.text} был снят с должности!', message['user'])
                    sendMessage(f'❌ Вы были сняты с должности администратором '
                                f'{message['user'].get()["username"]}!\nЕсли Вы считаете такую меру не справедливой,'
                                f' обратитесь к <a href="t.me/{os.getenv("ADMIN").replace("@", "")}">'
                                f'старшему администратору</a>', getUser(call.text), message['user'])
                elif isinstance(getUser(int(call.text)), Doctor):
                    # Удаляем запись
                    getUser(int(call.text)).remove()
                    # Информируем пользователей
                    sendMessage(f'✔ Пользователь с ID {call.text} был снят с должности!', message['user'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    sendMessage(f'❌ Вы были сняты с должности администратором '
                                f'{message['user'].get()["username"]}!\nЕсли Вы считаете такую меру не справедливой,'
                                f' обратитесь к <a href="t.me/{os.getenv("ADMIN").replace("@", "")}">'
                                f'старшему администратору</a>', getUser(int(call.text)), message['user'])
                else:
                    # Информируем пользователя
                    sendMessage('❌ Вы не можете снять пользователя, так как он не является врачом!',
                                message['user'], reply=telebot.types.ReplyKeyboardRemove())
            else:
                # Информируем пользователя
                sendMessage('✔ Операция отменена', message['user'], reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case(4):
            # Проверка числа
            if checkInt(call.text):
                # Если уровень не превышен
                if int(call.text) < Admin(message['user']).getAdmin()['level']:
                    # Последний ключ
                    lastKey: str = "undefined"
                    # Клавиатура
                    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(telebot.types.KeyboardButton(text="❌ Не оставлять"))
                    # Вычисляем ID операции
                    for key in ram.keys():
                        try:
                            # Если операция системная
                            if ram[key]['type'] == 'system' and ram[key]['operation'] == Operations.MakeAdmin:
                                # Прибавляем значение
                                lastKey = key
                        except KeyError:
                            pass
                    # Вносим ключ
                    ram[lastKey]['level'] = int(call.text)
                    # Отсылаем сообщение
                    sendMessage('🤔 Отправьте желаемый префикс', message['user'], reply=keyboard)
                    # Регистрируем событие
                    bot.register_next_step_handler(call, adminHandler, message, 5)
                else:
                    # Отсылаем сообщение
                    sendMessage('☝ Ответ не является допустимым числом.\nВаш уровень ниже или равен '
                                'введённому!', message['user'], reply=telebot.types.ReplyKeyboardRemove())
                    # Отсылаем сообщение
                    sendMessage('🤔 Отправьте желаемый уровень.\nУровень не должен привышать ваш собственный!',
                                message['user'], reply=telebot.types.ReplyKeyboardRemove())
                    # Регистрируем событие
                    bot.register_next_step_handler(call, adminHandler, message, 4)
            else:
                # Отсылаем сообщение
                sendMessage('☝ Ответ не является допустимым числом!', message['user'])
                # Отсылаем сообщение
                sendMessage('🤔 Отправьте желаемый уровень.\nУровень не должен привышать ваш собственный!',
                            message['user'], reply=telebot.types.ReplyKeyboardRemove())
                # Регистрируем событие
                bot.register_next_step_handler(call, adminHandler, message, 4)
            # Ломаем блок
            break
        elif case(5):
            # Клавиатура
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.KeyboardButton(text="✔ Подтвердить"),
                         telebot.types.KeyboardButton(text="❌ Отменить"))
            # Если нужно оставить префикс
            if 'не оставлять' not in call.text.lower():
                # Последний ключ
                lastKey: str = "undefined"
                # Вычисляем ID операции
                for key in ram.keys():
                    try:
                        # Если операция системная
                        if ram[key]['type'] == 'system' and ram[key]['operation'] == Operations.MakeAdmin:
                            # Прибавляем значение
                            lastKey = key
                    except KeyError:
                        pass
                # Назначаем префикс
                ram[lastKey]['prefix'] = call.text
                # Отсылаем сообщение
                sendMessage(f'✔ Назначен префикс: {call.text}\n\nПодтвердить назначение?', message['user'],
                            reply=keyboard)
            else:
                # Отсылаем сообщение
                sendMessage(f'✔ Префикс не назначен!\n\nПодтвердить назначение?', message['user'],
                            reply=keyboard)
            # Регистрируем событие
            bot.register_next_step_handler(call, adminHandler, message, 6)
            # Ломаем блок
            break
        elif case(6):
            # Последний ключ
            lastKey: str = "undefined"
            # Вычисляем ID операции
            for key in ram.keys():
                try:
                    # Если операция системная
                    if ram[key]['type'] == 'system' and ram[key]['operation'] == Operations.MakeAdmin:
                        # Прибавляем значение
                        lastKey = key
                except KeyError:
                    pass
            # Проверка ответа
            if 'подтвердить' in call.text.lower():
                try:
                    # Отсылаем сообщение
                    sendMessage(f'✔ Назначение подтверждено', message['user'],
                                reply=telebot.types.ReplyKeyboardRemove())
                    # Если получено число
                    if checkInt(lastKey):
                        # Создаём админа
                        admin: Admin = (Admin(getUser(int(lastKey))))
                        admin.writeNewAdmin(int(ram[lastKey]['level']), ram[lastKey]['prefix'])
                        # Информируем кандидата
                        sendMessage(f'💥 <b>Вы были назначены на должность администратора в сети '
                                    f'HealthAI!</b>\n\n'
                                    f'Подойдите добросовестно к исполнению своих обязанностей 🤗\nУровень: '
                                    f'{admin.getAdmin()["level"]}\nПрефикс: {admin.getAdmin()["prefix"]}',
                                    getUser(int(lastKey)))
                    else:
                        # Создаём админа
                        admin: Admin = Admin(getUser(lastKey))
                        admin.writeNewAdmin(int(ram[lastKey]['level']), ram[lastKey]['prefix'])
                        # Информируем кандидата
                        sendMessage(f'💥 <b>Вы были назначены на должность администратора в сети '
                                    f'HealthAI!</b>\n\n'
                                    f'Подойдите добросовестно к исполнению своих обязанностей 🤗\nУровень: '
                                    f'{admin.getAdmin()["level"]}\nПрефикс: {admin.getAdmin()["prefix"]}',
                                    getUser(lastKey))
                except AttributeError:
                    # Отсылаем сообщение
                    sendMessage(f'❌ Назначение отменено\nПользователя с ID {lastKey} не существует!',
                                message['user'], reply=telebot.types.ReplyKeyboardRemove())
            else:
                # Отсылаем сообщение
                sendMessage(f'❌ Назначение отменено', message['user'],
                            reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
    # Ломаем функцию
    return None


'''
======================================
            ОТКЛИКИ БОТА      
======================================
'''


# Обработчик Inline запросов врача
def callCheckDoctor(call: telebot.types.Message, message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case('doctorAnonim'):
            # Ломаем блок
            break
        elif case('patient'):
            # Ломаем блок
            break
        elif case('qualification'):
            # Ломаем блок
            break
        elif case('patientKick'):
            # Ломаем блок
            break
        elif case('passchangePhoto'):
            # Ломаем блок
            break
        elif case('doctorKick'):
            # Ломаем блок
            break
        elif case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к администратору!',
                        message['user'], reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break


# Обработчик Inline запросов пациента
def callCheckPatient(call: telebot.types.Message, message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case('contactDoctor'):
            # Ломаем блок
            break
        elif case('anonContactDoctor'):
            # Ломаем блок
            break
        elif case('patientExtract'):
            # Ломаем блок
            break
        elif case('patientDoctorKick'):
            # Ломаем блок
            break
        elif case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к администратору!',
                        message['user'], reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break


# Обработчик Inline запросов админа
def callCheckAdmin(call: telebot.types.Message, message: dict):
    # Иттерация по вариантам
    for case in Switch(message['message']):
        # Проверка вариантов
        if case('makeAdmin'):
            # Если ранг достаточен
            if Admin(message['user']).getAdmin()['level'] >= 4:
                # Отсылаем сообщение
                sendMessage('🤔 Введите имя пользователя или его ID для назначения в админы',
                            message['user'], reply=telebot.types.ReplyKeyboardRemove())
                # Передаём параметр в функцию
                bot.register_next_step_handler(call, adminHandler, message)
            else:
                # Отсылаем сообщение
                sendMessage('☝ Ваш ранг недостаточен!', message['user'],
                            reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case('contactUser'):
            # Если ранг достаточен
            if Admin(message['user']).getAdmin()['level'] >= 1:
                # Отсылаем сообщение
                sendMessage('🤔 Введите имя пользователя или его ID для контакта',
                            message['user'], reply=cancel)
                # Передаём параметр в функцию
                bot.register_next_step_handler(call, adminHandler, message, 1)
            else:
                # Отсылаем сообщение
                sendMessage('☝ Ваш ранг недостаточен!', message['user'],
                            reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case('removeAdmin'):
            # Если ранг достаточен
            if Admin(message['user']).getAdmin()['level'] >= 3:
                # Отсылаем сообщение
                sendMessage('🤔 Введите имя пользователя или его ID для удаления из админов',
                            message['user'], reply=cancel)
                # Передаём параметр в функцию
                bot.register_next_step_handler(call, adminHandler, message, 2)
            else:
                # Отсылаем сообщение
                sendMessage('☝ Ваш ранг недостаточен!', message['user'],
                            reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case('removeDoctor'):
            # Если ранг достаточен
            if Admin(message['user']).getAdmin()['level'] >= 2:
                # Отсылаем сообщение
                sendMessage('🤔 Введите имя пользователя или его ID для удаления из врачей',
                            message['user'], reply=cancel)
                # Передаём параметр в функцию
                bot.register_next_step_handler(call, adminHandler, message, 3)
            else:
                # Отсылаем сообщение
                sendMessage('☝ Ваш ранг недостаточен!', message['user'],
                            reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break
        elif case():
            # Отсылаем сообщение
            sendMessage('😐 Callback не распознан.\nОбратитесь за помощью к разработчику!',
                        message['user'], reply=telebot.types.ReplyKeyboardRemove())
            # Ломаем блок
            break


# Обработчик Inline запросов
@bot.callback_query_handler(func=lambda call: True)
def callCheck(call: telebot.types.CallbackQuery):
    # Получаем пользователя
    user: Union[Patient, Doctor, type(None)] = getUser(int(call.data.split('|')[1]))
    # Если пользователь найден
    if user is not None and user.isExsist():
        # Получаем сообщение
        message: dict = {
            'user': user,
            'message': call.data.split('|')[0],
            'params': call.data.split('|')[:2]
        }
        # Если пользователь - админ
        if Admin(user).getAdmin() is not None:
            # Передаём параметр
            callCheckAdmin(call.message, message)
        else:
            # Если пользователь - пациент
            if isinstance(user, Patient):
                # Передаём параметр
                callCheckPatient(call.message, message)
            elif isinstance(user, Doctor):
                # Передаём параметр
                callCheckDoctor(call.message, message)


'''
======================================
        СИСТЕМНЫЕ ФУНКЦИИ БОТА        
======================================
'''


# Отправка сообщения
def sendMessage(message: str, to: Union[Patient, Doctor, int], self: Union[Patient, Doctor, str, None] = None,
                reply: Union[telebot.types.InlineKeyboardMarkup, telebot.types.ReplyKeyboardMarkup,
                telebot.types.ReplyKeyboardRemove(), type(None)] = None, photo: Union[bytes, type(None)] = None,
                parse_mode: str = 'html') -> telebot.types.Message:
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
                        return bot.send_message(to.get()['id'], message, parse_mode)
                    else:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo, message, parse_mode)
                    else:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'],
                                                GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                    message),
                                                parse_mode)
                    else:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'],
                                                GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                    message),
                                                parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo,
                                              GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                  message),
                                              parse_mode)
                    else:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo,
                                              GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                  message),
                                              parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    return bot.send_message(to, message, parse_mode)
                else:
                    # Отправляем сообщение
                    return bot.send_message(to, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    return bot.send_photo(to, photo, message, parse_mode)
                else:
                    # Отправляем фото
                    return bot.send_photo(to, photo, message, parse_mode, reply_markup=reply)
    elif isinstance(self, type(None)):
        # Проверка типов
        if isinstance(to, Patient) or isinstance(to, Doctor):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    return bot.send_message(to.get()['id'], message, parse_mode)
                else:
                    # Отправляем сообщение
                    return bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    return bot.send_photo(to.get()['id'], photo, message, parse_mode)
                else:
                    # Отправляем фото
                    return bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    return bot.send_message(to, message, parse_mode)
                else:
                    # Отправляем сообщение
                    return bot.send_message(to, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    return bot.send_photo(to, photo, message, parse_mode)
                else:
                    # Отправляем фото
                    return bot.send_photo(to, photo, message, parse_mode, reply_markup=reply)
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
                        return bot.send_message(to.get()['id'], message, parse_mode)
                    else:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'], message, parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo, message, parse_mode)
                    else:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo, message, parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if photo is None:
                    # Проверка условий
                    if reply is None:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'],
                                                GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                    message),
                                                parse_mode)
                    else:
                        # Отправляем сообщение
                        return bot.send_message(to.get()['id'],
                                                GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                    message),
                                                parse_mode, reply_markup=reply)
                else:
                    # Проверка условий
                    if reply is None:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo,
                                              GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                  message),
                                              parse_mode)
                    else:
                        # Отправляем фото
                        return bot.send_photo(to.get()['id'], photo,
                                              GoogleTranslator(source='auto', target=to.get()['lang']).translate(
                                                  message),
                                              parse_mode, reply_markup=reply)
        elif isinstance(to, int):
            # Проверка условий
            if photo is None:
                # Проверка условий
                if reply is None:
                    # Отправляем сообщение
                    return bot.send_message(to, GoogleTranslator(source='auto', target=self).translate(message),
                                            parse_mode)
                else:
                    # Отправляем сообщение
                    return bot.send_message(to, GoogleTranslator(source='auto', target=self).translate(message),
                                            parse_mode, reply_markup=reply)
            else:
                # Проверка условий
                if reply is None:
                    # Отправляем фото
                    return bot.send_photo(to, photo, GoogleTranslator(source='auto', target=self).translate(message),
                                          parse_mode)
                else:
                    # Отправляем фото
                    return bot.send_photo(to, photo, GoogleTranslator(source='auto', target=self).translate(message),
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
                         telebot.types.KeyboardButton(text="👩 Женский"))
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
    try:
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
    except Exception:
        # Если пользователь находиться в контакте
        if message.from_user.id in ram or getUser(message.from_user.id).get()['username'] in ram:
            try:
                # Пересылаем сообщение
                bot.forward_message(getUser(ram[message.from_user.id]['contactInit']).get()['id'], message.chat.id,
                                    message.message_id)
            except Exception:
                try:
                    # Получаем имя
                    name: str = getUser(message.from_user.id).get()['username']
                    # Пересылаем сообщение
                    bot.forward_message(getUser(ram[name]['contactInit']).get()['id'], message.chat.id,
                                        message.message_id)
                except Exception:
                    # Выдаём ошибку
                    sendMessage('❌ Ошибка доставки сообщения!\nПрекратите диалог командой /stop',
                                message.from_user.id)
        else:
            # Иттерация по оперативной памяти
            for key in ram:
                # Если тип операции системный и содержит ID инициализировавшего мессенджер
                if 'type' in ram[key] and ram[key]['type'] == 'system' and 'contactInit' in ram[key]:
                    # Если ID совпали
                    if (ram[key]['contactInit'] == message.from_user.id or
                            ram[key]['contactInit'] == getUser(message.from_user.id).get()['username']):
                        try:
                            # Пересылаем сообщение
                            bot.forward_message(getUser(key).get()['id'], message.chat.id, message.message_id)
                        except Exception:
                            try:
                                # Пересылаем сообщение
                                bot.forward_message(getUser(int(key)).get()['id'], message.chat.id, message.message_id)
                            except Exception:
                                # Выдаём ошибку
                                sendMessage('❌ Ошибка доставки сообщения!\nПрекратите диалог командой /stop',
                                            message.from_user.id)


# Холдер команды помощи
@bot.message_handler(commands=['help'])
def help(message):
    # Отправляем сообщение
    sendMessage(f'🤗 <b>Помощь по боту</b>\n\n👇 <a href="{os.getenv("HELP")}">Кликни на меня</a>',
                getUser(message.from_user.id))


# Холдер команды списка
@bot.message_handler(commands=['list'])
def listCommand(message):
    # Получаем список пользователей
    userList: List[Union[Doctor, Patient]] = getAllUserList()
    # Если список не пустой
    if userList:
        # Попытка парсинга
        try:
            # Получаем список аргументов
            args: List[str] = message.text.split()
            args = args[1:]
            # Проверка аргументов
            for case in Switch(args[0]):
                if case('doctors') or case('doctors') or case('доктора'):
                    # Сообщение
                    msg: str = "📃 <b>Список врачей и админов:</b>\n\n👨‍⚕️ <b>Врачи:</b>\n"
                    # Словари
                    doctors: dict = {
                        'count': 0,
                        'message': ""
                    }
                    # Перебор администраторов
                    for user in userList:
                        # Если пользователь - врач
                        if isinstance(user, Doctor):
                            # Прибавляем иттератор
                            doctors['count'] += 1
                            # Если верифицирован
                            if user.get()['document'] is not None:
                                # Если есть номер телефона
                                if 'phone' in user.get():
                                    # Вносим в список
                                    doctors['message'] += (f"✔ {doctors['count']}. {user.get()['username']} "
                                                           f"[{user.get()['qualification']}]\n📱 Телефон: "
                                                           f"{user.get()['phone']}\n")
                                else:
                                    # Вносим в список
                                    doctors['message'] += (f"✔ {doctors['count']}. {user.get()['username']} "
                                                           f"[{user.get()['qualification']}]\n")
                            else:
                                # Если есть номер телефона
                                if 'phone' in user.get():
                                    # Вносим в список
                                    doctors['message'] += (f"{doctors['count']}. {user.get()['username']} "
                                                           f"[{user.get()['qualification']}]\n📱 Телефон: "
                                                           f"{user.get()['phone']}\n")
                                else:
                                    # Вносим в список
                                    doctors['message'] += (f"{doctors['count']}. {user.get()['username']} "
                                                           f"[{user.get()['qualification']}]\n")
                    # Прибавляем сообщения
                    msg += doctors['message']
                    # Отправляем сообщение
                    sendMessage(msg, getUser(message.from_user.id))
                    # Ломаем функцию
                    break
                elif case('admins') or case('admin') or case('админы'):
                    # Сообщение
                    msg: str = "📃 <b>Список врачей и админов:</b>\n\n🕵️‍♂️ <b>Администрация: </b>\n"
                    # Словари
                    admins: dict = {
                        'count': 0,
                        'message': ""
                    }
                    # Перебор администраторов
                    for user in userList:
                        # Если пользователь - администратор
                        if Admin(user).getAdmin()['level'] > 0:
                            # Прибавляем иттератор
                            admins['count'] += 1
                            # Если есть префикс
                            if Admin(user).getAdmin()['prefix'] != "undefined":
                                # Вносим в список
                                admins['message'] += (f"{admins['count']}. {user.get()['username']} "
                                                      f"[{Admin(user).getAdmin()['prefix']}]\n")
                            else:
                                # Вносим в список
                                admins['message'] += f"{admins['count']}. {user.get()['username']}\n"
                    # Прибавляем сообщения
                    msg += admins['message']
                    # Отправляем сообщение
                    sendMessage(msg, getUser(message.from_user.id))
                    # Ломаем функцию
                    break
                elif case():
                    # Отправляем сообщение
                    sendMessage('☝ <b>Неизвестный аргумент!</b>\n\nМожет быть вы имели ввиду «/list», '
                                '«/list doctors» или «/list admins»?', getUser(message.from_user.id))
                    # Ломаем функцию
                    break
        except Exception:
            # Сообщение
            msg: str = "📃 <b>Список врачей и админов:</b>\n\n🕵️‍♂️ <b>Администрация: </b>\n"
            # Словари
            admins: dict = {
                'count': 0,
                'message': ""
            }
            doctors: dict = {
                'count': 0,
                'message': ""
            }
            # Перебор администраторов
            for user in userList:
                # Если пользователь - администратор
                if Admin(user).getAdmin()['level'] > 0:
                    # Прибавляем иттератор
                    admins['count'] += 1
                    # Если есть префикс
                    if Admin(user).getAdmin()['prefix'] != "undefined":
                        # Вносим в список
                        admins['message'] += (f"{admins['count']}. {user.get()['username']} "
                                              f"[{Admin(user).getAdmin()['prefix']}]\n")
                    else:
                        # Вносим в список
                        admins['message'] += f"{admins['count']}. {user.get()['username']}\n"
                # Если пользователь - врач
                if isinstance(user, Doctor):
                    # Прибавляем иттератор
                    doctors['count'] += 1
                    # Если верифицирован
                    if user.get()['document'] is not None:
                        # Если есть номер телефона
                        if 'phone' in user.get():
                            # Вносим в список
                            doctors['message'] += (f"✔ {doctors['count']}. {user.get()['username']} "
                                                   f"[{user.get()['qualification']}]\n📱 Телефон: "
                                                   f"{user.get()['phone']}\n")
                        else:
                            # Вносим в список
                            doctors['message'] += (f"✔ {doctors['count']}. {user.get()['username']} "
                                                   f"[{user.get()['qualification']}]\n")
                    else:
                        # Если есть номер телефона
                        if 'phone' in user.get():
                            # Вносим в список
                            doctors['message'] += (f"{doctors['count']}. {user.get()['username']} "
                                                   f"[{user.get()['qualification']}]\n📱 Телефон: "
                                                   f"{user.get()['phone']}\n")
                        else:
                            # Вносим в список
                            doctors['message'] += (f"{doctors['count']}. {user.get()['username']} "
                                                   f"[{user.get()['qualification']}]\n")
            # Прибавляем сообщения
            msg += f"{admins['message']}\n👨‍⚕️ <b>Врачи:</b>\n{doctors['message']}"
            # Отправляем сообщение
            sendMessage(msg, getUser(message.from_user.id))
    else:
        # Отправляем сообщение
        sendMessage('😥 У нас ещё нет пользователей...', getUser(message.from_user.id))


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
            # Если есть префикс
            if 'prefix' in admin.getAdmin() and admin.getAdmin()['prefix'] != 'undefined':
                # Отправляем сообщение
                sendMessage(f'👋 <b>Админ-панель:</b>\n\nНик: {admin.getUser().get()["username"]}\nПрефикс: '
                            f'{admin.getAdmin()["prefix"]}\nУровень: {admin.getAdmin()["level"]}',
                            message.chat.id, admin.getUser(), reply=keyboard)
            else:
                # Отправляем сообщение
                sendMessage(f'👋 <b>Админ-панель:</b>\n\nНик: {admin.getUser().get()["username"]}'
                            f'\nУровень: {admin.getAdmin()["level"]}',
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


# Холдер команды остановки диалога
@bot.message_handler(commands=['stop'])
def stop(message: telebot.types.Message):
    # Если пользователь находиться в контакте
    if message.from_user.id in ram or getUser(message.from_user.id).get()['username'] in ram:
        try:
            # Пересылаем сообщение
            sendMessage('😥 Собеседник прекратил диалог',
                        getUser(ram[message.from_user.id]['contactInit']), getUser(message.from_user.id))
        except Exception:
            try:
                # Пересылаем сообщение
                sendMessage('😥 Собеседник прекратил диалог',
                            getUser(ram[message.from_user.id]['contactInit']), getUser(message.from_user.id))
            except Exception:
                # Посылаем сообщение
                sendMessage('❌ Диалог прекращён с ошибкой.\nПользователя не существует',
                            getUser(message.from_user.id))
        # Удаляем информацию из оперативной памяти
        ram.pop(message.from_user.id)
        # Прерываем функцию
        return None
    else:
        # Ключ на удаление
        removeKey: Union[str, int] = 0
        # Иттерация по оперативной памяти
        for key in ram:
            # Если тип операции системный и содержит ID инициализировавшего мессенджер
            if 'type' in ram[key] and ram[key]['type'] == 'system' and 'contactInit' in ram[key]:
                # Если ID совпали
                if (ram[key]['contactInit'] == message.from_user.id or
                        ram[key]['contactInit'] == getUser(message.from_user.id).get()['username']):
                    try:
                        # Пересылаем сообщение
                        sendMessage('😥 Собеседник прекратил диалог', getUser(key),
                                    getUser(ram[key]['contactInit']))
                    except Exception:
                        # Посылаем сообщение
                        sendMessage('❌ Диалог прекращён с ошибкой.\nПользователя не существует',
                                    getUser(message.from_user.id))
                    # Запоминаем ключ
                    removeKey = key
        try:
            # Удаляем информацию из оперативной памяти
            ram.pop(removeKey)
        except Exception:
            pass
    # Посылаем сообщение
    sendMessage('☝ Вы не находитесь в диалоге!', getUser(message.from_user.id))


# Принятие сообщений
@bot.message_handler(content_types=["text", "audio", "document", "sticker", "video", "video_note", "voice"])
def getMessage(message: telebot.types.Message):
    # Если пользователь находиться в контакте
    if message.from_user.id in ram or getUser(message.from_user.id).get()['username'] in ram:
        try:
            # Пересылаем сообщение
            bot.forward_message(getUser(ram[message.from_user.id]['contactInit']).get()['id'], message.chat.id,
                                message.message_id)
        except Exception:
            try:
                # Получаем имя
                name: str = getUser(message.from_user.id).get()['username']
                # Пересылаем сообщение
                bot.forward_message(getUser(ram[name]['contactInit']).get()['id'], message.chat.id,
                                    message.message_id)
            except Exception:
                # Выдаём ошибку
                sendMessage('❌ Ошибка доставки сообщения!\nПрекратите диалог командой /stop',
                            message.from_user.id)
    # Иттерация по оперативной памяти
    for key in ram:
        # Если тип операции системный и содержит ID инициализировавшего мессенджер
        if 'type' in ram[key] and ram[key]['type'] == 'system' and 'contactInit' in ram[key]:
            # Если ID совпали
            if (ram[key]['contactInit'] == message.from_user.id or
                    ram[key]['contactInit'] == getUser(message.from_user.id).get()['username']):
                try:
                    # Пересылаем сообщение
                    bot.forward_message(getUser(key).get()['id'], message.chat.id, message.message_id)
                except Exception:
                    # Выдаём ошибку
                    sendMessage('❌ Ошибка доставки сообщения!\nПрекратите диалог командой /stop',
                                message.from_user.id)


'''
======================================
          СИСТЕМНЫЕ ФУНКЦИИ
======================================
'''


# Создание чата
def makeContact(call: telebot.types.Message, message: dict, step: int = 0) -> bool:
    # Проверка состояния
    if step == 0:
        try:
            # Если не в чате
            if int(call.text) not in ram and call.text not in ram:
                try:
                    # Если такой пользователь существует
                    if getUser(int(call.text)) is not None:
                        # Устанавливаем связь
                        ram[int(call.text)] = {'type': 'system'}
                        ram[int(call.text)]['operation'] = Operations.Contact
                        ram[int(call.text)]['contactInit'] = call.from_user.id
                        # Отсылаем сообщение
                        sendMessage('👌 Контакт установлен!\nВаши сообщения будут переадресовываться контакту '
                                    'до команды /stop',
                                    message['user'])
                        # Отсылаем сообщение
                        sendMessage(f'👌 Контакт c пользователем {message['user'].get()['username']} '
                                    f'установлен!\nВаши сообщения будут переадресовываться контакту до команды /stop',
                                    getUser(int(call.text)))
                        # Возвращаем результат
                        return True
                    else:
                        # Отсылаем сообщение
                        sendMessage(f'❌ Контакт не установлен!\nПользователь с ID {call.text} не найден',
                                    message['user'])
                        # Возвращаем результат
                        return False
                except Exception:
                    # Если такой пользователь существует
                    if getUser(call.text) is not None:
                        # Устанавливаем связь
                        ram[call.text] = {'type': 'system'}
                        ram[call.text]['operation'] = Operations.Contact
                        ram[call.text]['contactInit'] = call.from_user.id
                        # Отсылаем сообщение
                        sendMessage('👌 Контакт установлен!\nВаши сообщения будут переадресовываться контакту '
                                    'до команды /stop',
                                    message['user'])
                        # Отсылаем сообщение
                        sendMessage(f'👌 Контакт c пользователем {message['user'].get()['username']} '
                                    f'установлен!\nВаши сообщения будут переадресовываться контакту до команды /stop',
                                    getUser(call.text))
                        # Возвращаем результат
                        return True
                    else:
                        # Отсылаем сообщение
                        sendMessage(f'❌ Контакт не установлен!\nПользователь с ID {call.text} не найден',
                                    message['user'])
                        # Возвращаем результат
                        return False
            else:
                # Клавиатура
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(telebot.types.KeyboardButton(text="❌ Завершить"))
                # Отсылаем сообщение
                sendMessage('☝ Завершите все диалоги и процессы, прежде чем начать новый диалог!',
                            message['user'], reply=keyboard)
                # Регистрируем процесс
                bot.register_next_step_handler(call, makeContact, message, 1)
                # Возвращаем результат
                return False
        except ValueError:
            # Отсылаем сообщение
            sendMessage(f'❌ Контакт не установлен!\nПользователь с ID {call.text} не найден',
                        message['user'])
            # Возвращаем результат
            return False
    else:
        try:
            # Удаляем ключ
            ram.pop(int(call.text))
        except KeyError:
            # Удаляем ключ
            ram.pop(call.text)
        # Повторяем вызов
        makeContact(call, message)
        # Возвращаем результат
        return False


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
                if (ramDict[key]['type'] == 'doctor' and len(ramDict[key].keys()) < doctorKeysRequired or
                        ramDict[key]['type'] == 'patient' and len(ramDict[key].keys()) < patientKeysRequired):
                    # Возвращаем ошибку
                    doClear = False
                elif ramDict[key]['type'] == 'system':
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
