import psycopg2
import configparser


# Настройки подключения к базе данных
config = configparser.ConfigParser()
config.read('settings.ini')
db_name = config['Tokens']['db_name_token']
db_user = config['Tokens']["db_user_token"]
db_password = config['Tokens']["db_password_token"]
db_host = config['Tokens']["db_host_token"]
db_port = config['Tokens']["db_port_token"]


def get_db_connection():
    """Создаёт и возвращает подключение к базе данных."""
    return psycopg2.connect(
        dbname=db_name, 
        user=db_user, 
        password=db_password, 
        host=db_host, 
        port=db_port
    )
