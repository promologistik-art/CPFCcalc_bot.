import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import Database
from food_parser import FoodParser
from config import BOT_TOKEN, ADMIN_IDS
from datetime import datetime
import threading
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
db = Database()
db.init_database()
parser = FoodParser()

# Флаг для отслеживания обновления базы
db_updating = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id)
        await update.message.reply_text(
            "👋 Привет! Я бот для подсчета КБЖУ.\n\n"
            "📝 Просто напиши мне, что ты съел(а):\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 2 ложки сахара\n"
            "• тарелка борща со сметаной\n"
            "• шашлык 200г\n"
            "• 3 литра пива, 100 гр арахиса\n\n"
            "Для настройки дневной нормы используй /settings\n"
            "Для статистики за день используй /stats"
        )
    else:
        await update.message.reply_text("👋 Что сегодня ел(а)?")

async def admin_update_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для админа - обновление базы продуктов"""
    user_id = update.effective_user.id
    
    # Проверяем, является ли пользователь админом
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return
    
    global db_updating
    if db_updating:
        await update.message.reply_text("🔄 Обновление базы уже выполняется. Подождите...")
        return
    
    await update.message.reply_text("🚀 Начинаю обновление базы продуктов...\n⏱️ Это займет 10-20 минут.")
    
    # Запускаем обновление в отдельном потоке
    def run_update():
        global db_updating
        db_updating = True
        try:
            from update_foods import update_database
            result = update_database()
            # Отправляем результат в том же потоке
            context.bot.send_message(
                chat_id=user_id,
                text=result
            )
        except Exception as e:
            context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Ошибка при обновлении: {str(e)}"
            )
        finally:
            db_updating = False
    
    thread = threading.Thread(target=run_update)
    thread.start()

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для админа - статус базы"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return
    
    from database import Database
    db_local = Database()
    session = db_local.Session()
    
    from models import Food
    food_count = session.query(Food).count()
    
    session.close()
    
    await update.message.reply_text(
        f"📊 Статус базы данных:\n"
        f"🍎 Всего продуктов: {food_count}\n"
        f"🔄 Обновление: {'выполняется' if db_updating else 'не выполняется'}\n\n"
        f"Чтобы обновить базу, используй /admin_update_db"
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройка параметров пользователя"""
    keyboard = [
        [InlineKeyboardButton("⚖️ Вес", callback_data='set_weight')],
        [InlineKeyboardButton("📏 Рост", callback_data='set_height')],
        [InlineKeyboardButton("🎂 Возраст", callback_data='set_age')],
        [InlineKeyboardButton("⚧ Пол", callback_data='set_gender')],
        [InlineKeyboardButton("📊 Моя норма", callback_data='show_norm')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Настройки:", reply_markup=reply_markup)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика за сегодня"""
    user_id = update.effective_user.id
    summary = db.get_daily_summary(user_id)
    
    if not any(summary['meals'].values()):
        await update.message.reply_text("📊 За сегодня еще ничего не записано.")
        return
    
    user = db.get_user(user_id)
    
    response = f"📊 Статистика за {summary['date']}:\n\n"
    
    meal_names = {
        'breakfast': '🍳 Завтрак',
        'lunch': '🍲 Обед',
        'dinner': '🍽 Ужин',
        'snack': '🍎 Перекусы'
    }
    
    for meal_type, meal_name in meal_names.items():
        if summary['meals'][meal_type]:
            response += f"{meal_name}:\n"
            for item in summary['meals'][meal_type]:
                response += f"  • {item['name']} ({item['weight']}г): {item['calories']:.0f} ккал\n"
            response += "\n"
    
    total = summary['total']
    response += f"📈 ИТОГО:\n"
    response += f"🔥 Калории: {total['calories']:.0f} ккал"
    
    if user and user.daily_calories:
        percent = (total['calories'] / user.daily_calories) * 100
        response += f" ({percent:.1f}% от нормы)\n"
    else:
        response += "\n"
    
    response += f"💪 Белки: {total['proteins']:.1f}г\n"
    response += f"🧈 Жиры: {total['fats']:.1f}г\n"
    response += f"🍚 Углеводы: {total['carbs']:.1f}г\n"
    
    await update.message.reply_text(response)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'set_weight':
        await query.edit_message_text("⚖️ Введите ваш вес в кг:")
        context.user_data['awaiting'] = 'weight'
    elif query.data == 'set_height':
        await query.edit_message_text("📏 Введите ваш рост в см:")
        context.user_data['awaiting'] = 'height'
    elif query.data == 'set_age':
        await query.edit_message_text("🎂 Введите ваш возраст:")
        context.user_data['awaiting'] = 'age'
    elif query.data == 'set_gender':
        keyboard = [
            [InlineKeyboardButton("👨 Мужской", callback_data='gender_male')],
            [InlineKeyboardButton("👩 Женский", callback_data='gender_female')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚧ Выберите пол:", reply_markup=reply_markup)
    elif query.data == 'gender_male':
        db.update_user_params(user_id, gender='male')
        await query.edit_message_text("✅ Пол установлен: Мужской")
    elif query.data == 'gender_female':
        db.update_user_params(user_id, gender='female')
        await query.edit_message_text("✅ Пол установлен: Женский")
    elif query.data == 'show_norm':
        user = db.get_user(user_id)
        if user and user.daily_calories:
            await query.edit_message_text(
                f"📊 Ваша дневная норма:\n"
                f"🔥 Калории: {user.daily_calories:.0f} ккал\n\n"
                f"⚖️ Вес: {user.weight} кг\n"
                f"📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age}\n"
                f"⚧ Пол: {'Мужской' if user.gender == 'male' else 'Женский'}"
            )
        else:
            await query.edit_message_text("❌ Норма не рассчитана. Заполните параметры.")
    elif query.data.startswith('meal_'):
        meal_type = query.data.replace('meal_', '')
        meal_names = {
            'breakfast': 'завтрак',
            'lunch': 'обед',
            'dinner': 'ужин',
            'snack': 'перекус'
        }
        context.user_data['meal_type'] = meal_type
        await query.edit_message_text(f"🍽 Что вы съели на {meal_names[meal_type]}?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений от пользователя"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'awaiting' in context.user_data:
        await handle_parameter_input(update, context)
        return
    
    # Парсим сообщение
    food_items = parser.parse_message(text)
    
    if not food_items:
        await update.message.reply_text(
            "😕 Не удалось распознать продукты. Попробуйте:\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 2 ложки сахара\n"
            "• тарелка борща\n"
            "• шашлык 200г\n"
            "• 3 литра пива, 100 гр арахиса"
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
        await update.message.reply_text(
            "😕 Не удалось найти продукты в базе.\n"
            "Попробуйте написать точнее или подождите обновления базы."
        )
        return
    
    user = db.get_user(user_id)
    
    meal_names = {
        'breakfast': '🍳 Завтрак',
        'lunch': '🍲 Обед',
        'dinner': '🍽 Ужин',
        'snack': '🍎 Перекус'
    }
    
    response = f"{meal_names[meal_type]}:\n\n"
    
    for item in meal_items:
        response += f"• {item['name']} ({item['weight']}г):\n"
        response += f"  {item['calories']} ккал, Б:{item['proteins']}г, Ж:{item['fats']}г, У:{item['carbs']}г\n"
    
    if not_found:
        response += f"\n⚠️ Не найдены: {', '.join(not_found)}\n"
    
    response += f"\n📊 ИТОГО:\n"
    response += f"🔹 Калории: {total['calories']:.1f} ккал"
    
    if user and user.daily_calories:
        percent = (total['calories'] / user.daily_calories) * 100
        response += f" ({percent:.1f}% от нормы)\n"
    else:
        response += "\n"
    
    response += f"🔸 Белки: {total['proteins']:.1f}г\n"
    response += f"🔸 Жиры: {total['fats']:.1f}г\n"
    response += f"🔸 Углеводы: {total['carbs']:.1f}г\n"
    
    keyboard = [
        [
            InlineKeyboardButton("🍳 Завтрак", callback_data='meal_breakfast'),
            InlineKeyboardButton("🍲 Обед", callback_data='meal_lunch'),
        ],
        [
            InlineKeyboardButton("🍽 Ужин", callback_data='meal_dinner'),
            InlineKeyboardButton("🍎 Перекус", callback_data='meal_snack'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup)

async def handle_parameter_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода параметров пользователя"""
    user_id = update.effective_user.id
    text = update.message.text
    
    param_type = context.user_data.get('awaiting')
    
    try:
        if param_type == 'weight':
            weight = float(text.replace(',', '.'))
            if 20 <= weight <= 300:
                db.update_user_params(user_id, weight=weight)
                await update.message.reply_text(f"✅ Вес установлен: {weight} кг")
            else:
                await update.message.reply_text("❌ Введите реальный вес (20-300 кг)")
                return
        elif param_type == 'height':
            height = float(text.replace(',', '.'))
            if 100 <= height <= 250:
                db.update_user_params(user_id, height=height)
                await update.message.reply_text(f"✅ Рост установлен: {height} см")
            else:
                await update.message.reply_text("❌ Введите реальный рост (100-250 см)")
                return
        elif param_type == 'age':
            age = int(text)
            if 10 <= age <= 120:
                db.update_user_params(user_id, age=age)
                await update.message.reply_text(f"✅ Возраст установлен: {age}")
            else:
                await update.message.reply_text("❌ Введите реальный возраст (10-120 лет)")
                return
        
        del context.user_data['awaiting']
        
        user = db.get_user(user_id)
        if user and user.daily_calories:
            await update.message.reply_text(
                f"📊 Ваша дневная норма: {user.daily_calories:.0f} ккал"
            )
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды для всех
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("stats", stats))
    
    # Команды для админа
    application.add_handler(CommandHandler("admin_update_db", admin_update_db))
    application.add_handler(CommandHandler("admin_status", admin_status))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот запущен...")
    print("📝 Команды:")
    print("   /start - начать работу")
    print("   /settings - настройки")
    print("   /stats - статистика")
    print("   /admin_update_db - обновить базу (только админ)")
    print("   /admin_status - статус базы (только админ)")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()