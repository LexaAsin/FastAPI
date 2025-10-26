import pydantic
from datetime import datetime


class User(pydantic.BaseModel):
    id: int
    tg_ID: int
    nick: str = None
    create_date: datetime
    wallet: 'Wallet'
    sended_transactions: list['Transaction'] = None
    received_transactions: list['Transaction'] = None

    class Config:
        arbitrary_types_allowed = True


class Transaction(pydantic.BaseModel):
    id: int
    sender: User = None
    receiver: User = None
    sender_wallet: 'Wallet' = None
    receiver_wallet: 'Wallet' = None
    sender_address: str
    receiver_address: str
    amount_btc_with_fee: float
    amount_btc_without_fee: float
    fee: float
    date_of_transaction: datetime
    tx_hash: str

    class Config:
        arbitrary_types_allowed = True


class Wallet(pydantic.BaseModel):
    id: int
    user: User
    balance: float = 0.0
    private_key: str
    address: str
    sended_transactions: list[Transaction] = []
    received_transactions: list[Transaction] = []

    class Config:
        arbitrary_types_allowed = True


class User_to_update(pydantic.BaseModel):
    id: int
    tg_ID: int = None
    nick: str = None
    create_date: datetime = None
    wallet: 'Wallet' = None

    class Config:
        arbitrary_types_allowed = True


class User_to_create(pydantic.BaseModel):
    tg_ID: int = None
    nick: str = None

    class Config:
        arbitrary_types_allowed = True


class Create_Transaction(pydantic.BaseModel):
    receiver_address: str
    amount_btc_without_fee: float

    class Config:
        arbitrary_types_allowed = True


# ========== PONY ORM МОДЕЛИ (ВТОРАЯ ЧАСТЬ ФАЙЛА) ==========

from datetime import datetime
from pony.orm import *

db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_ID = Required(int, unique=True)
    nick = Optional(str)
    create_date = Required(datetime)
    wallet = Required('Wallet')
    sended_transactions = Set('Transaction', reverse='sender')
    received_transactions = Set('Transaction', reverse='receiver')


class Transaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    sender = Optional(User, reverse='sended_transactions')
    receiver = Optional(User, reverse='received_transactions')
    sender_wallet = Optional('Wallet', reverse='sended_transactions')
    receiver_wallet = Optional('Wallet', reverse='received_transactions')
    sender_address = Optional(str)
    receiver_address = Optional(str)
    amount_btc_with_fee = Required(float)
    amount_btc_without_fee = Required(float)
    fee = Required(float)
    date_of_transaction = Required(datetime)
    tx_hash = Required(str, unique=True)


class Wallet(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Optional(User)
    balance = Required(float, default="0.0")
    private_key = Required(str, unique=True)
    address = Required(str, unique=True)
    sended_transactions = Set(Transaction, reverse='sender_wallet')
    received_transactions = Set(Transaction, reverse='receiver_wallet')

