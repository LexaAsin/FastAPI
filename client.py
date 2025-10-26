import requests
import pydantic_models
from config import api_url


def update_user(user: dict):
    """Обновляем юзера"""
    try:
        user = pydantic_models.User_to_update.validate(user)
        response = requests.put(f'{api_url}/user/{user.id}', data=user.json())
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def delete_user(user_id: int):
    """Удаляем юзера"""
    try:
        response = requests.delete(f'{api_url}/user/{user_id}')
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def create_user(user: pydantic_models.User_to_create):
    """Создаем Юзера"""
    try:
        user = pydantic_models.User_to_create.validate(user)
        response = requests.post(f'{api_url}/user/create', data=user.json())
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_info_about_user(user_id):
    """Получаем инфу по юзеру"""
    try:
        response = requests.get(f'{api_url}/get_info_by_user_id/{user_id}')
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_user_balance_by_id(user_id):
    """Получаем баланс юзера"""
    try:
        response = requests.get(f'{api_url}/get_user_balance_by_id/{user_id}')
        if response.status_code == 200:
            try:
                return float(response.text)
            except:
                return response.text
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_total_balance():
    """Получаем общий баланс"""
    try:
        response = requests.get(f'{api_url}/get_total_balance')
        if response.status_code == 200:
            try:
                return float(response.text)
            except:
                return response.text
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_users():
    """Получаем всех юзеров"""
    try:
        print(f"🔍 Client: Запрос всех пользователей")
        response = requests.get(f"{api_url}/users")
        print(f"🔍 Client: Статус: {response.status_code}")
        print(f"🔍 Client: Текст: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        print(f"🔍 Client: Исключение: {e}")
        return f"Error: {str(e)}"


def get_user_wallet_by_tg_id(tg_id):
    """Получаем кошелек пользователя по TG ID"""
    try:
        user_dict = get_user_by_tg_id(tg_id)

        if isinstance(user_dict, dict) and 'id' in user_dict:
            response = requests.get(f"{api_url}/get_user_wallet/{user_dict['id']}")
            if response.status_code == 200:
                return response.json()
            else:
                return f"Wallet Error {response.status_code}: {response.text}"
        else:
            return f"User Error: {user_dict}"

    except Exception as e:
        return f"Error: {str(e)}"


def get_user_by_tg_id(tg_id):
    """Получаем юзера по айди его ТГ"""
    try:
        response = requests.get(f"{api_url}/user_by_tg_id/{tg_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    """Создаем транзакцию"""
    try:
        user_dict = get_user_by_tg_id(tg_id)

        if isinstance(user_dict, dict) and 'id' in user_dict:
            payload = {
                'receiver_address': receiver_address,
                'amount_btc_without_fee': amount_btc_without_fee
            }
            response = requests.post(
                f"{api_url}/create_transaction/{user_dict['id']}",
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                return f"Transaction Error {response.status_code}: {response.text}"
        else:
            return f"User Error: {user_dict}"

    except Exception as e:
        return f"Error: {str(e)}"


def get_user_transactions(user_id: int):
    """Получаем список транзакций пользователя"""
    try:
        response = requests.get(f"{api_url}/get_user_transactions/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_wallets():
    """Получаем все кошельки"""
    try:
        response = requests.get(f"{api_url}/wallets")
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_all_transactions():
    """Получаем все транзакции"""
    try:
        response = requests.get(f"{api_url}/transactions")
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"