import re


def check_for_russian_letters(word):
    # Регулярное выражение для проверки наличия русских букв
    if re.search(r"[а-яА-Я]", word):
        return False
    return True
