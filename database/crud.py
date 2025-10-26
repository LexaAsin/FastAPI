# import datetime
# import pydantic_models
# import models
# import bit
# import config
#
# wallet = bit.PrivateKeyTestnet(config.testnet_wallet)  # наш кошелек готов и содержится в переменной wallet
# print(f"Баланс: {wallet.get_balance()}")
# print(f"Адрес: {wallet.address}")
# print(f"Приватный ключ: {wallet.to_wif()}")

import datetime
import bit
from database.db import *
from database.models import *
import config
from pony.orm import db_session



@db_session
def create_wallet(user=None, private_key=None, testnet=False):
    if not testnet:
        raw_wallet = bit.Key() if not private_key else bit.Key(private_key)
    else:
        raw_wallet = bit.PrivateKeyTestnet() if not private_key else bit.PrivateKeyTestnet(private_key)

    if user:
        wallet = Wallet(user=user, private_key=raw_wallet.to_wif(), address=raw_wallet.address)
    else:
        wallet = Wallet(private_key=raw_wallet.to_wif(), address=raw_wallet.address)

    flush()
    return wallet

@db_session
def create_user(tg_id: int, nick: str = None):
    if nick:
        user = User(tg_ID=tg_id, nick=nick, create_date=datetime.now(), wallet=create_wallet())
    else:
        user = User(tg_ID=tg_id, create_date=datetime.now(), wallet=create_wallet())
    flush()  # сохраняем объект в базе данных, чтобы получить его айди
    return user


@db_session
def create_transaction(
        sender: User,
        amount_btc_without_fee: float,
        receiver_address: str,
        fee: float | None = None,
        testnet: bool = False
):
    """
    :param amount_btc_without_fee: количество биткоинов исключая комиссию, значение в сатоши
    :param receiver_address: адрес получателя, строка с адресом
    :param fee: абсолютная комиссия, исчисляем в сатоши – необязательно.
    :param testnet: в тестовой сети ли мы работаем
    :return: Transaction object
    """

    # Тут мы загружаем в переменную wallet_of_sender кошелек отправителя
    # и если мы в тестовой сети, то соответственно мы загружаем кошелек из тестовой сети
    wallet_of_sender = bit.Key(sender.wallet.private_key) if not testnet else bit.PrivateKeyTestnet(
        sender.wallet.private_key)
    sender.wallet.balance = wallet_of_sender.get_balance()  # Получаем баланс кошелька

    if not fee:
        fee = bit.network.fees.get_fee() * 1000  # получаем стоимость транзакции sat/B и умножаем на 1000

    amount_btc_with_fee = amount_btc_without_fee + fee  # находим сумму включая комиссию

    if amount_btc_without_fee + fee > sender.wallet.balance:
        return f"Too low balance: {sender.wallet.balance}"

    # подготавливаем кортеж в списке с данными для транзакции
    output = [(receiver_address, amount_btc_without_fee, 'satoshi')]

    # отправляем транзакцию и получаем её хеш
    tx_hash = wallet_of_sender.send(output, fee, absolute_fee=True)

    # создаем объект транзакции и сохраняем его тем самым в нашей БД
    transaction = Transaction(sender=sender,
                              sender_wallet=sender.wallet,
                              fee=fee,
                              sender_address=sender.wallet.address,
                              receiver_address=receiver_address,
                              amount_btc_with_fee=amount_btc_with_fee,
                              amount_btc_without_fee=amount_btc_without_fee,
                              date_of_transaction=datetime.now(),
                              tx_hash=tx_hash)

    return transaction  # возвращаем объект с нашей транзакцией


@db_session
def update_wallet_balance(wallet):
    """
    Обновляем баланс кошелька (упрощенная версия)
    """
    try:
        # Просто устанавливаем тестовый баланс
        wallet.balance = 100000  # 0.001 BTC в сатоши
        return wallet.balance
    except Exception as e:
        print(f"❌ Ошибка при обновлении баланса: {e}")
        wallet.balance = 0
        return 0

@db_session
def update_all_wallets():
    """
    Обновляем балансы всех кошельков
    """
    try:
        for wallet in Wallet.select():
            update_wallet_balance(wallet)
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении всех кошельков: {e}")
        return False

@db_session
def get_user_by_id(id: int):
    return User[id]

@db_session
def get_user_by_tg_id(tg_id: int):
    return User.select(lambda u: u.tg_ID == tg_id).first()

@db_session
def get_transaction_info(transaction):
    return {"id": transaction.id,
        "sender": transaction.sender if transaction.sender else None,
        "receiver": transaction.receiver if transaction.receiver else None,
        "sender_wallet": transaction.sender_wallet if transaction.sender_wallet else None,
        "receiver_wallet": transaction.receiver_wallet if transaction.receiver_wallet else None,
        "sender_address": transaction.sender_address,
        "receiver_address": transaction.receiver_address,
        "amount_btc_with_fee": transaction.amount_btc_with_fee,
        "amount_btc_without_fee": transaction.amount_btc_without_fee,
        "fee": transaction.fee,
        "date_of_transaction": transaction.date_of_transaction,
        "tx_hash": transaction.tx_hash}

@db_session
def get_wallet_info(wallet):
    """
    Получаем информацию о кошельке
    """
    try:
        # Проверяем, что wallet - это объект, а не число
        if hasattr(wallet, 'id'):
            return {
                "id": wallet.id,
                "user": {},
                "balance": wallet.balance,
                "private_key": wallet.private_key,
                "address": wallet.address,
                "sended_transactions": [],
                "received_transactions": []
            }
        else:
            # Если передан ID вместо объекта
            wallet_obj = Wallet.get(id=wallet)
            if wallet_obj:
                return {
                    "id": wallet_obj.id,
                    "user": {},
                    "balance": wallet_obj.balance,
                    "private_key": wallet_obj.private_key,
                    "address": wallet_obj.address,
                    "sended_transactions": [],
                    "received_transactions": []
                }
            else:
                return {"error": "Wallet not found"}
    except Exception as e:
        print(f"❌ Ошибка в get_wallet_info: {e}")
        return {"error": str(e)}

@db_session
def get_user_info(user):
    return {"id": user.id,
        "tg_ID": user.tg_ID if user.tg_ID else None,
        "nick": user.nick if user.nick else None,
        "create_date": user.create_date,
        "wallet": get_wallet_info(user.wallet),
        "sended_transactions": user.sended_transactions if user.sended_transactions else [],
        "received_transactions": user.received_transactions if user.received_transactions else []}

@db_session
def update_user(user):
    user_to_update = User(user.id)
    if user.tg_ID:
        user_to_update.tg_ID = user.tg_ID
    if user.nick:
        user_to_update.nick = user.nick
    if user.create_date:
        user_to_update.create_date = user.create_date
    if user.wallet:
        user_to_update.wallet = user.wallet
    return user_to_update


@db_session
def get_user_transactions(user_id: int):
    """
    Получаем все транзакции пользователя (входящие и исходящие)
    """
    user = User[user_id]
    if not user:
        return []

    # Получаем исходящие транзакции
    sended = list(user.sended_transactions)
    # Получаем входящие транзакции
    received = list(user.received_transactions)

    # Объединяем и преобразуем в словари
    all_transactions = []

    for transaction in sended:
        all_transactions.append({
            'id': transaction.id,
            'sender': transaction.sender.id if transaction.sender else None,
            'receiver': transaction.receiver.id if transaction.receiver else None,
            'sender_address': transaction.sender_address,
            'receiver_address': transaction.receiver_address,
            'amount_btc': float(transaction.amount_btc),
            'fee': float(transaction.fee),
            'date': transaction.date.isoformat() if transaction.date else None,
            'tx_hash': transaction.tx_hash
        })

    for transaction in received:
        all_transactions.append({
            'id': transaction.id,
            'sender': transaction.sender.id if transaction.sender else None,
            'receiver': transaction.receiver.id if transaction.receiver else None,
            'sender_address': transaction.sender_address,
            'receiver_address': transaction.receiver_address,
            'amount_btc': float(transaction.amount_btc),
            'fee': float(transaction.fee),
            'date': transaction.date.isoformat() if transaction.date else None,
            'tx_hash': transaction.tx_hash
        })
    all_transactions.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)

    return all_transactions