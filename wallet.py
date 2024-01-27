"""
======================================
        HealthAI Telegram Бот
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
import json
import hashlib
from os import getenv
from typing import List
from dotenv import load_dotenv
from support import stringToBool
from random import randint, choice
from yoomoney import Quickpay, Account
from yoomoney import Authorize, Client, History

# Инициализация
initializated: bool = False
load_dotenv()

# Холдер клиента
client: Client = None
user: Account = None

# Открываем слова хэширования
with open(getenv('WORDS'), 'r') as fi:
    # Запоминаем слова
    hashWords: List[str] = json.loads(fi.read())

# Если есть ключ авторизации
if getenv('ACCESSTOKEN') is not None:
    try:
        # Создаём клиента
        client = Client(getenv('ACCESSTOKEN'))
        user = client.account_info()
        # Инициализировано
        initializated = True
    except Exception:
        # Не нициализировано
        initializated = False

# Если режим отладки
if stringToBool(getenv('DEBUG')) and initializated:
    # Выводим сообщение
    print("Wallet Service is initializated successfully!")
elif stringToBool(getenv('DEBUG')) and not initializated:
    # Выводим сообщение
    print("Error on initializate wallet services!")


# Класс чека
class BillOperations:
    # Инициализация
    def __init__(self, walletClient: Client = client, wallet: Account = user):
        # Применяем параметры
        self.__billList: List[str] = []
        self.__client: Client = walletClient
        self.__wallet: Account = wallet

    # Уникальные ID
    def createBill(self, label: str, ammount: int, minimum: int = 0, maximum: int = 10000):
        while True:
            # Генерируем ID
            newBill = randint(minimum, maximum)
            # Если ID не существует
            if newBill not in self.__billList:
                # Создаём ключ
                key: str = hashlib.md5(f'{choice(hashWords)}{newBill}{choice(hashWords)}'.encode()).hexdigest()
                # Вносим ключ
                self.__billList.append(key)
                # Создаём платёж
                return Quickpay(
                    receiver=self.__wallet.account,
                    quickpay_form="shop",
                    targets=label,
                    paymentType="SB",
                    sum=ammount,
                    label=key
                ).redirected_url

    # Проверка чека
    def checkBill(self, bill: str) -> bool:
        # Если в списке
        if bill in self.__billList:
            # Получаем историю платежей
            history: History = self.__client.operation_history(label=bill)
            # Иттерация по операциям
            for operation in history.operations:
                # Если успех
                if operation.status == 'success':
                    # Удаляем чек из списка
                    self.__billList.pop(bill)
                    # Возвращаем успех
                    return True
        # Возвращаем значение
        return False

    # Получение чеков
    def getBills(self) -> List[str]:
        return self.__billList


# Холдер операций
operations: BillOperations = BillOperations()

# Если требуется авторизация или не инициализировано
if stringToBool(getenv('NEEDAUTH')) or not initializated:
    # Выводим сообщение
    print('Authorizate is required!')
    # Авторизация
    Authorize(
        client_id=getenv('YOOMONEY'),
        redirect_uri=getenv('REDIRECT'),
        scope=[
            "account-info",
            "operation-history",
            "operation-details",
            "incoming-transfers",
            "payment-p2p",
            "payment-shop",
        ]
    )
elif initializated:
    # Если режим отладки
    if stringToBool(getenv('DEBUG')):
        # Выводим информацию о клиенте
        print("Account number:", user.account)
        print("Account balance:", user.balance)
        print("Account currency code in ISO 4217 format:", user.currency)
        print("Account status:", user.account_status)
        print("Account type:", user.account_type)
        print("Extended balance information:")
        for pair in vars(user.balance_details):
            print("\t-->", pair, ":", vars(user.balance_details).get(pair))
        print("Information about linked bank cards:")
        cards = user.cards_linked
        if len(cards) != 0:
            for card in cards:
                print(card.pan_fragment, " - ", card.type)
        else:
            print("No card is linked to the account")
