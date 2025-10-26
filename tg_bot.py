import telebot
import config
import pydantic_models
import client
import json

bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        client.create_user({"tg_ID": message.from_user.id, "nick": message.from_user.username})
    except Exception as Ex:
        # Игнорируем ошибку если пользователь уже существует
        pass

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)

    text = f'Привет {message.from_user.full_name}, я твой бот-криптокошелек, \nу меня ты можешь хранить и отправлять биткоины'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Кошелек')
def wallet(message):
    try:
        # Получаем пользователя
        user_data = client.get_user_by_tg_id(message.from_user.id)

        # Получаем кошелек
        wallet = client.get_user_wallet_by_tg_id(message.from_user.id)

        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton('Меню')
        markup.add(btn1)

        # Безопасное получение данных
        if isinstance(wallet, dict):
            balance = wallet.get("balance")
            if balance is None:
                balance_text = "0.0"
            else:
                balance_btc = balance / 100000000
                balance_text = f"{balance_btc}"

            address = wallet.get("address", "Адрес не найден")

            text = f'💰 Ваш баланс: {balance_text} BTC\n' \
                   f'📍 Ваш адрес: {address}'
        else:
            text = f'❌ Ошибка: {wallet}'

        bot.send_message(message.chat.id, text, reply_markup=markup)

    except Exception as e:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton('Меню')
        markup.add(btn1)
        text = f'❌ Ошибка при получении кошелька: {str(e)}'
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Перевести')
def start_transaction(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите адрес кошелька куда хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # Сохраняем состояние пользователя
    if message.from_user.id not in states_of_users:
        states_of_users[message.from_user.id] = {}
    states_of_users[message.from_user.id]["STATE"] = "ADDRESS"


@bot.message_handler(regexp='История')
def history(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)

    try:
        # Получаем реальные транзакции пользователя
        user_data = client.get_user_by_tg_id(message.from_user.id)
        if isinstance(user_data, dict) and 'id' in user_data:
            transactions = client.get_user_transactions(user_data['id'])
            text = f'Ваши транзакции: \n{transactions}'
        else:
            text = f'Ошибка: {user_data}'
    except Exception as e:
        text = f'Ошибка при получении истории: {e}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Меню')
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)
    text = f'Главное меню'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['update'])
def update_balance(message):
    """Обновляем баланс кошелька"""
    try:
        # Получаем пользователя
        user_data = client.get_user_by_tg_id(message.from_user.id)
        if isinstance(user_data, dict) and 'id' in user_data:
            # Обновляем баланс через API
            balance = client.get_user_balance_by_id(user_data['id'])

            markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = telebot.types.KeyboardButton('Меню')
            markup.add(btn1)

            if isinstance(balance, (int, float)):
                balance_btc = balance / 100000000
                text = f'✅ Баланс обновлен: {balance_btc} BTC'
            else:
                text = f'ℹ️ {balance}'
        else:
            text = f'❌ Ошибка пользователя: {user_data}'

        bot.send_message(message.chat.id, text, reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка: {e}')


@bot.message_handler(regexp='Я в консоли')
def print_me(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    print(message.from_user.to_dict())
    text = f'Ты: {message.from_user.to_dict()}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Админка")
def admin_panel(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Общий баланс')
    btn2 = telebot.types.KeyboardButton('Все юзеры')
    btn3 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1, btn2, btn3)
    text = f'Админ-панель'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# ============ ПАГИНАЦИЯ ============

@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Все юзеры")
def all_users(message):
    show_users_page(message, 1)


def show_users_page(message, page):
    users = client.get_users()
    if not isinstance(users, list):
        bot.send_message(message.chat.id, f"Ошибка: {users}")
        return

    users_per_page = 4
    start_index = (page - 1) * users_per_page
    end_index = start_index + users_per_page

    total_pages = (len(users) + users_per_page - 1) // users_per_page

    inline_markup = telebot.types.InlineKeyboardMarkup()

    # Показываем пользователей текущей страницы
    for user in users[start_index:end_index]:
        inline_markup.add(telebot.types.InlineKeyboardButton(
            text=f'Юзер: {user["tg_ID"]}',
            callback_data=f"user_{user["tg_ID"]}"
        ))

    # Добавляем кнопки пагинации
    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(telebot.types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"page_{page - 1}"
        ))

    pagination_buttons.append(telebot.types.InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data="current"
    ))

    if page < total_pages:
        pagination_buttons.append(telebot.types.InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"page_{page + 1}"
        ))

    if pagination_buttons:
        inline_markup.add(*pagination_buttons)

    text = f'Юзеры (страница {page} из {total_pages}):'
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


def show_users_page_edit(call, page):
    users = client.get_users()
    if not isinstance(users, list):
        bot.edit_message_text(f"Ошибка: {users}", call.message.chat.id, call.message.message_id)
        return

    users_per_page = 4
    start_index = (page - 1) * users_per_page
    end_index = start_index + users_per_page

    total_pages = (len(users) + users_per_page - 1) // users_per_page

    inline_markup = telebot.types.InlineKeyboardMarkup()

    for user in users[start_index:end_index]:
        inline_markup.add(telebot.types.InlineKeyboardButton(
            text=f'Юзер: {user["tg_ID"]}',
            callback_data=f"user_{user["tg_ID"]}"
        ))

    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(telebot.types.InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"page_{page - 1}"
        ))

    pagination_buttons.append(telebot.types.InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data="current"
    ))

    if page < total_pages:
        pagination_buttons.append(telebot.types.InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"page_{page + 1}"
        ))

    if pagination_buttons:
        inline_markup.add(*pagination_buttons)

    text = f'Юзеры (страница {page} из {total_pages}):'
    bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_markup
    )


# ============ ОБРАБОТЧИК КОЛБЭКОВ ============

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    query_type = call.data.split('_')[0]

    if query_type == 'page':
        page = int(call.data.split('_')[1])
        show_users_page_edit(call, page)

    elif query_type == 'user':
        user_id = call.data.split('_')[1]
        users = client.get_users()
        if isinstance(users, list):
            inline_markup = telebot.types.InlineKeyboardMarkup()
            for user in users:
                if str(user['tg_ID']) == user_id:
                    inline_markup.add(
                        telebot.types.InlineKeyboardButton(text="Назад", callback_data='users'),
                        telebot.types.InlineKeyboardButton(text="Удалить юзера", callback_data=f'delete_user_{user_id}')
                    )

                    balance = client.get_user_balance_by_id(user['id'])
                    balance_text = balance if isinstance(balance, (int, float)) else "Ошибка"

                    bot.edit_message_text(
                        text=f'Данные по юзеру:\n'
                             f'ID: {user["tg_ID"]}\n'
                             f'Ник: {user.get("nick", "Нет ника")}\n'
                             f'Баланс: {balance_text}',
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=inline_markup
                    )
                    break

    elif query_type == 'users':
        show_users_page_edit(call, 1)

    elif query_type == 'delete' and call.data.split('_')[1] == 'user':
        user_id = int(call.data.split('_')[2])
        users = client.get_users()
        if isinstance(users, list):
            for user in users:
                if user['tg_ID'] == user_id:
                    client.delete_user(user['id'])
                    show_users_page_edit(call, 1)
                    break


@bot.message_handler(func=lambda message: message.from_user.id == config.tg_admin_id and message.text == "Общий баланс")
def total_balance(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    btn2 = telebot.types.KeyboardButton('Админка')
    markup.add(btn1, btn2)

    try:
        balance = client.get_total_balance()
        if isinstance(balance, (int, float)):
            balance_btc = balance / 100000000
            text = f'Общий баланс: {balance_btc} BTC'
        else:
            text = f'Ошибка: {balance}'
    except Exception as e:
        text = f'Ошибка: {e}'

    bot.send_message(message.chat.id, text, reply_markup=markup)


# ============ СИСТЕМА СОСТОЯНИЙ ДЛЯ ТРАНЗАКЦИЙ ============

states_of_users = {}


@bot.message_handler(
    func=lambda message: message.from_user.id in states_of_users and states_of_users[message.from_user.id].get(
        "STATE") == 'ADDRESS')
def get_amount_of_transaction(message):
    if message.text == "Меню":
        if message.from_user.id in states_of_users:
            del states_of_users[message.from_user.id]
        menu(message)
        return

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите сумму в сатоши, которую хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)

    states_of_users[message.from_user.id]["STATE"] = "AMOUNT"
    states_of_users[message.from_user.id]["ADDRESS"] = message.text


@bot.message_handler(
    func=lambda message: message.from_user.id in states_of_users and states_of_users[message.from_user.id].get(
        "STATE") == 'AMOUNT')
def get_confirmation_of_transaction(message):
    if message.text == "Меню":
        if message.from_user.id in states_of_users:
            del states_of_users[message.from_user.id]
        menu(message)
        return

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')

    if message.text.isdigit():
        text = f'Вы хотите перевести {message.text} сатоши,\nна биткоин-адрес {states_of_users[message.from_user.id]["ADDRESS"]}'
        confirm = telebot.types.KeyboardButton('Подтверждаю')
        markup.add(confirm)
        bot.send_message(message.chat.id, text, reply_markup=markup)

        states_of_users[message.from_user.id]["STATE"] = "CONFIRM"
        states_of_users[message.from_user.id]["AMOUNT"] = int(message.text)
    else:
        text = f'Вы ввели не число, попробуйте заново: '
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.from_user.id in states_of_users and states_of_users[message.from_user.id].get(
        "STATE") == 'CONFIRM')
def get_hash_of_transaction(message):
    if message.text == "Меню":
        if message.from_user.id in states_of_users:
            del states_of_users[message.from_user.id]
        menu(message)
    elif message.text == "Подтверждаю":
        try:
            result = client.create_transaction(
                message.from_user.id,
                states_of_users[message.from_user.id]['ADDRESS'],
                states_of_users[message.from_user.id]['AMOUNT']
            )
            bot.send_message(message.chat.id, f"Результат: {result}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {e}")

        if message.from_user.id in states_of_users:
            del states_of_users[message.from_user.id]
        menu(message)


bot.infinity_polling() #- отдельный запуск сервера и бота
# Терминал 1 - Сервер:
#
# uvicorn app:api --reload
# Терминал 2 - Бот:
#
# python tg_bot.py





# Threading код - НЕ ЗАРАБОТАЛ(((
# import threading
#
# def run_bot():
#     bot.infinity_polling()
#
# if __name__ == "__main__":
#     bot_thread = threading.Thread(target=run_bot)
#     bot_thread.daemon = True
#     bot_thread.start()
#
#     import uvicorn
#     uvicorn.run("app:api", host="127.0.0.1", port=8000, reload=True) #  uvicorn app:api --reload одна команда и запускается сервер и бот