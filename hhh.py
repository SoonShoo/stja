import pygsheets
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Вставьте ваш токен здесь
TOKEN = '7836270948:AAF0tLyHklUxbBCGIQ9WKyw15mSZc8VSg_Q'
SHEET_NAME = 'stja'  # Замените на название вашей Google Таблицы
row_n = 'A1'

# Определяем состояния для диалога регистрации
NAME, CONTACT = range(2)

# Настройка Google Sheets


def setup_gspread():
    try:
        gc = pygsheets.authorize(service_file='credentials.json')
        sheet = gc.open(SHEET_NAME).sheet1
        print("Таблица успешно открыта")
        return sheet
    except Exception as e:
        print(f"Ошибка при открытии таблицы: {e}")

def add_to_sheet(name, contact):
    try:
        print("Данные успешно записаны в таблицу")
        sheet = setup_gspread()
        sheet.append_table([name, contact], start=row_n, end=None, dimension='ROWS', overwrite=False)  # Добавление новой строки с данными
        print("Данные успешно записаны в таблицу")
    except Exception as e:
        print(f"Ошибка записи в таблицу: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добро пожаловать! Я ваш AI-ассистент для интенсива 'Практическое применение ИИ'.\n"
        "Вот доступные команды:\n"
        "/info - Узнать больше о интенсиве\n"
        "/schedule - Расписание мероприятий\n"
        "/faq - Часто задаваемые вопросы\n"
        "/contact - Связаться с организаторами\n"
        "/register - Зарегистрироваться на интенсив\n"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Интенсив 'Практическое применение ИИ' — это программа, где вы научитесь основам "
        "искусственного интеллекта и его применению в различных областях. "
        "Программа включает практические задания и проекты."
    )

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Расписание мероприятий:\n"
        "1. Введение в ИИ - 10:00, 1 день\n"
        "2. Машинное обучение - 12:00, 1 день\n"
        "3. Практическое задание - 14:00, 1 день\n"
        "4. Проекты и защита - 10:00, 2 день\n"
    )

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Часто задаваемые вопросы:\n"
        "Q: Как зарегистрироваться?\n"
        "A: Используйте команду /register для регистрации на интенсив.\n"
        "Q: Какова стоимость участия?\n"
        "A: Стоимость участия составляет 5000 рублей."
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     await update.message.reply_text(
        "Вы можете связаться с нами через:\n"
        "Email: mna@example.com\n"
            "Телефон: +7 (123) 456-78-90"
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Начало регистрации")
    await update.message.reply_text("Пожалуйста, введите ваше имя:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    print(f"Получено имя: {update.message.text}")
    await update.message.reply_text("Спасибо, {}! Теперь укажите ваш контактный номер:".format(update.message.text))
    print("Данные успешно записаны в таблицу")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact'] = update.message.text
    print(f"Получен контакт: {update.message.text}")

    # Проверка на корректность номера
    if not update.message.text.isdigit() or len(update.message.text) < 7:
        await update.message.reply_text("Пожалуйста, введите номер телефона корректно. Попробуйте снова.")
         # Оставляем пользователя в том же состоянии
        return CONTACT


    print("Данные успешно записаны в таблицу")
    add_to_sheet(context.user_data['name'], context.user_data['contact'])  # Запись данных в таблицу
    await update.message.reply_text(
    "Вы успешно зарегистрированы на интенсив!\n"
    "Имя: {}\nКонтакт: {}\n".format(context.user_data['name'], context.user_data['contact'])
)
    # Завершение разговора
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Определение обработчиков для регистрации
    register_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(register_conv_handler)

    app.run_polling()
