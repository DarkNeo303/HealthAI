"""
======================================
        HealthAI Telegram Бот
             База данных
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
import ai
import os
import json
import sqlite3
import datetime
from enum import Enum
from random import choice
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Union, List, Tuple

# Инициализация
load_dotenv()

# Устанавливаем соединение с базой данных
connection = sqlite3.connect(os.getenv("DATA"), check_same_thread=False)
database = connection.cursor()

# Время опросов
times: List[int] = json.loads(os.getenv('TIMES'))

# Список активных меню
menus: list = []

# Создание таблицы докторов
database.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY NOT NULL,
        username TEXT NOT NULL UNIQUE,
        lang VARCHAR(10) DEFAULT "ru",
        qualification TEXT NOT NULL,
        document BLOB,
        discharged INTEGER,
        subordinates JSON,
        phone INTEGER,
        patients JSON
    )
''')

# Создание таблицы настроек
database.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        timezone VARCHAR(255),
        surveys TINYINT,
        wallet INTEGER
    )
''')

# Создание таблицы премиума
database.execute('''
    CREATE TABLE IF NOT EXISTS premium (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        experies VARCHAR(255)
    )
''')

# Создание таблицы с рекламой
database.execute('''
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        author INTEGER NOT NULL,
        photo BLOB,
        experies VARCHAR(255)
    )
''')

# Создание таблицы с
database.execute('''
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        author INTEGER NOT NULL,
        photo BLOB,
        experies VARCHAR(255)
    )
''')

# Создание таблицы пациентов
database.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY NOT NULL,
        sex BOOLEAN NOT NULL DEFAULT 0,
        lang VARCHAR(10) DEFAULT "ru",
        age INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        phone INTEGER,
        history JSON,
        tables JSON
    )
''')

# Сохранение изменений
connection.commit()

# Изображения
photos: dict = {}
# Если папка с изображениями не пуста
if os.listdir(os.getenv('IMAGES')):
    # Инициализация фотографий
    for file in os.listdir(os.getenv('IMAGES')):
        # Открываем фотографию
        with open(os.getenv('IMAGES') + file, 'rb') as ph:
            # Вносим фото
            photos[file.split('.')[0]] = ph.read()


# Операции
class Operations(Enum):
    MakeAdmin = 0
    Contact = 1
    AnonContactFind = 2
    ChangeMe = 3
    Diagnose = 4
    MakeTable = 5
    TimeZoneSelect = 6


# Тип данных таблицы
@dataclass
class Table:
    # Вопрос с вариантом
    @dataclass
    class Variant:
        # Переменные
        question: str = "undefined"
        variants: List[str] = None

    # Переменные
    id: int = 0
    title: str = "undefined"
    expires: datetime.date = None
    assigned: datetime.date = None
    replyable: List[str] = None
    variants: Union[dict, List[Variant]] = None

    # После инициализации
    def __post_init__(self):
        # Проверка типа
        if isinstance(self.variants, dict):
            # Если словарь не пустой
            if self.variants != {}:
                # Выходной список
                result: List[Table.Variant] = []
                # Парсинг вопросов с вариантами
                for key in self.variants:
                    # Добавляем вариант в список
                    result.append(self.Variant(key, self.variants[key]))


# Класс врача
class Doctor:
    # Типы данных
    class Types(Enum):
        lang = 1,
        phone = 2,
        patients = 3,
        document = 4,
        subordinates = 5,
        qualification = 6,
        settings = 7

    # Инициализация
    def __init__(self, id: Union[int, str], db: sqlite3.Cursor = database):
        # Запрос
        result = None
        settings = None
        # Курсор
        self.__db: sqlite3.Cursor = db
        # Если получено число
        if isinstance(id, int):
            # Переменные
            self.__id: int = id
            self.__lang: str = 'ru'
            self.__username: str = "undefined"
            self.__phone: int = 0
            self.__qualification: dict = {}
            self.__document: bytes = b"0"
            self.__discharged: int = 0
            self.__subordinates: List[Doctor] = []
            self.__patients: List[Patient] = []
            self.__settings: dict = {}
            self.__exsist: bool = False
            # Попытка найти пользователя
            result = db.execute(f'SELECT * FROM doctors WHERE id={id}').fetchone()
            settings = db.execute(f'SELECT * FROM settings WHERE id={id}').fetchone()
        # Если получена строка
        elif isinstance(id, str):
            # Переменные
            self.__id: int = 0
            self.__lang: str = 'ru'
            self.__username: str = id
            self.__phone: int = 0
            self.__qualification: dict = {}
            self.__document: bytes = b"0"
            self.__discharged: int = 0
            self.__subordinates: List[Doctor] = []
            self.__patients: List[Patient] = []
            self.__settings: dict = {}
            self.__exsist: bool = False
            # Попытка найти пользователя
            result = db.execute(f'SELECT * FROM doctors WHERE username={id}').fetchone()
            settings = db.execute(f'SELECT * FROM settings WHERE id={id}').fetchone()
        # Проверка результата
        if result is not None:
            # Устанавливаем переменные
            self.__exsist = True
            self.__id = result[0]
            self.__username = result[1]
            self.__lang = result[2]
            try:
                self.__qualification = result[3]
            except Exception:
                pass
            try:
                self.__document = result[4]
            except Exception:
                pass
            try:
                self.__discharged = result[5]
            except Exception:
                pass
            try:
                # Перебор врачей
                for id in json.loads(result[6]):
                    # Добавляем подчинённого
                    self.__subordinates.append(Doctor(id))
            except Exception:
                pass
            try:
                self.__phone = result[7]
            except Exception:
                pass
            try:
                # Перебор пациентов
                for id in json.loads(result[8]):
                    # Добавляем пациента
                    self.__patients.append(Patient(id))
            except Exception:
                pass
        if settings is not None:
            try:
                # Вносим в настройки
                self.__settings['timezone'] = settings[1]
                self.__settings['surveys'] = settings[2]
                self.__settings['wallet'] = settings[3]
            except Exception:
                pass

    # Проверка премиума
    def isPremium(self) -> Union[bool, tuple]:
        # Возвращаем результат
        return (self.__db.execute(f'SELECT * FROM premium WHERE id={self.__id}').fetchone() is not None and
                self.__db.execute(f'SELECT * FROM premium WHERE id={self.__id}').fetchone())

    # Добавление премиума
    def premiumAdd(self, expires: datetime.date = datetime.date.today()) -> sqlite3.Cursor:
        try:
            # Результат
            result: sqlite3.Cursor = self.__db.execute('INSERT INTO premium (id, expires) VALUES (?, ?)',
                                                       (self.__id, expires.strftime(
                                                           os.getenv('DATEFORMAT'))))
            connection.commit()
            return result
        except Exception:
            # Выбрасываем ошибку
            raise KeyError(f"Can't add premium. Premium is already added to id {self.__id}!")

    # Проверка существования
    def isExsist(self) -> bool:
        # Попытка найти пользователя
        self.__exsist = self.__db.execute(f'SELECT * FROM doctors WHERE id={self.__id}').fetchone() is not None
        # Возвращаем значение
        return self.__exsist

    # Создание записи
    def create(self, username: str, qualification: str, document: Union[bytes, type(None)],
               lang: str = 'ru', phone: int = 0) -> Union[Tuple[sqlite3.Cursor, sqlite3.Cursor, sqlite3.Cursor], bool]:
        # Подтверждаем существование
        self.__exsist = True
        # Если получено число
        if isinstance(self.__id, int):
            # Обращение к БД
            result1 = self.__db.execute(f'INSERT INTO doctors (id, username, lang, qualification, document) '
                                        f'VALUES (?, ?, ?, ?, ?)', (self.__id, username, lang, qualification,
                                                                    document))
            connection.commit()
            # Обновляем телефон
            result2 = self.update(self.Types.phone, phone)
            # Обращение к БД
            result3 = self.__db.execute(f'INSERT INTO settings (id) VALUES (?)', (self.__id,))
            connection.commit()
            # Возвращаем результат
            return result1, result2, result3
        else:
            # Выбрасываем ошибку
            raise TypeError("Username can't be recognized as 'int' type id!")

    # Удаление записи
    def remove(self) -> sqlite3.Cursor:
        # Удаляем запись о враче
        result = self.__db.execute(f'DELETE FROM doctors WHERE id={self.__id}')
        connection.commit()
        # Возвращаем результат
        return result

    # Получение настроек
    def getSettings(self) -> dict:
        return self.__settings

    # Обновление пользователя
    def update(self, types: Types, value) -> Union[sqlite3.Cursor, bool]:
        # Проверка типов данных
        if types == self.Types.phone:
            # Проверка параметра
            if isinstance(value, int):
                # Обновляем поле
                self.__phone = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE doctors SET phone={value} WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'phone' field requires the 'int' type!")
        elif types == self.Types.settings:
            # Проверка параметра
            if isinstance(value, dict):
                # Обновляем поле
                self.__settings = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE settings SET timezone="{value["timezone"]}", '
                                           f'surveys={value["surveys"]}, wallet={value["wallet"]} '
                                           f'WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'settings' field requires the 'dict' type!")
        elif types == self.Types.lang:
            # Проверка параметра
            if isinstance(value, str):
                # Обновляем поле
                self.__lang = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE doctors SET lang="{value}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'lang' field requires the 'str' type!")
        elif types == self.Types.qualification:
            # Проверка параметра
            if isinstance(value, str):
                # Обновляем поле
                self.__qualification = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE doctors SET qualification="{value}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'qualification' field requires the 'str' type!")
        elif types == self.Types.document:
            # Проверка параметра
            if isinstance(value, bytes):
                # Обращение к нейросети
                check: Union[str, bool] = ai.checkDocument(ai.ImageRecognize(value).textRecognize())
                # Проверка типа данных
                if isinstance(check, bool) and not check:
                    # Возвращаем результат
                    return check
                else:
                    # Обновляем поле
                    self.__document = value
                    # Обновляем БД
                    result = self.__db.execute(f'UPDATE doctors SET document={value} WHERE id={self.__id}')
                    connection.commit()
                    return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'document' field requires the 'byte' type!")
        elif types == self.Types.patients:
            # Проверка параметра
            if isinstance(value, Patient):
                # Существует
                exsist: Union[Patient, bool] = False
                # Подчинённые
                patients: List[int] = []
                # Иттерация по пациентам
                for patient in self.__patients:
                    # Если ID совпали
                    if value.get()['id'] == patient.get()['id']:
                        # Существует
                        exsist = patient
                        # Ломаем иттерацию
                        break
                # Если не существует
                if not exsist:
                    # Обновляем поле
                    self.__patients.append(value)
                else:
                    # Обновляем поле
                    self.__patients.remove(exsist)
                # Перебор пациентов
                for patient in self.__patients:
                    # Вносим пациента
                    patients.append(patient.get()['id'])
                # Обновляем БД
                result = self.__db.execute(f'UPDATE doctors SET patients="{json.dumps(patients)}" '
                                           f'WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'patients' field requires the 'list' type!")
        elif types == self.Types.subordinates:
            # Проверка параметра
            if isinstance(value, Doctor):
                # Существует
                exsist: Union[Doctor, bool] = False
                # Подчинённые
                subordinates: List[int] = []
                # Иттерация по врачам
                for doctor in self.__subordinates:
                    # Если врач существует
                    if doctor.get()['id'] == value.get()['id']:
                        # Существует
                        exsist = doctor
                        # Ломаем иттерацию
                        break
                # Если пользователя не существует
                if not exsist:
                    # Обновляем поле
                    self.__subordinates.append(value)
                else:
                    # Обновляем поле
                    self.__subordinates.remove(exsist)
                # Иттерация по врачам
                for doctor in self.__subordinates:
                    # Вносим ID в список
                    subordinates.append(doctor.get()['id'])
                # Обновляем БД
                result = self.__db.execute(f'UPDATE doctors SET subordinates="{json.dumps(subordinates)}" '
                                           f'WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'subordinates' field requires the 'list' type!")

    # Получение данных
    def get(self) -> dict:
        # Если есть телефон
        if self.__phone != 0:
            # Возвращаем словарь
            return {
                "id": self.__id,
                "username": self.__username,
                "phone": self.__phone,
                "lang": self.__lang,
                "qualification": self.__qualification,
                "discharged": self.__discharged,
                "document": self.__document,
                "exsist": self.__exsist
            }
        else:
            # Возвращаем словарь
            return {
                "id": self.__id,
                "username": self.__username,
                "lang": self.__lang,
                "qualification": self.__qualification,
                "discharged": self.__discharged,
                "document": self.__document,
                "exsist": self.__exsist
            }

    # Получение пациентов
    def getPatients(self) -> list:
        return self.__patients

    # Получение подчинённых
    def getSubordinates(self) -> list:
        return self.__subordinates

    # Сложение
    def __add__(self, other):
        # Если число
        if isinstance(other, int):
            try:
                # Обновляем БД
                count: int = int(self.__db.execute(f'SELECT * FROM doctors WHERE id={self.__id}').fetchone()[4])
                self.__db.execute(f'UPDATE doctors SET discharged={count + other} WHERE id={self.__id}')
                connection.commit()
            except TypeError:
                # Обновляем БД
                self.__db.execute(f'UPDATE doctors SET discharged=1 WHERE id={self.__id}')
                connection.commit()
        else:
            # Выбрасываем ошибку
            raise TypeError("Required 'int' type!")

    # Вычитание
    def __sub__(self, other):
        # Если число
        if isinstance(other, int):
            try:
                # Обновляем БД
                count: int = int(self.__db.execute(f'SELECT * FROM doctors WHERE id={self.__id}').fetchone()[4])
                self.__db.execute(f'UPDATE doctors SET discharged={count - other} WHERE id={self.__id}')
                connection.commit()
            except TypeError:
                # Выбрасываем ошибку
                raise TypeError(f"Count of doctor {self.__id} is less then 1")
        else:
            # Выбрасываем ошибку
            raise TypeError("Required 'int' type!")


# Тип данных истории болезни
@dataclass
class History:
    # Ответы на таблицу
    @dataclass
    class TableAnswers:
        # Переменные
        table: Table = None
        answers: List[str] = None

    # Диагноз
    @dataclass
    class Diagnosis:
        # Переменные
        title: str = "undefined"
        description: str = "undefined"
        neuralnetwork: bool = False

    # Переменные
    predict: str = "undefined"
    analyzes: str = "undefined"
    complaints: str = "undefined"
    description: str = "undefined"
    assigned: datetime.date = None
    medicines: List[str] = None
    doctors: List[Doctor] = None
    diagnoses: List[Diagnosis] = None
    answers: List[TableAnswers] = None


# Класс пациента
class Patient:
    # Ошибка истории
    class HistoryError(Exception):
        # Выдача текста
        def __str__(self):
            return "History format error in dict!"

    # Ошибка таблицы
    class TableError(Exception):
        # Выдача текста
        def __str__(self):
            return "Table format error in dict!"

    # Типы данных
    class Types(Enum):
        phone = 0,
        history = 1,
        tables = 2,
        age = 3,
        lang = 4,
        settings = 5

    # Проверка премиума
    def isPremium(self) -> Union[bool, tuple]:
        # Возвращаем результат
        return (database.execute(f'SELECT * FROM premium WHERE id={self.__id}').fetchone() is not None and
                database.execute(f'SELECT * FROM premium WHERE id={self.__id}').fetchone())

    # Добавление премиума
    def premiumAdd(self, expires: datetime.date = datetime.date.today()) -> sqlite3.Cursor:
        try:
            # Результат
            result: sqlite3.Cursor = database.execute('INSERT INTO premium (id, expires) VALUES (?, ?)',
                                                      (self.__id, expires.strftime(
                                                          os.getenv('DATEFORMAT'))))
            connection.commit()
            return result
        except Exception:
            # Выбрасываем ошибку
            raise KeyError(f"Can't add premium. Premium is already added to id {self.__id}!")

    # Парсинг истории болезни
    def __parseHistory(self, data: Union[History, dict]) -> Union[History, dict]:
        # Проверка типов
        if isinstance(data, dict):
            try:
                # Переменные
                medicines: List[str] = []
                doctors: List[Doctor] = []
                diagnoses: List[History.Diagnosis] = []
                answers: List[History.TableAnswers] = []
                # Если есть медикаменты
                if 'medicines' in data and data['medicines']:
                    # Перебор списка
                    for cure in data['medicines']:
                        # Добавляем лекарство
                        medicines.append(cure)
                # Если есть врачи
                if 'doctors' in data and data['doctors']:
                    # Перебор списка
                    for doctor in data['doctors']:
                        # Добавляем врача
                        doctors.append(Doctor(doctor))
                # Если есть диагнозы
                if 'diagnoses' in data and data['diagnoses']:
                    # Перебор списка
                    for diagnosis in data['diagnoses']:
                        # Добавляем диагнозы
                        diagnoses.append(History.Diagnosis(diagnosis['title'], diagnosis['description'],
                                                           diagnosis['neuralnetwork']))
                # Если есть ответы
                if 'answers' in data and data['answers']:
                    # Перебор списка
                    for answer in data['answers']:
                        # Табличные ответы
                        tableAns: History.TableAnswers = History.TableAnswers()
                        tableAns.table = self.__parseTable(answer['table'])
                        tableAns.answers = answer['answers']
                        # Добавляем ответы
                        answers.append(tableAns)
                # Возвращаем значение
                return History(data['predict'], data['analyzes'], data['complaints'],
                               data['description'], datetime.datetime.strptime(data['assigned'],
                                                                               os.getenv('DATEFORMAT')).date(),
                               medicines, doctors, diagnoses, answers)
            except Exception:
                # Выбрасываем ошибку
                raise self.HistoryError
        elif isinstance(data, History):
            # Списки
            doctors: List[int] = []
            diagnoses: List[dict] = []
            answers: List[dict] = []
            # Если есть доктора
            if data.doctors is not None and data.doctors:
                # Получаем ID докторов
                for doctor in data.doctors:
                    # Вносим ID в список
                    doctors.append(doctor.get()['id'])
            # Если есть диагнозы
            if data.diagnoses is not None and data.diagnoses:
                # Получаем диагнозы
                for diagnosis in data.diagnoses:
                    # Вносим диагноз в список
                    diagnoses.append({"title": diagnosis.title, "description": diagnosis.description,
                                      "neuralnetwork": diagnosis.neuralnetwork})
            # Если есть диагнозы
            if data.answers is not None and data.answers:
                # Получаем ответы
                for answer in data.answers:
                    # Вносим ответы
                    answers.append({"table": self.__parseTable(answer.table), "answers": answer.answers})
            # Возвращаем результат
            return {
                'predict': data.predict,
                'analyzes': data.analyzes,
                'complaints': data.complaints,
                'description': data.description,
                'assigned': data.assigned.strftime(os.getenv('DATEFORMAT')),
                'medicines': data.medicines,
                'diagnoses': diagnoses,
                'doctors': doctors,
                'answers': answers
            }

    # Парсинг таблицы
    @staticmethod
    def __parseTable(data: Union[Table, dict]) -> Union[Table, dict]:
        # Проверка типов
        if isinstance(data, Table):
            # Результат
            result: dict = {
                "id": data.id,
                "title": data.title,
                "expires": data.expires,
                "assigned": data.assigned,
                "replyable": data.replyable,
            }
            # Иттерация по вариантам
            for variant in range(len(data.variants)):
                # Если есть ключ
                if 'variants' in result:
                    # Вносим вариант
                    result['variants'].append({
                        "variants": data.variants[variant].variants,
                        "question": data.variants[variant].question
                    })
                else:
                    # Создаём список
                    result['variants'] = []
                    # Вносим вариант
                    result['variants'].append({
                        "variants": data.variants[variant].variants,
                        "question": data.variants[variant].question
                    })
            # Возвращаем словарь
            return result
        elif isinstance(data, dict):
            # Результат
            result: Table = Table()
            # Вносим значения
            result.id = data['id']
            result.title = data['title']
            result.expires = data['expires']
            result.assigned = data['assigned']
            result.replyable = data['replyable']
            result.variants = []
            # Если есть варианты
            if data['variants']:
                # Иттерация по списку
                for variant in data['variants']:
                    # Вариант
                    v: Table.Variant = Table.Variant()
                    # Наполняем вариант
                    v.variants = variant['variants']
                    v.question = variant['question']
                    # Вносим вариант
                    result.variants.append(v)
            # Возвращаем результат
            return result

    # Создание истории болезни
    def createHistory(self, doctors: Union[List[Doctor], type(None)] = None) -> Tuple[History, sqlite3.Cursor]:
        # Если есть доктора
        if doctors is not None:
            # История
            history: History = History(doctors=doctors, assigned=datetime.datetime.today())
            # Создаём историю
            return history, self.updateHistory(history)
        else:
            # История
            history: History = History(assigned=datetime.datetime.today())
            # Создаём историю
            return history, self.updateHistory(history)

    # Обновление истории
    def updateHistory(self, history: History) -> sqlite3.Cursor:
        # История болезни
        historyParsed: str = '"' + json.dumps(self.__parseHistory(history)).replace("\"", "\'") + '"'
        # Обновляем историю болезни
        result: sqlite3.Cursor = database.execute(f'UPDATE patients SET history=? WHERE id=?',
                                                  (historyParsed, self.__id))
        connection.commit()
        # Возвращаем результат
        return result

    # Инициализация
    def __init__(self, id: Union[int, str], db: sqlite3.Cursor = database):
        # Запрос
        result = None
        settings = None
        # Курсор
        self.__db: sqlite3.Cursor = db
        # Если получено число
        if isinstance(id, int):
            # Переменные
            self.__id: int = id
            self.__age: int = 0
            self.__sex: bool = False
            self.__lang: str = 'ru'
            self.__username: str = "undefined"
            self.__phone: int = 0
            self.__history: Union[History, type(None)] = None
            self.__tables: List[Table] = []
            self.__settings: dict = {}
            self.__exsist: bool = False
            # Попытка найти пользователя
            result = self.__db.execute(f'SELECT * FROM patients WHERE id={id}').fetchone()
            settings = self.__db.execute(f'SELECT * FROM settings WHERE id={id}').fetchone()
        # Если получена строка
        elif isinstance(id, str):
            # Переменные
            self.__id: int = 0
            self.__age: int = 0
            self.__sex: bool = False
            self.__lang: str = 'ru'
            self.__username: str = id
            self.__phone: int = 0
            self.__history: Union[History, type(None)] = None
            self.__tables: List[Table] = []
            self.__settings: dict = {}
            self.__exsist: bool = False
            # Попытка найти пользователя
            result = self.__db.execute(f'SELECT * FROM patients WHERE username={id}').fetchone()
            settings = self.__db.execute(f'SELECT * FROM settings WHERE id={id}').fetchone()
        # Проверка результата
        if result is not None:
            # Устанавливаем переменные
            self.__exsist = True
            self.__id = result[0]
            self.__sex = result[1]
            self.__lang = result[2]
            self.__age = result[3]
            self.__username = result[4]
            try:
                # Устанавливаем переменные
                self.__phone = result[5]
            except Exception:
                pass
            try:
                # Устанавливаем переменные
                self.__history = self.__parseHistory(json.loads(result[6].replace("'", '"')[1:][:-1]))
            except Exception:
                # Устанавливаем переменные
                self.__history = None
            try:
                # Перебор ключей
                for key in json.loads(result[7].replace('\"', '').replace("\'", '\"')):
                    try:
                        # Добавляем таблицу в список
                        self.__tables.append(self.__parseTable(key))
                    except Exception:
                        pass
            except Exception:
                pass
        if settings is not None:
            try:
                # Вносим в настройки
                self.__settings['timezone'] = settings[1]
                self.__settings['surveys'] = settings[2]
                self.__settings['wallet'] = settings[3]
            except Exception:
                pass

    # Создание пациента
    def create(self, username: str, age: int, sex: bool, doctors: Union[List[Doctor], type(None)] = None,
               lang: str = 'ru', phone: int = 0) -> Tuple[sqlite3.Cursor, sqlite3.Cursor]:
        # Подтверждаем существование
        self.__exsist = True
        # Если получено число
        if isinstance(self.__id, int):
            # Если есть доктор
            if doctors is not None:
                # Перебор списка
                for doctor in doctors:
                    # Запись к доктору
                    doctor.update(Doctor.Types.patients, doctor.getPatients().append(self))
            # Обращение к БД
            result = self.__db.execute(f'INSERT INTO patients (id, sex, lang, age, username, phone) '
                                       f'VALUES (?, ?, ?, ?, ?, ?)',
                                       (self.__id, sex, lang, age, username, phone))
            connection.commit()
            # Обращение к БД
            result1 = self.__db.execute(f'INSERT INTO settings (id) VALUES (?)', (self.__id,))
            connection.commit()
            # Возвращаем результат
            return result, result1
        else:
            # Выбрасываем ошибку
            raise TypeError("Username can't be recognized as 'int' type id!")

    # Проверка существования
    def isExsist(self) -> bool:
        # Попытка найти пользователя
        self.__exsist = self.__db.execute(f'SELECT * FROM patients WHERE id={self.__id}').fetchone() is not None
        # Возвращаем значение
        return self.__exsist

    # Получение данных
    def get(self) -> dict:
        # Если есть телефон
        if self.__phone != 0:
            # Возвращаем словарь
            return {
                "id": self.__id,
                "sex": self.__sex,
                "lang": self.__lang,
                "age": self.__age,
                "username": self.__username,
                "phone": self.__phone,
                "exsist": self.__exsist
            }
        else:
            # Возвращаем словарь
            return {
                "id": self.__id,
                "sex": self.__sex,
                "lang": self.__lang,
                "age": self.__age,
                "username": self.__username,
                "exsist": self.__exsist
            }

    # Получение истории
    def getHistory(self) -> Union[History, type(None)]:
        return self.__history

    # Получение таблиц
    def getTables(self) -> List[Table]:
        return self.__tables

    # Получение настроек
    def getSettings(self) -> dict:
        return self.__settings

    # Внесение таблиц
    def addTable(self, table: Table) -> sqlite3.Cursor:
        # Таблицы
        parsedTables: List[dict] = []
        # Вносим таблицу
        self.__tables.append(table)
        # Иттерация по таблицам
        for tab in self.__tables:
            # Вносим таблицу
            parsedTables.append(self.__parseTable(tab))
        # Изменённая таблица
        parsedData: str = '"' + json.dumps(parsedTables, ensure_ascii=False).replace("\"", "\'") + '"'
        # Обновляем БД
        result = self.__db.execute(f'UPDATE patients SET tables=?', (parsedData,))
        connection.commit()
        # Возвращаем результат
        return result

    # Удаление таблицы
    def removeTable(self, id: int) -> sqlite3.Cursor:
        # Таблицы
        parsedTables: List[dict] = []
        # Иттерация по списку
        for table in self.__tables:
            # Если найдено ID
            if table.id == id:
                # Удаялем таблицу
                self.__tables.remove(table)
                break
        # Иттерация по таблицам
        for table in self.__tables:
            # Вносим таблицу
            parsedTables.append(self.__parseTable(table))
        # Изменённая таблица
        parsedData: str = '"' + json.dumps(parsedTables, ensure_ascii=False).replace("\"", "\'") + '"'
        # Обновляем БД
        result = self.__db.execute(f'UPDATE patients SET tables=?', (parsedData,))
        connection.commit()
        # Возвращаем результат
        return result

    # Выписка пациента
    def extract(self, doctors: List[Doctor] = None) -> List[sqlite3.Cursor]:
        # Результат
        result: List[sqlite3.Cursor] = []
        # Если список не пустой
        if doctors and doctors is not None:
            # Иттерация по списку
            for doctor in doctors:
                # Выписка
                doctor + 1
                # Удаляем запись о пациенте
                result.append(self.__db.execute(f'DELETE FROM patients WHERE id={self.__id}'))
                connection.commit()
        else:
            # Удаляем запись о пациенте
            result.append(self.__db.execute(f'DELETE FROM patients WHERE id={self.__id}'))
            connection.commit()
        # Возвращаем результат
        return result

    # Обновление пользователя
    def update(self, types: Types, value) -> sqlite3.Cursor:
        # Проверка типов данных
        if types == self.Types.phone:
            # Проверка параметра
            if isinstance(value, int):
                # Обновление поля
                self.__phone = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE patients SET phone={value} WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'phone' field requires the 'int' type!")
        elif types == self.Types.settings:
            # Проверка параметра
            if isinstance(value, dict):
                # Обновляем поле
                self.__settings = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE settings SET timezone="{value["timezone"]}", '
                                           f'surveys={value["surveys"]}, wallet={value["wallet"]} '
                                           f'WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'settings' field requires the 'dict' type!")
        elif types == self.Types.lang:
            # Проверка параметра
            if isinstance(value, str):
                # Обновление поля
                self.__lang = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE patients SET lang="{value}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'lang' field requires the 'str' type!")
        elif types == self.Types.age:
            # Проверка параметра
            if isinstance(value, int):
                # Обновление поля
                self.__age = value
                # Обновляем БД
                result = self.__db.execute(f'UPDATE patients SET age="{value}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'history' field requires the 'int' type!")
        elif types == self.Types.history:
            # Проверка параметра
            if isinstance(value, History):
                # Обновляем БД
                result = self.__db.execute(f'UPDATE patients SET history='
                                           f'"{self.__parseHistory(value)}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'history' field requires the 'dict' type!")
        elif types == self.Types.tables:
            # Проверка параметра
            if isinstance(value, Table):
                # Обновление поля
                self.__tables.append(value)
                # Обновляем БД
                result = self.__db.execute(f'UPDATE patients SET '
                                           f'tables="{json.dumps(self.__parseTable(value))}" WHERE id={self.__id}')
                connection.commit()
                return result
            else:
                # Возвращаем ошибку
                raise TypeError("The 'tables' field requires the 'Table' type!")


# Класс администратора
class Admin:
    # Инициализация
    def __init__(self, user: Union[Patient, Doctor]):
        # Получаем пользователя
        self.__user = user
        # Получаем ID
        self.__id: int = self.__user.get()['id']
        # Заполняем поля
        self.__level: int = 0
        self.__prefix: str = "undefined"
        try:
            # Проверка документа
            with open(os.getenv('ADMINS'), 'r+', encoding=os.getenv('CODEC')) as f:
                # Получаем список
                data: List[dict] = json.loads(f.read())
                # Иттерация по списку
                for admin in data:
                    # Если админ существует
                    if admin['id'] == self.__id:
                        try:
                            # Назначаем уровень
                            self.__level = admin['level']
                            self.__prefix = admin['prefix']
                        except Exception:
                            pass
        except json.decoder.JSONDecodeError:
            pass

    # Запись админа
    def writeNewAdmin(self, level: int, prefix: str = "undefined") -> bool:
        try:
            # Проверка документа
            with open(os.getenv('ADMINS'), 'r+', encoding=os.getenv('CODEC')) as f:
                # Получаем список
                data: List[dict] = json.loads(f.read())
                # Иттерация по списку
                for admin in data:
                    # Если админ существует
                    if admin['id'] == self.__id:
                        # Возвращаем результат
                        return False
                # Запоминаем параметры
                self.__level = level
                self.__prefix = prefix
                # Создаем нового админа
                admin: dict = {
                    'id': self.__id,
                    'level': self.__level,
                    'prefix': self.__prefix
                }
            # Если есть список
            if data:
                # Запись в документ
                with open(os.getenv('ADMINS'), 'w+', encoding=os.getenv('CODEC')) as f:
                    # Читаем документ
                    document: List[dict] = data
                    # Вносим нового админа
                    document.append(admin)
                    # Записываем в файл
                    f.write(json.dumps(document))
                # Возвращаем результат
                return True
            else:
                # Запись в документ
                with open(os.getenv('ADMINS'), 'w+', encoding=os.getenv('CODEC')) as f:
                    # Создаём документ
                    document: List[dict] = [admin]
                    # Записываем в файл
                    f.write(json.dumps(document))
                # Возвращаем результат
                return True
        except json.decoder.JSONDecodeError:
            pass

    # Удаление админа
    def removeAdmin(self) -> bool:
        # Существует
        exsist: bool = False
        # Админ
        admin: dict = {
            'id': self.__id,
            'level': self.__level,
            'prefix': self.__prefix
        }
        try:
            # Проверка документа
            with open(os.getenv('ADMINS'), 'r', encoding=os.getenv('CODEC')) as f:
                # Получаем список
                data: List[dict] = json.loads(f.read())
                # Иттерация по списку
                for admin in data:
                    # Если админ существует
                    if admin['id'] == self.__id:
                        # Возвращаем результат
                        exsist = True
            # Если существует
            if exsist:
                # Если есть список
                if data:
                    # Запись в документ
                    with open(os.getenv('ADMINS'), 'w+', encoding=os.getenv('CODEC')) as f:
                        # Читаем документ
                        document: List[dict] = data
                        # Вносим нового админа
                        document.remove(admin)
                        # Записываем в файл
                        f.write(json.dumps(document))
                    # Возвращаем результат
                    return exsist
                else:
                    # Возвращаем результат
                    return exsist
            # Возвращаем результат
            return exsist
        except Exception:
            # Возвращаем результат
            return False

    # Получение пользователя
    def getUser(self) -> Union[Patient, Doctor]:
        return self.__user

    # Получение параметров
    def getAdmin(self) -> Union[dict, type(None)]:
        # Если админ
        if self.__level != 0:
            return {
                'level': self.__level,
                'prefix': self.__prefix
            }
        # Возвращаем ошибку
        return None


# Класс рекламы
class Ads:
    # Класс одной рекламы
    @dataclass
    class Ad:
        id: int = None
        label: str = None
        description: str = None
        author: Union[Doctor, Patient] = None
        experies: datetime.date = None
        photo: bytes = None
        exsist: bool = False

    # Инициализация
    def __init__(self, id: Union[int, Doctor, Patient]):
        # Тип рекламы
        adType = type(self.Ad())
        # Автор
        self.__author: Union[Doctor, Patient] = None
        # Список реклам
        self.__ads: List[adType] = []
        # Определяем тип переменной
        if isinstance(id, int):
            # Выполняем поиск по ID
            result: Union[tuple, type(None)] = database.execute('SELECT * FROM ads WHERE id=?',
                                                                (id,)).fetchone()
            # Если есть результат
            if result is not None:
                # Создаём рекламу
                ad: adType = self.Ad()
                # Получаем поля
                ad.id = id
                ad.label = result[1]
                ad.description = result[2]
                ad.author = getUser(int(result[3]))
                try:
                    # Получаем дату
                    ad.experies = datetime.datetime.strptime(result[5], '%Y%m%d')
                except Exception:
                    # Записываем ошибку
                    ad.experies = None
                try:
                    # Получаем фото
                    ad.photo = result[4]
                except Exception:
                    # Записываем ошибку
                    ad.photo = None
                # Если есть результат
                ad.exsist = result is not None
                # Вносим результат
                self.__ads.append(ad)
        elif isinstance(id, Doctor) or isinstance(id, Patient):
            # Автор
            self.__author: Union[Doctor, Patient] = id
            # Выполняем поиск по ID автора
            result: Union[list, type(None)] = database.execute('SELECT * FROM ads WHERE author=?',
                                                               (id.get()['id'],)).fetchall()
            # Если есть список
            if result is not None and result:
                # Иттерация по списку
                for item in result:
                    # Создаём рекламу
                    ad: adType = None
                    # Получаем поля
                    ad.id = item[0]
                    ad.author = id.get()['id']
                    ad.label = item[1]
                    ad.description = item[2]
                    try:
                        # Получаем дату
                        ad.experies = datetime.datetime.strptime(result[5], '%Y%m%d')
                    except Exception:
                        # Записываем ошибку
                        ad.experies = None
                    try:
                        # Получаем фото
                        ad.photo = item[4]
                    except Exception:
                        # Записываем ошибку
                        ad.photo = None
                    # Есть результат
                    ad.exsist = True
                    # Вносим результат
                    self.__ads.append(ad)

    # Создание рекламы
    def createAd(self, label: str, description: str, photo: Union[bytes, type(None)] = None,
                 author: Union[Doctor, Patient, type(None)] = None,
                 experies: Union[datetime.date, type(None)] = datetime.date.today() + datetime.timedelta(
                     days=int(os.getenv('ADEXP'))
                 )) -> sqlite3.Cursor:
        # Тип рекламы
        adType = type(self.Ad())
        # Если автор есть
        if self.__author is None and author is not None:
            # Назначаем автора
            self.__author = author
        # Если есть автор
        if self.__author is not None:
            # Если есть фото
            if photo is not None:
                # Создаём рекламу
                ad: adType = self.Ad()
                # Наполняем поля
                ad.author = self.__author
                ad.label = label
                ad.photo = photo
                ad.description = description
                try:
                    # Получаем дату
                    ad.experies = experies.strftime('%Y%m%d')
                except Exception:
                    # Записываем ошибку
                    ad.experies = None
                ad.exsist = True
                # Создаём рекламное объявление
                self.__ads.append(ad)
                # Делаем запрос к БД
                result: sqlite3.Cursor = database.execute('INSERT INTO ads SET label="?", '
                                                          'description="?", photo=?, author=?',
                                                          (label, description, photo,
                                                           self.__author.get()['id']))
                connection.commit()
                return result
            else:
                # Создаём рекламу
                ad: adType = self.Ad()
                # Наполняем поля
                ad.author = self.__author
                ad.label = label
                ad.description = description
                try:
                    # Получаем дату
                    ad.experies = experies.strftime('%Y%m%d')
                except Exception:
                    # Записываем ошибку
                    ad.experies = None
                ad.exsist = True
                # Создаём рекламное объявление
                self.__ads.append(ad)
                # Делаем запрос к БД
                result: sqlite3.Cursor = database.execute(
                    'INSERT INTO ads SET label="?", description="?", author=?',
                    (label, description, self.__author.get()['id']))
                connection.commit()
                return result
        else:
            # Выбрасываем ошибку
            raise KeyError("Author of ad is not set!")

    # Проверка рекламы
    def checkAd(self):
        # Если есть реклама
        if self.__ads:
            # Иттерация по рекламе
            for item in self.__ads:
                # Проверка типа даты
                if item is not None:
                    # Проверка срока давности
                    if item.experies == datetime.date.today():
                        # Удаляем рекламу
                        self.removeAd(item.id)

    # Удаление рекламы
    @staticmethod
    def removeAd(id: int) -> sqlite3.Cursor:
        # Запрос к базе данных
        result: sqlite3.Cursor = database.execute('DELETE FROM ads WHERE id=?', (id,))
        connection.commit()
        return result

    # Получение реклам
    def getAds(self) -> Union[List[Ad], type(None)]:
        # Если есть реклама
        if self.__ads:
            # Возвращаем результат
            return self.__ads
        # Возвращаем результат
        return None

    # Получение автора
    def authorGet(self) -> Union[Doctor, Patient, type(None)]:
        # Если есть реклама
        if self.__ads:
            # Возвращаем пользователя
            return self.__ads[0].author
        # Возвращаем результат
        return None


# Получение случайного врача
def getRandomDoctor() -> Union[Doctor, type(None)]:
    # Выполняем запрос
    doctor: Union[tuple, type(None)] = choice(database.execute('SELECT * FROM doctors').fetchall())
    # Если есть результат
    if doctor is not None:
        # Возвращаем результат
        return Doctor(doctor[0])
    # Возвращаем результат
    return None


# Получение списка пользователей
def getAllUserList(inThread: bool = False) -> List[Union[Patient, Doctor]]:
    # Если в потоке
    if inThread:
        # Открываем соединение
        db = connection.cursor()
        # Результат
        result: List[Union[Patient, Doctor]] = []
        # Получаем списки
        doctors: Union[tuple, type(None)] = db.execute('SELECT * FROM doctors').fetchall()
        patients: Union[tuple, type(None)] = db.execute('SELECT * FROM patients').fetchall()
        # Проверка типов
        if doctors is not None:
            # Иттерация по списку
            for doctor in doctors:
                # Добавляем результат
                result.append(Doctor(doctor[0], db))
        # Проверка типов
        if patients is not None:
            # Иттерация по списку
            for patient in patients:
                # Добавляем результат
                result.append(Patient(patient[0], db))
        # Возвращаем результат
        return result
    else:
        # Результат
        result: List[Union[Patient, Doctor]] = []
        # Получаем списки
        doctors: Union[tuple, type(None)] = database.execute('SELECT * FROM doctors').fetchall()
        patients: Union[tuple, type(None)] = database.execute('SELECT * FROM patients').fetchall()
        # Проверка типов
        if doctors is not None:
            # Иттерация по списку
            for doctor in doctors:
                # Добавляем результат
                result.append(Doctor(doctor[0]))
        # Проверка типов
        if patients is not None:
            # Иттерация по списку
            for patient in patients:
                # Добавляем результат
                result.append(Patient(patient[0]))
        # Возвращаем результат
        return result


# Получение случайного пациента
def getRandomPatient() -> Union[Patient, type(None)]:
    # Выполняем запрос
    patient: Union[tuple, type(None)] = choice(database.execute('SELECT * FROM patients').fetchall())
    # Если есть результат
    if patient is not None:
        # Возвращаем результат
        return Patient(patient[0])
    # Возвращаем результат
    return None


# Получение рекламного листа
def getAllAds(inThread: bool = False) -> Union[List[Ads.Ad], type(None)]:
    # Рекламы
    ads: Union[List[Ads.Ad], type(None)] = []
    # Если не в потоке
    if not inThread:
        # Выполняем запрос
        result: Union[list, type(None)] = database.execute(f'SELECT * FROM ads').fetchall()
        # Если есть результат
        if result is not None and result:
            # Иттерация по результатам
            for item in result:
                # Получаем рекламу
                ads.append(Ads(int(item[0])))
    else:
        # Создаём курсор
        db = connection.cursor()
        # Выполняем запрос
        result: Union[list, type(None)] = db.execute(f'SELECT * FROM ads').fetchall()
        # Если есть результат
        if result is not None and result:
            # Иттерация по результатам
            for item in result:
                # Получаем рекламу
                ads.append(Ads(int(item[0])))
    # Возвращаем результат
    return ads


# Удаление премиума
def removePremium(id: int) -> sqlite3.Cursor:
    # Удаляем пользователя
    return database.execute('DELETE FROM premium WHERE id=?', id)


def getUser(id: Union[int, str]) -> Union[Patient, Doctor, type(None)]:
    # Проверка типа
    if isinstance(id, int):
        # Выполняем запросы
        patient: Union[tuple, type(None)] = database.execute(f'SELECT * FROM patients WHERE id={id}').fetchone()
        doctor: Union[tuple, type(None)] = database.execute(f'SELECT * FROM doctors WHERE id={id}').fetchone()
        # Проверка условий
        if patient is None and doctor is not None:
            # Возвращаем врача
            return Doctor(id)
        elif patient is not None and doctor is None:
            # Возвращаем пациента
            return Patient(id)
        else:
            # Возвращаем ошибку
            return None
    elif isinstance(id, str):
        # Выполняем запросы
        patient: Union[tuple, type(None)] = database.execute(f'SELECT * FROM patients WHERE username={id}').fetchone()
        doctor: Union[tuple, type(None)] = database.execute(f'SELECT * FROM doctors WHERE username={id}').fetchone()
        # Проверка условий
        if patient is None and doctor is not None:
            # Возвращаем врача
            return Doctor(id)
        elif patient is not None and doctor is None:
            # Возвращаем пациента
            return Patient(id)
        else:
            # Возвращаем ошибку
            return None
