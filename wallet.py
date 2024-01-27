"""
======================================
        HealthAI Telegram Бот
======================================
Разработчик: Савунов Александр
"""

# Библиотеки
from os import getenv
from dotenv import load_dotenv
from support import stringToBool
from yoomoney import Quickpay, Account
from yoomoney import Authorize, Client

# Инициализация
initializated: bool = False
load_dotenv()

# Холдер клиента
client: Client = None
user: Account = None

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

# Если требуется авторизация или не инициализировано
if stringToBool(getenv('NEEDAUTH')) or not initializated:
    # Выводим сообщение
    print('Authorizate is required!')
    # Авторизация
    Authorize(
          client_id=getenv('YOOMONEY'),
          redirect_uri=getenv('REDIRECT'),
          scope=["account-info",
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
