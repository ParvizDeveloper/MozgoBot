import telebot
from telebot import types
import psycopg2
import os
from datetime import datetime
import time

bot = telebot.TeleBot('')

IMAGE_DIR = './images/img_games/'

# Подключение к базе данных
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = 'postgres'
DB_PASSWORD = '6653'
DB_NAME = 'mzgbDb'

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
connection = get_db_connection()

cursor = connection.cursor()
# Создание таблиц
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS public.games (
        id SERIAL PRIMARY KEY,
        name_game VARCHAR(200),
        name_theme VARCHAR(200),
        game_date VARCHAR(200),
        time VARCHAR(200),
        place VARCHAR(200),
        address VARCHAR(200),
        price INTEGER,
        is_now BOOLEAN,
        picture VARCHAR(200)
    );
    ''')
    connection.commit()
    cursor.close()
    connection.close()


cursor.execute('''
CREATE TABLE IF NOT EXISTS public.people
(
    id serial NOT NULL,
    name character varying(200),
    phone_number character varying(20),
    user_id bigint,
    which_game character varying(200),
    name_team character varying(200),
    PRIMARY KEY (id)
);
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS public.teams
(
    id serial NOT NULL,
    name_leader character varying(200),
    team_name character varying(20),
    user_id_leader bigint,
    game_reg character varying(200),
    PRIMARY KEY (id)
);
''')
# обработка /start
@bot.message_handler(commands=['start'])
def main(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    cursor.execute(f"SELECT * FROM public.people WHERE user_id = '{user_id}'")
    check = cursor.fetchone()
    if not check:
        cursor.execute(f"INSERT INTO public.people (name, user_id) VALUES ('{user_name}', {user_id})")
    else:
        pass
    connection.commit()
    file = open('./images/mzgb_logo.jpg', 'rb')
    bot.send_photo(message.chat.id, file)
    bot.send_message(message.chat.id, '<b>Привет!</b>👋 \n \n'
                                      'Добро пожаловать на Мозгобойню — увлекательный квиз, где можно проверить свои знания и'
                                      'посоревноваться с друзьями! 🧠🎉 \n \n'
                                      'Каждый раунд включает вопросы по разным темам: от истории и науки до поп-культуры и '
                                      'спорта. 📚🎬⚽ Покажите, на что вы способны, и станьте чемпионом Мозгобойни! 🏆 \n \n'
                                      'Удачи! 🍀', parse_mode='html')
    bot.send_message(message.chat.id, 'Для того чтобы принять участие в игре, вам нужно зарегестрировать свою команду.')


# регистрация
@bot.message_handler(commands=['register'])
def register(message):
    markup = types.InlineKeyboardMarkup()
    btn2 = types.InlineKeyboardButton('Да', callback_data='yes')
    btn3 = types.InlineKeyboardButton('Нет', callback_data='no')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Для регистрации команды вы должны будете отправить свой номер телефона. Вы согласны?', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'yes':
        # Удаляем предыдущее сообщение
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

        # Создаем клавиатуру для запроса контакта
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        item = telebot.types.KeyboardButton('Поделиться моим номером телефона', request_contact=True) #
        markup.add(item)

        # Отправляем запрос контакта с новой клавиатурой
        bot.send_message(callback.message.chat.id, "Поделись своим номером телефона, пожалуйста.", reply_markup=markup) # запрос контакта

    elif callback.data == 'no':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Вам нужно пройти регистрацию.')  # отмена регистрации


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    contact = message.contact
    phone_number = contact.phone_number
    user_id = message.from_user.id

    # Удаляем клавиатуру после получения контакта
    bot.send_message(message.chat.id, "Проверяю вас в нашей базе данных...", reply_markup=telebot.types.ReplyKeyboardRemove())
    time.sleep(1.5)

    cursor.execute(f"SELECT * FROM public.people WHERE phone_number = '{phone_number}'")
    existing_entry = cursor.fetchone()

    if existing_entry:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы у нас")
    else:
        bot.send_message(message.chat.id, "Успешная регистрация! Поздравляю\nДля регистрации команды введите /register_team "
                                          "\nСписок активных игр можете посмотреть в /games")
        cursor.execute(f"""UPDATE public.people SET phone_number = '{phone_number}' WHERE user_id = {user_id};""")
        connection.commit()


# Авторизация админа
@bot.message_handler(commands=['admin'])
def main(message):
    user_id = message.from_user.id
    if user_id == 577593785:
        bot.send_message(message.chat.id, 'Вы авторизовались как администратор. \n \n'
                                          'Доступные команды: /add_game , /del_game'
                         )
    else:
        bot.send_message(message.chat.id, 'Ошибка. Недостаточно прав доступа.')

# Функция добавления игры в базу данных
def adder(name_game, name_theme, game_date, time, place, address, price, is_now, picture):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO public.games 
        (name_game, name_theme, game_date, time, place, address, price, is_now, picture)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (name_game, name_theme, game_date, time, place, address, price, is_now, picture))

    connection.commit()
    cursor.close()
    connection.close()

# Стартовый запрос к пользователю для ввода данных
@bot.message_handler(commands=['add_game'])
def start_add_game(message):
    user_id = message.from_user.id
    if user_id == 577593785:
        bot.send_message(message.chat.id, "Введите тематику игры (например: Вечные хиты или если особой тематики нет, "
                                          "как например в 'Классика', то просто отправьте '-'):")
        bot.register_next_step_handler(message, process_name_game)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Недостаточно прав доступа.')

# Обработка названия игры
def process_name_game(message):
    name_game = message.text
    bot.send_message(message.chat.id, "Введите название игры (например: Туц-Туц Квиз):")
    bot.register_next_step_handler(message, process_name_theme, name_game)

# Обработка темы игры
def process_name_theme(message, name_game):
    name_theme = message.text
    bot.send_message(message.chat.id, "Введите дату игры (например: 09-11-2024):")
    bot.register_next_step_handler(message, process_game_date, name_game, name_theme)

# Обработка даты игры
def process_game_date(message, name_game, name_theme):
    game_date = message.text
    bot.send_message(message.chat.id, "Введите время игры (например: 19:00):")
    bot.register_next_step_handler(message, process_time, name_game, name_theme, game_date)

# Обработка времени игры
def process_time(message, name_game, name_theme, game_date):
    time = message.text
    bot.send_message(message.chat.id, "Введите место проведения игры (например: Nebo):")
    bot.register_next_step_handler(message, process_place, name_game, name_theme, game_date, time)

# Обработка места игры
def process_place(message, name_game, name_theme, game_date, time):
    place = message.text
    bot.send_message(message.chat.id, "Введите адрес игры (например: ул. А.Темура 53):")
    bot.register_next_step_handler(message, process_address, name_game, name_theme, game_date, time, place)

# Обработка адреса игры
def process_address(message, name_game, name_theme, game_date, time, place):
    address = message.text
    bot.send_message(message.chat.id, "Введите цену участия в игре (например: 50000):")
    bot.register_next_step_handler(message, process_price, name_game, name_theme, game_date, time, place, address)

# Обработка цены игры
def process_price(message, name_game, name_theme, game_date, time, place, address):
    try:
        price = int(message.text)
        bot.send_message(message.chat.id, "Активен ли набор на игру? (Ответьте 'True' или 'False'):")
        bot.register_next_step_handler(message, process_is_now, name_game, name_theme, game_date, time, place, address, price)
    except ValueError:
        process_address(message, name_game, name_theme, game_date, time, place)

# Обработка статуса игры (играем ли сейчас)
def process_is_now(message, name_game, name_theme, game_date, time, place, address, price):
    is_now = message.text.lower() == 'true'
    bot.send_message(message.chat.id, "Отправьте фотографию игры:")
    bot.register_next_step_handler(message, process_picture, name_game, name_theme, game_date, time, place, address, price, is_now)


# Обработка картинки игры
def process_picture(message, name_game, name_theme, game_date, time, place, address, price, is_now):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)

        file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        file_path = os.path.join(IMAGE_DIR, file_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        adder(name_game, name_theme, game_date, time, place, address, price, is_now, file_path)

        bot.send_message(message.chat.id, f"Игра '{name_game}' успешно добавлена!")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию.")
connection.commit()



@bot.message_handler(commands=['games'])
def main(message):
    user_id = message.from_user.id
    cursor.execute(f"SELECT phone_number FROM public.people WHERE user_id = {user_id}")
    existing_entry = cursor.fetchone()
    if existing_entry is not None and existing_entry[0] is not None:
        bot.send_message(message.chat.id, 'Вот список доступных игр:')
        cursor.execute('''SELECT * FROM public.games''')
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                id, name_game, name_theme, game_date, time, place, address, price, is_now, picture = row
                file = open(picture, 'rb')
                bot.send_photo(message.chat.id, file)
                if is_now:
                    now = 'Да'
                else:
                    now = 'Нет'
                bot.send_message(message.chat.id,
                                 f"Номер игры: {id}\nТема игры: {name_game}\nТип игры: {name_theme}\nДата проведения: "
                                 f"{game_date}\nВремя: {time}\nМесто проведения: {place}\n"
                                 f"Адрес: {address}\nЦена за учасника: {price} сум\nДоступна для регистрации? {now}\n")
        else:
            bot.send_message(message.chat.id, 'Пока нет досутпных игр')

    else:
        bot.send_message(message.chat.id, 'Вам надо зарегестрироваться, введите /register')




# редактирование игр
@bot.message_handler(commands=['edit_game'])
def main(message):
    user_id = message.from_user.id
    if user_id == 577593785:
        bot.send_message(message.chat.id, 'Введите номер игры которую хотите редактировать. (просмотреть номер игры вы'
                                          'можете в /games)')
        cursor.execute(f'''SELECT * FROM public.games WHERE id = {message.text}''')
        ed_game = cursor.fetchall()
        for row in ed_game:
            bot.send_message(message.chat.id, f"{row}")
            bot.send_message(message.chat.id, 'Das ist gut')

    else:
        bot.send_message(message.chat.id, 'Ошибка. Недостаточно прав доступа.')



if __name__ == '__main__':
    # Создание таблицы при старте
    create_table()

    # Запуск бота
    bot.polling(none_stop=True)
