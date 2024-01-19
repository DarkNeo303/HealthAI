"""
======================================
        HealthAI Telegram Бот
       Вспомогательные функции
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
import difflib
from dotenv import load_dotenv

# Инициализация
load_dotenv()

# Оперативная память
ram: dict = {}


# Функция проверки числа
def checkInt(string: str) -> bool:
    try:
        int(string)
        return True
    except Exception:
        return False


# Функция switch
class Switch(object):
    # Инициализация
    def __init__(self, value):
        self.value = value
        self.fall = False

    # При иттерации
    def __iter__(self):
        yield self.match
        raise StopIteration

    # При совпадении
    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        return False


# Сходство списков
def similarity(s1: list, s2: list) -> int:
    # Находим совпадения
    matcher = difflib.SequenceMatcher(None, s1, s2)
    # Возвращаем проценты
    return int(matcher.ratio()) * 100


# Строку в условие
def stringToBool(text: str) -> bool:
    # Возвращаем проверку условия
    return text == "True" or text == "true" or text == "1"
