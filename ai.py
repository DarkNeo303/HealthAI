"""
======================================
        HealthAI Telegram Бот
       Исскуственный Интеллект
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
import os
import g4f
import json
import base64
import requests
import datetime
from pyqadmin import admin
from typing import Union, List
from dotenv import load_dotenv
from spellchecker import SpellChecker
from support import stringToBool, similarity, checkInt

# Инициализация
load_dotenv()

# Контент шаблонов
templates: dict = {}
initialized: bool = False

# Читаем файл взлома GPT
with open('hack.json', 'r', encoding=os.getenv('CODEC')) as hackFile:
    # Запоминаем содержимое
    hack: dict = json.loads(hackFile.read())


# Метод управления запросом
def getResponse(message: str,
                model: str = str(os.getenv("GPT")),
                provider: g4f.Provider = g4f.Provider.Aura, useHack: bool = True) -> str:
    # Если режим отладки
    if stringToBool(os.getenv("DEBUG")):
        # Доступные провайдеры
        print([
            provider.__name__
            for provider in g4f.Provider.__providers__
            if provider.working
        ])
    try:
        # Если нужно использовать взлом
        if useHack:
            # Ответ
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider,
                messages=[{"role": "user", "content": hack['prompt'] + message}],
            )
        else:
            # Ответ
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider,
                messages=[{"role": "user", "content": message}],
            )
        # Если режим отладки
        if stringToBool(os.getenv("DEBUG")):
            # Выводим ответ
            print(f"ChatGPT response: {response}")
        # Проверка ответа
        if response != "":
            # Возвращаем значение
            return response
        else:
            # Выбрасываем ошибку
            raise TimeoutError(f"ChatGPT error :/")
    except Exception as e:
        # Если режим отладки
        if stringToBool(os.getenv("DEBUG")):
            # Выводим ошибку
            print(f"ChatGPT error at {e}")
        # Выбрасываем ошибку
        raise TimeoutError(f"ChatGPT error at {e}")


# Распознавание фото
class ImageRecognize:
    # Переменные
    __text: Union[str, List[str]] = ""

    # Инициализация
    def __init__(self, img: bytes, lang: str = "rus"):
        # Запоминаем путь
        self.__lang = lang
        self.__image: bytes = img

    # Получение пути
    def getImage(self) -> bytes:
        return self.__image

    # Получение текста
    def getText(self) -> Union[str, List[str]]:
        # Проверка текста
        if self.__text != "" and self.__text != []:
            # Возвращаем значение
            return self.__text
        else:
            # Выбрасываем ошибку
            raise KeyError("Text isn't recognized! Try 'textRecognize' method")

    # Восстановление повреждений
    def __recoverText(self) -> Union[str, bool, List[str]]:
        # Реставрация текста
        recover: str = getResponse(f"Исправь текст, расположи исправленные варианты через запятую. "
                                   f"Верни варианты как список Python. В ответе оставь только список: "
                                   f"{','.join(self.__text.split())}")
        # Сокращение текста до исходного, перевод в список
        self.__text = (','.join(']'.join(recover.split(']')[:])[recover.find("["):]).replace("[", "")
                       .replace("]", "").replace("'", "").replace('"', "")
                       .replace(',', '').split())
        # Проверка типа
        if isinstance(self.__text, str):
            # Проверка на качество
            if not self.__text not in SpellChecker(language=self.__lang[:-1]).candidates(self.__text):
                # Выбрасываем ошибку
                return False
            else:
                # Если режим отладки
                if stringToBool(os.getenv("DEBUG")):
                    print(f"Output: {self.__text}")
                # Выбрасываем текст
                return self.__text
        elif isinstance(self.__text, list):
            # Если режим отладки
            if stringToBool(os.getenv("DEBUG")):
                # Выводим режим отладки
                print(f"Input: {self.__text}")
            # Переменные
            strings: int = 0
            booleans: int = 0
            # Выходной текст
            result: List[Union[str, bool]] = []
            # Перебор списка
            for item in self.__text:
                # Орфография
                spell: Union[dict, type(None)] = SpellChecker(language=self.__lang[:-1]).candidates(item)
                # Проверка на качество
                if spell is None or len(item) <= 2 or checkInt(item):
                    # Выбрасываем ошибку
                    result.append(item)
                else:
                    # Выбрасываем текст
                    result.append(list(spell)[0])
            # Проверка кол-ва правильных слов
            for item in result:
                # Проверка типа
                if isinstance(item, str):
                    strings += 1
                elif isinstance(item, bool):
                    booleans += 1
            # Проверка результатов
            if strings >= booleans:
                # Если режим отладки
                if stringToBool(os.getenv("DEBUG")):
                    print(f"Output: {self.__text}")
                return self.__text
            else:
                # Если режим отладки
                if stringToBool(os.getenv("DEBUG")):
                    print(f"Output: False")
                return False

    # Распознавание текста
    def textRecognize(self) -> Union[str, bool]:
        try:
            # Распознаём текст
            self.__text = json.loads(requests.post(
                os.getenv("OCR"),
                headers={'apikey': os.getenv("KEY")},
                data={'language': self.__lang, 'base64image': f"data:image/jpeg;base64,"
                                                              f"{base64.b64encode(self.__image).decode()}"}
            ).content)['ParsedResults'][0]['ParsedText']
            # Запоминаем текст
            self.__text = self.__recoverText()
            # Исправление недочётов
            return self.__text
        except Exception:
            # Выбрасываем ошибку
            raise Exception(requests.post(
                os.getenv("OCR"),
                headers={'apikey': os.getenv("KEY")},
                data={'language': self.__lang, 'base64image': f"data:image/jpeg;base64,"
                                                              f"{base64.b64encode(self.__image).decode()}"}
            ).content)


# Обработка шаблонов
@admin
def trainDocumentScaner(path: str = 'templates'):
    # Глобальные переменные
    global initialized
    # Иттерация по изображениям
    for image in os.listdir(path):
        # Открываем фото
        with open(f'{path}/{image}', 'rb') as f:
            # Перебираем доступные языки
            for ln in os.getenv("SUPPORTEDLANGS").split(', '):
                # Результат
                result: Union[str, bool] = False
                try:
                    # Распознаём текст
                    result = ImageRecognize(f.read(), ln).textRecognize()
                except Exception as e:
                    # Если режим отладки
                    if stringToBool(os.getenv("DEBUG")):
                        # Выбрасываем ошибку
                        print(f"\n!! WARNING !!\n{e}\n")
                # Если есть результат
                if isinstance(result, str) or isinstance(result, list):
                    # Запись в словарь
                    templates[image.split('.')[0]] = result
                    # Если режим отладки
                    if stringToBool(os.getenv("DEBUG")):
                        # Выводим текст
                        print(f"Result is: {result}")
    # Проверка файлов
    if 'train.json' in os.listdir():
        # Переменные
        name: str = f'hash-{str(datetime.datetime.now()).replace(":", "-")
                            .replace(".", "")}.json'
        # Переназываем файл
        os.rename('train.json', name)
        try:
            # Перемещаем файл
            os.replace(name, './hash')
        except PermissionError:
            pass
    # Сохранение файла
    with open('train.json', 'w+', encoding=os.getenv('CODEC')) as f:
        # Запись массива
        f.write(json.dumps(templates))
    # Инициализирован
    initialized = True
    # Если режим отладки
    if stringToBool(os.getenv("DEBUG")):
        # Выводим информацию в консоль
        print(f"Training is complete! Status is - {initialized}")


# Проверка документа на подлинность
def checkDocument(text: str) -> bool:
    # Проверка инициализации
    if initialized:
        # Переменные
        result: int = 0
        # Перебор словаря
        for key in templates.keys():
            # Прибавляем проценты
            result += 1 + (result + similarity(text.split(), templates[key])) / 100
        # Возвращаем результат
        return result >= int(os.getenv("ACCUR"))
    else:
        # Выбрасываем ошибку
        raise TimeoutError("Templates is not initialized yet!")


# Инициализация
def initAi() -> bool:
    # Глобальные переменные
    global initialized, templates
    # Если необходима тренировка
    if stringToBool(os.getenv("TRAIN")):
        # Если режим отладки
        if stringToBool(os.getenv("DEBUG")):
            # Выводим результат
            print("Training is started...")
        # Запускаем обучение на шаблонах
        trainDocumentScaner()
    else:
        try:
            # Открываем файл
            with open('train.json', 'r', encoding=os.getenv('CODEC')) as f:
                # Читаем значения
                templates = json.loads(f.read())
            # Инициализировано
            initialized = False
        except Exception:
            # Инициализировано
            initialized = False
            # Выбрасываем ошибку
            raise FileNotFoundError("Train data isn't generated!")
    # Возвращаем значение
    return initialized
