import fastapi
from fastapi import FastAPI, Query, Path, Body, UploadFile, File
import pydantic_models
from database import crud
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Главная страница
@api.get('/')
def index():
    return {"message": "Добро пожаловать в Bitcoin App!"}


# Обновляем юзера
@api.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_models.User_to_update = fastapi.Body()):
    """Обновляем юзера"""
    if user_id == user.id:
        return crud.update_user(user).to_dict()
    return {"error": "User ID mismatch"}


# Удаляем юзера
@api.delete('/user/{user_id}')
@crud.db_session
def delete_user(user_id: int = fastapi.Path()):
    """
    Удаляем юзера
    :param user_id:
    :return:
    """
    user = crud.get_user_by_id(user_id)
    if user:
        user.delete()
        return True
    return {"error": "User not found"}


# Создаем юзера
@api.post('/user/create')
def create_user(user: pydantic_models.User_to_create):
    """
    Создаем Юзера
    """
    return crud.create_user(tg_id=user.tg_ID, nick=user.nick if user.nick else None).to_dict()


@api.get("/test")
def test_connection():
    return {"status": "OK", "message": "Server is working"}


# Получаем инфу по юзеру
@api.get('/get_info_by_user_id/{user_id:int}')
@crud.db_session
def get_info_about_user(user_id):
    """
    Получаем инфу по юзеру
    """
    user = crud.User.get(id=user_id)
    if user:
        return crud.get_user_info(user)
    return {"error": "User not found"}


# Получаем баланс юзера
@api.get('/get_user_balance_by_id/{user_id:int}')
@crud.db_session
def get_user_balance_by_id(user_id):
    """
    Получаем баланс юзера
    :param user_id:
    :return:
    """
    user = crud.User.get(id=user_id)
    if user and user.wallet:
        crud.update_wallet_balance(user.wallet)
        return user.wallet.balance
    return {"error": "User or wallet not found"}


# Получаем общий баланс
@api.get('/get_total_balance')
@crud.db_session
def get_total_balance():
    """
    Получаем общий баланс

    """
    balance = 0.0
    crud.update_all_wallets()
    for user in crud.User.select()[:]:
        if user.wallet and user.wallet.balance is not None:
            balance += user.wallet.balance
    return balance

# Получаем всех юзеров
@api.get("/users")
@crud.db_session
def get_users():
    """
    Получаем всех юзеров
    :return:
    """
    users = []
    for user in crud.User.select()[:]:
        users.append(user.to_dict())
    return users


# Получаем юзера по айди его ТГ
@api.get("/user_by_tg_id/{tg_id:int}")
@crud.db_session
def get_user_by_tg_id(tg_id):
    """
    Получаем юзера по айди его ТГ
    :param tg_id:
    :return:
    """
    user = crud.User.get(tg_ID=tg_id)
    if user:
        return crud.get_user_info(user)
    return {"error": "User not found"}


# Получаем кошелек пользователя
@api.get("/get_user_wallet/{user_id:int}")
@crud.db_session
def get_user_wallet(user_id):
    """
    Получаем кошелек пользователя
    :param user_id:
    :return:
    """
    user = crud.User.get(id=user_id)
    if user and user.wallet:
        return crud.get_wallet_info(user.wallet)
    return {"error": "User or wallet not found"}


# Получаем все транзакции пользователя
@api.get("/get_user_transactions/{user_id:int}")
@crud.db_session
def get_user_transactions(user_id):
    """
    Получаем все транзакции пользователя (входящие и исходящие)
    :param user_id:
    :return:
    """
    return crud.get_user_transactions(user_id)


# Получаем все кошельки
@api.get("/wallets")
@crud.db_session
def get_wallets():
    """
    Получаем все кошельки
    :return:
    """
    wallets = []
    for wallet in crud.Wallet.select()[:]:
        wallets.append(crud.get_wallet_info(wallet))
    return wallets


# Получаем все транзакции
@api.get("/transactions")
@crud.db_session
def get_transactions():
    """
    Получаем все транзакции
    :return:
    """
    transactions = []
    for transaction in crud.Transaction.select()[:]:
        transactions.append({
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
    return transactions


# Создаем транзакцию - ИСПРАВЛЕННАЯ ФУНКЦИЯ
@api.post("/create_transaction/{user_id:int}")
@crud.db_session
def create_transaction(user_id: int, transaction_data: pydantic_models.Create_Transaction):
    """
    Создаем транзакцию
    """
    try:
        user = crud.User.get(id=user_id)
        if not user:
            return {"error": "User not found"}

        # Здесь должна быть реальная логика создания транзакции
        # Пока возвращаем заглушку с данными
        return {
            "message": "Транзакция создана (тестовый режим)",
            "sender": user_id,
            "receiver_address": transaction_data.receiver_address,
            "amount_btc_without_fee": transaction_data.amount_btc_without_fee,
            "status": "pending",
            "tx_hash": "test_tx_" + str(hash(str(user_id) + transaction_data.receiver_address))
        }
    except Exception as e:
        return {"error": str(e)}


# Загрузка файла
@api.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "saved_to": file_path,
        "file_size": os.path.getsize(file_path)
    }


# Список загруженных файлов
@api.get("/files/")
def list_files():
    if os.path.exists("uploads"):
        files = os.listdir("uploads")
        return {"uploaded_files": files}
    return {"uploaded_files": []}