import telebot
from telebot import types
import psycopg2
import os
from datetime import datetime

bot = telebot.TeleBot('8125147433:AAG5UmSLaSUl23DicIcMeEd7sq2wNT-Zp_E')
games = [
    ['Вечные хиты', 'Туц-Туц Квиз', 'Тематика', '09-11-2024', '19:00',
     'Nebo', "ул. А.Темура 53", 50000, True, './images/mzgb.jpg']
]

IMAGE_DIR = './images/'

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
                                      'Добро пожаловать в Мозгобойню — увлекательный квиз, где можно проверить свои знания и'
                                      'посоревноваться с друзьями! 🧠🎉 \n \n'
                                      'Каждый раунд включает вопросы по разным темам: от истории и науки до поп-культуры и '
                                      'спорта. 📚🎬⚽ Покажите, на что вы способны, и станьте чемпионом Мозгобойни! 🏆 \n \n'
                                      'Удачи! 🍀', parse_mode='html')
    bot.send_message(message.chat.id, 'Для того чтобы принять участие в игре, вам нужно зарегестрировать свою команду.')
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

    # Используем параметризованный запрос для безопасности
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
def main(message):
    user_id = message.from_user.id
    if user_id == 577593785:
        def start_add_game(message):
            # Отправляем сообщение с просьбой ввести название игры
            bot.send_message(message.chat.id, "Введите название игры (например: Вечные хиты):")
            bot.register_next_step_handler(message, process_name_game)


        # Обработка названия игры
        def process_name_game(message):
            name_game = message.text
            bot.send_message(message.chat.id, "Введите тематику игры (например: Туц-Туц Квиз):")
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
                bot.register_next_step_handler(message, process_is_now, name_game, name_theme, game_date, time, place, address,
                                               price)
            except ValueError:
                bot.send_message(message.chat.id, "Пожалуйста, введите корректную цену (целое число).")


        # Обработка статуса игры (играем ли сейчас)
        def process_is_now(message, name_game, name_theme, game_date, time, place, address, price):
            is_now = message.text.lower() == 'true'
            bot.send_message(message.chat.id, "Отправьте фотографию игры:")
            bot.register_next_step_handler(message, process_picture, name_game, name_theme, game_date, time, place, address,
                                           price, is_now)


        # Обработка картинки игры
        def process_picture(message, name_game, name_theme, game_date, time, place, address, price, is_now):
            if message.content_type == 'photo':
                # Скачивание фото
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                # Создание директории, если она не существует
                if not os.path.exists(IMAGE_DIR):
                    os.makedirs(IMAGE_DIR)

                # Генерация уникального имени файла
                file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                file_path = os.path.join(IMAGE_DIR, file_name)

                # Сохранение фото
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Добавление игры в базу данных
                adder(name_game, name_theme, game_date, time, place, address, price, is_now, file_path)

                bot.send_message(message.chat.id, f"Игра '{name_game}' успешно добавлена!")
            else:
                bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию.")
        connection.commit()
    else:
        bot.send_message(message.chat.id, "Отказано. Недостаточно прав доступа.")

if __name__ == '__main__':
    # Создание таблицы при старте
    create_table()

    # Запуск бота
    bot.polling(none_stop=True)