import logging
import threading
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import Database
from food_parser import FoodParser
from config import BOT_TOKEN, ADMIN_IDS
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
db.init_database()
parser = FoodParser()
db_updating = False


def check_and_import_data():
    """Проверяет базу и импортирует данные при необходимости"""
    print("=" * 50)
    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 50)

    try:
        food_count = db.get_food_count()
        print(f"📊 Текущее количество продуктов: {food_count}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        food_count = 0

    if food_count < 1000:
        print("⚠️ База пуста или содержит мало продуктов! Начинаю импорт...")

        if not os.path.exists('data.json'):
            print("❌ Файл data.json не найден!")
            return False

        success = db.import_from_json()
        if success:
            print(f"✅ Импорт завершен! В базе {db.get_food_count()} продуктов")
            return True
        else:
            print("❌ Ошибка импорта")
            return False

    print(f"✅ База данных содержит {food_count} продуктов")
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id)
        await update.message.reply_text(
            "👋 Привет! Я бот для подсчета КБЖУ.\n\n"
            "📝 Просто напиши мне, что ты съел(а), например:\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 2 ложки сахара\n"
            "• тарелка борща со сметаной\n"
            "• шашлык 200г\n\n"
            "Для настройки дневной нормы используй /settings\n"
            "Для статистики за день используй /stats"
        )
    else:
        await update.message.reply_text("👋 Что сегодня ел(а)?")


def send_telegram_message(chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30
        )
    except Exception as e:
        print(f"Ошибка: {e}")


async def admin_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет прав.")
        return

    global db_updating
    if db_updating:
        await update.message.reply_text("🔄 Импорт уже выполняется...")
        return

    await update.message.reply_text("🚀 Начинаю импорт... ⏱️ 1-3 минуты.")

    def run_import():
        global db_updating
        db_updating = True
        try:
            success = db.import_from_json()
            if success:
                send_telegram_message(user_id, f"✅ Импорт завершен! Продуктов: {db.get_food_count()}")
            else:
                send_telegram_message(user_id, "❌ Ошибка импорта")
        except Exception as e:
            send_telegram_message(user_id, f"❌ Ошибка: {e}")
        finally:
            db_updating = False

    threading.Thread(target=run_import).start()


async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет прав.")
        return

    food_count = db.get_food_count()
    await update.message.reply_text(
        f"📊 Статус:\n"
        f"🍎 Всего продуктов: {food_count}\n"
        f"🔄 Обновление: {'выполняется' if db_updating else 'не выполняется'}"
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚖️ Вес", callback_data='set_weight')],
        [InlineKeyboardButton("📏 Рост", callback_data='set_height')],
        [InlineKeyboardButton("🎂 Возраст", callback_data='set_age')],
        [InlineKeyboardButton("⚧ Пол", callback_data='set_gender')],
        [InlineKeyboardButton("📊 Моя норма", callback_data='show_norm')],
    ]
    await update.message.reply_text("⚙️ Настройки:", reply_markup=InlineKeyboardMarkup(keyboard))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    summary = db.get_daily_summary(user_id)

    if not any(summary['meals'].values()):
        await update.message.reply_text("📊 За сегодня ничего не записано.")
        return

    user = db.get_user(user_id)
    response = f"📊 Статистика за {summary['date']}:\n\n"

    meal_names = {'breakfast': '🍳 Завтрак', 'lunch': '🍲 Обед', 'dinner': '🍽 Ужин', 'snack': '🍎 Перекусы'}

    for meal_type, meal_name in meal_names.items():
        if summary['meals'][meal_type]:
            response += f"{meal_name}:\n"
            for item in summary['meals'][meal_type]:
                response += f"  • {item['name']} ({item['weight']}г): {item['calories']:.0f} ккал\n"
            response += "\n"

    total = summary['total']
    response += f"📈 ИТОГО:\n🔥 Калории: {total['calories']:.0f} ккал"

    if user and user.daily_calories:
        percent = (total['calories'] / user.daily_calories) * 100
        response += f" ({percent:.1f}% от нормы)\n"
    else:
        response += "\n"

    response += f"💪 Белки: {total['proteins']:.1f}г\n🧈 Жиры: {total['fats']:.1f}г\n🍚 Углеводы: {total['carbs']:.1f}г"

    await update.message.reply_text(response)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'set_weight':
        await query.edit_message_text("⚖️ Введите вес в кг:")
        context.user_data['awaiting'] = 'weight'
    elif query.data == 'set_height':
        await query.edit_message_text("📏 Введите рост в см:")
        context.user_data['awaiting'] = 'height'
    elif query.data == 'set_age':
        await query.edit_message_text("🎂 Введите возраст:")
        context.user_data['awaiting'] = 'age'
    elif query.data == 'set_gender':
        keyboard = [[InlineKeyboardButton("👨 Мужской", callback_data='gender_male')],
                    [InlineKeyboardButton("👩 Женский", callback_data='gender_female')]]
        await query.edit_message_text("⚧ Выберите пол:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'gender_male':
        db.update_user_params(user_id, gender='male')
        await query.edit_message_text("✅ Пол: Мужской")
    elif query.data == 'gender_female':
        db.update_user_params(user_id, gender='female')
        await query.edit_message_text("✅ Пол: Женский")
    elif query.data == 'show_norm':
        user = db.get_user(user_id)
        if user and user.daily_calories:
            await query.edit_message_text(
                f"📊 Ваша норма: {user.daily_calories:.0f} ккал\n\n"
                f"⚖️ Вес: {user.weight} кг\n📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age}\n⚧ Пол: {'Мужской' if user.gender == 'male' else 'Женский'}"
            )
        else:
            await query.edit_message_text("❌ Норма не рассчитана. Заполните параметры.")
    elif query.data.startswith('meal_'):
        meal_type = query.data.replace('meal_', '')
        meal_names = {'breakfast': 'завтрак', 'lunch': 'обед', 'dinner': 'ужин', 'snack': 'перекус'}
        context.user_data['meal_type'] = meal_type
        await query.edit_message_text(f"🍽 Что съели на {meal_names[meal_type]}?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if 'awaiting' in context.user_data:
        await handle_parameter_input(update, context)
        return

    food_items = parser.parse_message(text)

    if not food_items:
        await update.message.reply_text(
            "😕 Не удалось распознать. Попробуйте:\n"
            "• 100г творог 9%\n• бутерброд с колбасой\n• кофе 2 ложки сахара"
        )
        return

    meal_type = context.user_data.get('meal_type', 'breakfast')
    total = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
    meal_items = []
    not_found = []

    for item in food_items:
        result = db.add_meal(user_id, item['name'], item['weight'], meal_type)
        if result:
            meal_items.append(result)
            total['calories'] += result['calories']
            total['proteins'] += result['proteins']
            total['fats'] += result['fats']
            total['carbs'] += result['carbs']
        else:
            not_found.append(item['name'])

    if not meal_items:
        await update.message.reply_text("😕 Не удалось найти продукты в базе.")
        return

    user = db.get_user(user_id)
    meal_names = {'breakfast': '🍳 Завтрак', 'lunch': '🍲 Обед', 'dinner': '🍽 Ужин', 'snack': '🍎 Перекус'}

    response = f"{meal_names[meal_type]}:\n\n"
    for item in meal_items:
        response += f"• {item['name']} ({item['weight']}г): {item['calories']} ккал, Б:{item['proteins']}г, Ж:{item['fats']}г, У:{item['carbs']}г\n"

    if not_found:
        response += f"\n⚠️ Не найдены: {', '.join(not_found)}\n"

    response += f"\n📊 ИТОГО:\n🔹 Калории: {total['calories']:.1f} ккал"
    if user and user.daily_calories:
        percent = (total['calories'] / user.daily_calories) * 100
        response += f" ({percent:.1f}% от нормы)\n"
    else:
        response += "\n"
    response += f"🔸 Белки: {total['proteins']:.1f}г\n🔸 Жиры: {total['fats']:.1f}г\n🔸 Углеводы: {total['carbs']:.1f}г"

    keyboard = [
        [InlineKeyboardButton("🍳 Завтрак", callback_data='meal_breakfast'),
         InlineKeyboardButton("🍲 Обед", callback_data='meal_lunch')],
        [InlineKeyboardButton("🍽 Ужин", callback_data='meal_dinner'),
         InlineKeyboardButton("🍎 Перекус", callback_data='meal_snack')],
    ]
    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_parameter_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    param_type = context.user_data.get('awaiting')

    try:
        if param_type == 'weight':
            weight = float(text.replace(',', '.'))
            if 20 <= weight <= 300:
                db.update_user_params(user_id, weight=weight)
                await update.message.reply_text(f"✅ Вес: {weight} кг")
            else:
                await update.message.reply_text("❌ Введите вес от 20 до 300 кг")
                return
        elif param_type == 'height':
            height = float(text.replace(',', '.'))
            if 100 <= height <= 250:
                db.update_user_params(user_id, height=height)
                await update.message.reply_text(f"✅ Рост: {height} см")
            else:
                await update.message.reply_text("❌ Введите рост от 100 до 250 см")
                return
        elif param_type == 'age':
            age = int(text)
            if 10 <= age <= 120:
                db.update_user_params(user_id, age=age)
                await update.message.reply_text(f"✅ Возраст: {age}")
            else:
                await update.message.reply_text("❌ Введите возраст от 10 до 120 лет")
                return

        del context.user_data['awaiting']
        user = db.get_user(user_id)
        if user and user.daily_calories:
            await update.message.reply_text(f"📊 Ваша дневная норма: {user.daily_calories:.0f} ккал")

    except ValueError:
        await update.message.reply_text("❌ Введите число")


def main():
    if not check_and_import_data():
        print("⚠️ Бот запускается с пустой базой!")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("admin_import", admin_import))
    application.add_handler(CommandHandler("admin_status", admin_status))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()