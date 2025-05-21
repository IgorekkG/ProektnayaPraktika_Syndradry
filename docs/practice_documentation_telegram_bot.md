# Руководство по разработке Telegram-бота-энциклопедии для проекта-игры Synthadry
## Введение
В рамках проекта **Synthadry** была поставлена задача создать **Telegram-бота**, который поможет игрокам ориентироваться во вселенной игры. Основной задачей стало предоставление информации в удобной форме, с визуальными материалами и хорошей навигацией.
## Анализ предметной области
Перед началом разработки команда провела исследование, включающее:
+ Изучение Telegram Bot API
+ Анализ существующих решений
+ Сравнение Python-библиотек для Telegram:
  - telebot (pyTelegramBotAPI)
  - aiogram
  - python-telegram-bot (выбранный вариант)
**Причина выбора:** стабильность, поддержка асинхронности, удобство построения интерактивных меню.
## Проектирование технологии
1. Получение API-токена через **BotFather**
2. Настройка окружения:
  - Установка зависимостей: pip install python-telegram-bot
  - IDE: PyCharm
3. Создание структуры:
  - TGbot/
  - bot.py
  - images/ (подпапки bestiary/, locations/, notes/)
4. Организация данных:
  - Словари BESTIARY, LOCATIONS, STORY_NOTES
5. Проектирование интерфейса:
  - Главное меню
  - Кнопки навигации
  - Вывод изображений и описаний
## Пошаговое руководство
### Шаг 1. Создание бота
- Перейдите к **BotFather** в Telegram

![image](https://github.com/user-attachments/assets/b220e260-86b1-4b8d-99cb-2baee67fd499)
- Введите /newbot и следуйте инструкциям
- Получите TOKEN и сохраните его в bot.py

![image](https://github.com/user-attachments/assets/97a6813d-2eff-49d8-81c8-0d5efbeda271)

Ниже в сообщении показан токен вашего бота. Его нельзя разглашать.
### Шаг 2. Создание словарей с данными
В файле bot.py добавьте:
```python
BESTIARY = {
    "creature1": {
        "name": "Тодд",
        "description": "Он не идёт, а продавливает лес...",
        "image_path1": "images/bestiary/hunter1.jpg",
        "image_path2": "images/bestiary/hunter2.jpg"
    }
}
```
Создайте аналогичные словари LOCATIONS и STORY_NOTES по примеру.
### Шаг 3. Базовая реализация команды /start
```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐾 Бестиарий", callback_data='bestiary')],
        [InlineKeyboardButton("🗺 Локации", callback_data='locations')],
        [InlineKeyboardButton("📝 Сюжетные заметки", callback_data='notes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите категорию:', reply_markup=reply_markup)
```
### Шаг 4. Запуск бота
Добавьте в конце файла:
```python
from telegram.ext import CallbackQueryHandler

application = Application.builder().token("ВАШ_ТОКЕН").build()
application.add_handler(CommandHandler("start", start))
application.run_polling()
```
Запустите бота командой в терминале:
```bash
python main.py
```
Проверьте в Telegram, что команда /start работает.

![image](https://github.com/user-attachments/assets/a036bc8e-7c17-4dfe-83f0-285c17df6c20)

### Шаг 5. Обработка кнопок и показ существ
Добавьте обработку нажатий:
```python
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'bestiary':
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f'beast_{key}')]
                    for key, item in BESTIARY.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите существо:", reply_markup=reply_markup)
```
По анологии сделайти обработку остальных кнопок.
Не забудьте добавить в конце файла:
```python
application.add_handler(CallbackQueryHandler(button_handler))
```
### Шаг 6. Показ изображений и текста существа
В button_handler добавьте проверку на выбор существа:
```python
elif query.data.startswith('beast_'):
    key = query.data.replace('beast_', '')
    item = BESTIARY[key]
    caption = f"{item['name']}\n\n{item['description']}"
    await context.bot.send_photo(chat_id=query.message.chat_id,
                                 photo=open(item['image_path1'], 'rb'),
                                 caption=caption)
```
### Шаг 7. Тестирование
1. Убедитесь, что все изображения лежат в правильных папках.
2. Запустите main.py, откройте бота в Telegram, нажмите /start.
3. Проверьте функциональность кнопок и отображение информации.
4. Бот готов
## Заключение
Результатом стала удобная и расширяемая энциклопедия внутри Telegram, работающая с визуальным и текстовым контентом. Благодаря использованию библиотеки python-telegram-bot, асинхронной архитектуре и грамотному проектированию, бот получился не только функциональным, но и устойчивым.
Бот может быть расширен: добавлением новых разделов, подключением базы данных, генерацией контента на основе запросов пользователя и т.д.
