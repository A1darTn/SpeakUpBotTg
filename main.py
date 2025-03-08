import telebot
from random import shuffle
import configparser
from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from data_base_conn import get_db_connection
from data_base_hand import (
    create_db,
    ensure_user_exists,
    filling_in_the_general_dictionary,
    add_word_to_user,
    delete_user_word,
    get_random_words,
    check_word_existence,
    check_existence_of_a_word_in_a_personal_dictionary,
    number_of_words_studied_by_the_user,
)
from func import check_for_russian_letters


# Подключение к базе данных
get_db_connection()

# Создание таблиц
create_db()

state_storage = StateMemoryStorage()

config = configparser.ConfigParser()
config.read("settings.ini")
token_bot = config["Tokens"]["tg_bot_token"]
bot = telebot.TeleBot(token_bot, state_storage=state_storage)

ensure_user_exists(bot.get_me().id, bot.get_me().username)


class Command:
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово 🔙"
    NEXT = "Следующее слово ➡️"


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_word = State()
    adding_new_word = State()
    savind_new_word = State()
    deleting_word = State()


common_words = [
    ("Peace", "Мир"),
    ("Green", "Зелёный"),
    ("White", "Белый"),
    ("Hello", "Привет"),
    ("Car", "Машина"),
    ("Sky", "Небо"),
    ("Tree", "Дерево"),
    ("Book", "Книга"),
    ("Love", "Любовь"),
    ("Friend", "Друг"),
]


filling_in_the_general_dictionary(common_words)


@bot.message_handler(commands=["start", "cards"])
def send_welcome(message):
    cid = message.chat.id
    username = message.chat.username or "Unknown"
    ensure_user_exists(cid, username)

    bot.send_message(
        cid,
        f"Приветсвую, {message.from_user.first_name}! \nЯ {bot.get_me().first_name}! "
        f"Начнем изучать язык\nУ тебя есть возможность использовать тренажер, как конструктор, "
        f"и собирать свою собственную базу для обучения. Для этого можете использовать "
        f"следующие инструменты: \n"
        f"Добавить слово ➕\n"
        f"Удалить слово 🔙\n"
        f"Следующее слово ➡️\n"
        f"Приступим ⬇️",
        parse_mode="html",
    )

    send_main_menu(cid)


def create_cards(message):
    cid = message.chat.id

    words = get_random_words(message.from_user.id, limit=4)

    if not words or len(words) < 4:
        bot.send_message(
            cid, "Недостаточно слов!\nДобавьте слова с помощью 'Добавить слово ➕'."
        )
        return

    target_word, translate_word = words[0]
    other_words = [word[0] for word in words[1:]]

    options = [target_word] + other_words
    shuffle(options)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    btns = [types.KeyboardButton(option) for option in options]
    btns.append(types.KeyboardButton(Command.NEXT))
    btns.append(types.KeyboardButton(Command.ADD_WORD))
    btns.append(types.KeyboardButton(Command.DELETE_WORD))
    markup.add(*btns)

    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=cid) as data:
        data["target_word"] = target_word
        data["translate_word"] = translate_word

    bot.send_message(
        cid, f"Выбери перевод слова: \n{translate_word}", reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_word(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_start(message):
    cid = message.chat.id
    bot.set_state(
        user_id=message.from_user.id, chat_id=cid, state=MyStates.adding_new_word
    )
    bot.send_message(cid, "Введите на английском слово, которое хотите добавить:")


@bot.message_handler(state=MyStates.adding_new_word)
def add_word_translate(message):
    cid = message.chat.id
    word = message.text.strip().capitalize()

    if check_for_russian_letters(word=word) == False:
        bot.send_message(cid, f"Слово должно состоять исключительно из английских букв")
        return

    if check_word_existence(word):
        bot.send_message(
            cid,
            f'Слово "{word}" уже есть в общем словаре, пожалуйста, введите другое слово',
        )
        return
    elif check_existence_of_a_word_in_a_personal_dictionary(
        message.from_user.id, word=word
    ):
        bot.send_message(
            cid,
            f'Слово "{word}" уже есть в вашем персональном словаре, пожалуйста, введите другое слово',
        )
        return

    with bot.retrieve_data(message.from_user.id, cid) as data:
        data["target_word"] = word

    bot.set_state(message.from_user.id, chat_id=cid, state=MyStates.savind_new_word)
    bot.send_message(cid, f'Теперь введите перевод для слова "{word}":')


@bot.message_handler(state=MyStates.savind_new_word)
def save_new_word(message):
    cid = message.chat.id
    translate = message.text.strip().capitalize()

    if not translate:
        bot.send_message(
            cid, "Перевод не может быть пустым, пожалуйста, введите перевод"
        )
        return
    
    if check_for_russian_letters(translate):
        bot.send_message(cid, f'Перевод слово должен состоять исключительно из русских букв')
        return
    try:
        with bot.retrieve_data(message.from_user.id, cid) as data:
            target_word = data["target_word"].capitalize()

        if not target_word:
            bot.send_message(cid, "Ошибка! Попробуйте начать заново с /start.")
            bot.delete_state(user_id=message.from_user.id, chat_id=cid)
            return

        add_word_to_user(message.from_user.id, target_word, translate)
        count_words_user = number_of_words_studied_by_the_user(message.from_user.id)
        bot.send_message(
            cid,
            f"Слово '{target_word}' и его перевод '{translate}' успешно добавлены!"
            f"Количетсво изучаемых слов: {count_words_user}",
        )
        bot.delete_state(user_id=message.from_user.id, chat_id=cid)
    except Exception as e:
        bot.send_message(
            cid, f"Произошла ошибка при сохранении слова, попробуйте заново {e}"
        )
    finally:

        send_main_menu(cid)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word_start(message):
    cid = message.chat.id
    bot.set_state(
        user_id=message.from_user.id, chat_id=cid, state=MyStates.deleting_word
    )
    bot.send_message(cid, "Введите на английском слово, которое хотите удалить: ")


@bot.message_handler(state=MyStates.deleting_word)
def delete_word(message):
    cid = message.chat.id
    word_to_delete = message.text.strip().capitalize()

    word_to_delete_def = delete_user_word(message.from_user.id, word_to_delete)

    if word_to_delete_def:
        bot.send_message(
            cid, f'Слово "{word_to_delete_def[0]}" успешно удалено из вашего словаря'
        )
        send_main_menu(cid)
    else:
        bot.send_message(cid, f'Слово "{word_to_delete}" не найдено в вашем словаре')
        send_main_menu(cid)


def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btns = [
        types.KeyboardButton(Command.NEXT),
        types.KeyboardButton(Command.ADD_WORD),
        types.KeyboardButton(Command.DELETE_WORD),
    ]

    markup.add(*btns)
    bot.send_message(chat_id, "Выбери дальнейшее действие", reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_reply(message):
    cid = message.chat.id
    user_response = message.text

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data["target_word"]
        translate_word = data["translate_word"]
        attempts = data.get("attempts", 0)

        if not target_word or not translate_word:
            bot.send_message(cid, "Ошибка! Попробуйте начать заново с /start.")
            return

        if user_response.strip().capitalize() == target_word.strip().capitalize():
            try:
                bot.send_message(
                    cid, f"✅ Правильно!\n{target_word} => {translate_word}!"
                )
                send_main_menu(cid)
            except Exception as e:
                bot.send_message(
                    cid, "Произошла ошибка при сохранении слова, попробуйте заново"
                )
            finally:
                data.clear()
                return

        attempts += 1
        data["attempts"] = attempts
        if attempts < 3:
            bot.send_message(
                cid,
                f"❌ Неправильно! Попробуй снова.\nПеревод слова: {translate_word}\n"
                f"Попытка {attempts} из 3",
            )
        else:
            bot.send_message(
                cid,
                f"К сожалению вы истратили все попытки. \n"
                f"Правильный перевод: {target_word}",
            )
            data.clear()
            return


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
