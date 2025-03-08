from data_base_conn import get_db_connection


def create_db():
    # Создание словаря
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Таблица пользователей
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, 
                user_id BIGSERIAL UNIQUE NOT NULL,
                user_name VARCHAR(255) UNIQUE NOT NULL
            )
            """
            )

            # Общий словарь
            cur.execute(
                """ 
            CREATE TABLE IF NOT EXISTS words (
                id SERIAL PRIMARY KEY,
                target_word VARCHAR(255) UNIQUE NOT NULL,
                translate_word VARCHAR(255) NOT NULL
            )
            """
            )

            # Персональный словарь
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS user_words (
                id SERIAL PRIMARY KEY,
                user_id BIGSERIAL NOT NULL,
                target_word VARCHAR(255) UNIQUE NOT NULL,
                translate_word VARCHAR(255) NOT NULL
            )
            """
            )

            conn.commit()


def ensure_user_exists(user_id, user_name):
    # Добавление пользователя
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            INSERT INTO users (user_id, user_name)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET user_name = EXCLUDED.user_name
            """,
                (user_id, user_name),
            )

            conn.commit()


def filling_in_the_general_dictionary(common_words):
    # Заполнение общего словаря
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
            INSERT INTO words (target_word, translate_word)
            VALUES (%s, %s)
            ON CONFLICT (target_word) DO NOTHING
            """,
                common_words,
            )

            conn.commit()


def add_word_to_user(user_id, target_word, translate_word):
    # Заполнение персонального словаря
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            INSERT INTO user_words (user_id, target_word, translate_word)
            VALUES (%s, %s, %s)
            """,
                (
                    user_id,
                    target_word.strip().capitalize(),
                    translate_word.strip().capitalize(),
                ),
            )

            conn.commit()


def delete_user_word(user_id, target_word):
    # Удаление слова из персонального словаря
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            DELETE FROM user_words
            WHERE user_id = %s AND target_word = %s
            RETURNING target_word;
            """,
                (user_id, target_word),
            )
            result = cur.fetchone()
            conn.commit()
            return result


def get_random_words(cid, limit=4):
    # Получение 4 случайных слов из общего и случайного словарей
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT target_word, translate_word
            FROM (
                SELECT w.target_word, w.translate_word
                    FROM words w
                UNION
                SELECT uw.target_word, uw.translate_word
                    FROM user_words uw
                WHERE uw.user_id = %s
                    ) AS combined_words
            ORDER BY RANDOM()
            LIMIT %s;
            """,
                (cid, limit),
            )

            return cur.fetchall()


def check_word_existence(word):
    # Проверяет есть ли слово в общем словаре
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT 1 
            FROM words
            WHERE target_word = %s
            """,
                (word,),
            )
            return cur.fetchone() is not None


def check_existence_of_a_word_in_a_personal_dictionary(user_id, word):
    # Проверяет есть ли слово в персональном словаре
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT 1 
            FROM user_words
            WHERE target_word = %s AND user_id = %s
            """,
                (word, user_id),
            )
            return cur.fetchone() is not None


def number_of_words_studied_by_the_user(user_id):
    # Считывает количсетво изучаемых слов пользователем
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT COUNT(*)
            FROM user_words 
            WHERE user_id = %s
            """,
                (user_id,),
            )
            return cur.fetchone()[0]
