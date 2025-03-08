# *SpeakUpBot*: Telegram-бот «Обучалка английскому языку»

## Описание проекта
*SpeakUpBot* — это Telegram-бот для изучения английского языка, основанный на взаимодействии с базой данных. Пользователи могут изучать английские слова, отвечая на вопросы, добавлять или удалять слова из своего персонального словаря.

## Цель проекта
Целью проекта является разработка базы данных и Telegram-бота для эффективного изучения английского языка. Проект помогает пользователям пополнять свой словарный запас и тренировать перевод слов в интерактивной форме.

## Функционал бота
*1. Приветственное сообщение:*
- После запуска бот отправляет пользователю приветственное сообщение, объясняющее основные функции.

*2. Изучение слов:*
- Бот предлагает пользователю перевести слово, показывая 4 варианта ответа на английском языке в виде кнопок.
- При правильном ответе бот подтверждает выбор.
- При неправильном ответе предлагает попробовать снова, даётся 3 попытки.
  
*3. База данных слов:*
- Содержит общий набор слов (например, местоимения, цвета). Первоначально заполняется 10 словами, доступными всем пользователям.
- Пользователи могут добавлять новые слова в свой персональный словарь.
- Удаление слов доступно только из персонального словаря и не влияет на других пользователей.
  
*4. Добавление новых слов:*
- Пользователь может пополнить свой словарь, добавив слово и его перевод.
- Эти слова будут доступны только данному пользователю.
  
*5. Удаление слов:*
- Реализована функция удаления слов из персонального словаря.
  
## Технологии
- Язык программирования: Python
- База данных: PostgreSQL
- Telegram API: используется для взаимодействия с ботом.
  
## Документация
Основные команды бота:
1. /start или /cards — приветствие и описание функционала.
2. /ADD_WORD — добавление нового слова в словарь.
3. /DELETE_WORD — удаление слова из персонального словаря.
4. /NEXT — переход к следующему слову.

## Пример взаимодействия с ботом
1. После команды /start или /cards бот отправляет приветственное сообщение:
   
   *Приветствую!*
*Я SpeakUpBot! Начнём учить язык.*
*У тебя есть возможность использовать тренажёр,
как конструктор, и собирать свою собственную базу для обучения.*
*Для этого можете использовать следующие инструменты:*
*добавить слово ➕,*
*удалить слово 🔙*
*Приступим ⬇️*

2. Бот задаёт вопрос:

   *Выбери перевод слова: Любовь*

   Пользователь выбирает один из четырёх вариантов ответа.

3. Кнопка *Добавить слово ➕* позволяет добавить слово:
   
   *Введите слово, которое вы хотите добавить, на английском:*

   *Теперь введите перевод для слова 'Moon':*

4. Кнопка *Удалить слово 🔙* запускает процесс удаления слова:
   
   *Введите слово, которое хотите удалить из вашего словаря:*