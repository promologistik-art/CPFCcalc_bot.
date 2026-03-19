import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import Database
from food_parser import FoodParser
from config import BOT_TOKEN
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
db = Database()
db.init_database()  # Заполняем базу продуктов
parser = FoodParser()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли пользователь в БД
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id)
        await update.message.reply_text(
            "👋 Привет! Я бот для подсчета КБЖУ.\n\n"
            "Я помогу тебе отслеживать калории и нутриенты.\n\n"
            "📝 Просто напиши мне, что ты съел(а), например:\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 3 ложки сахара\n"
            "• тарелка борща со сметаной\n"
            "• шашлык из свинины 200г\n"
            "• салат оливье\n\n"
            "Для настройки дневной нормы используй /settings\n"
            "Для статистики за день используй /stats"
        )
    else:
        await update.message.reply_text(
            "👋 С возвращением! Что сегодня ел(а)?"
        )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройка параметров пользователя"""
    keyboard = [
        [InlineKeyboardButton("⚖️ Вес", callback_data='set_weight')],
        [InlineKeyboardButton("📏 Рост", callback_data='set_height')],
        [InlineKeyboardButton("🎂 Возраст", callback_data='set_age')],
        [InlineKeyboardButton("⚧ Пол", callback_data='set_gender')],
        [InlineKeyboardButton("🏃 Активность", callback_data='set_activity')],
        [InlineKeyboardButton("📊 Моя норма", callback_data='show_norm')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚙️ Настройки дневной нормы калорий:",
        reply_markup=reply_markup
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика за сегодня"""
    user_id = update.effective_user.id
    
    # Получаем сводку за сегодня
    summary = db.get_daily_summary(user_id)
    
    if not summary['meals']['breakfast'] and not summary['meals']['lunch'] and \
       not summary['meals']['dinner'] and not summary['meals']['snack']:
        await update.message.reply_text("📊 За сегодня еще ничего не записано.")
        return
    
    # Получаем пользователя для расчета процентов
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
                response += f"  • {item['name']} ({item['weight']}г): "
                response += f"{item['calories']:.0f} ккал\n"
            response += "\n"
    
    total = summary['total']
    response += f"📈 ИТОГО ЗА ДЕНЬ:\n"
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
        await query.edit_message_text("⚖️ Введите ваш вес в кг (например: 75):")
        context.user_data['awaiting'] = 'weight'
    elif query.data == 'set_height':
        await query.edit_message_text("📏 Введите ваш рост в см (например: 175):")
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
    elif query.data == 'set_activity':
        keyboard = [
            [InlineKeyboardButton("🛌 Минимальная (сидячая работа)", callback_data='activity_1.2')],
            [InlineKeyboardButton("🚶 Низкая (легкие тренировки 1-3 раза)", callback_data='activity_1.375')],
            [InlineKeyboardButton("🏃 Средняя (тренировки 3-5 раз)", callback_data='activity_1.55')],
            [InlineKeyboardButton("🏋️ Высокая (тренировки 6-7 раз)", callback_data='activity_1.725')],
            [InlineKeyboardButton("⚡ Очень высокая (спортсмены)", callback_data='activity_1.9')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏃 Уровень активности:", reply_markup=reply_markup)
    elif query.data.startswith('activity_'):
        activity = float(query.data.replace('activity_', ''))
        db.update_user_params(user_id, activity_level=activity)
        await query.edit_message_text(f"✅ Уровень активности установлен!")
    elif query.data == 'gender_male':
        db.update_user_params(user_id, gender='male')
        await query.edit_message_text("✅ Пол установлен: Мужской")
    elif query.data == 'gender_female':
        db.update_user_params(user_id, gender='female')
        await query.edit_message_text("✅ Пол установлен: Женский")
    elif query.data == 'show_norm':
        user = db.get_user(user_id)
        if user and user.daily_calories:
            activity_names = {
                1.2: "Минимальная",
                1.375: "Низкая",
                1.55: "Средняя",
                1.725: "Высокая",
                1.9: "Очень высокая"
            }
            activity_name = activity_names.get(user.activity_level, "Неизвестно")
            
            await query.edit_message_text(
                f"📊 Ваша дневная норма:\n\n"
                f"🔥 Калории: {user.daily_calories:.0f} ккал\n\n"
                f"📌 Ваши параметры:\n"
                f"⚖️ Вес: {user.weight} кг\n"
                f"📏 Рост: {user.height} см\n"
                f"🎂 Возраст: {user.age}\n"
                f"⚧ Пол: {'Мужской' if user.gender == 'male' else 'Женский'}\n"
                f"🏃 Активность: {activity_name}\n\n"
                f"Для изменения параметров используйте /settings"
            )
        else:
            await query.edit_message_text(
                "❌ Норма еще не рассчитана. Заполните все параметры в /settings"
            )
    elif query.data.startswith('meal_'):
        meal_type = query.data.replace('meal_', '')
        meal_names = {
            'breakfast': 'завтрак',
            'lunch': 'обед',
            'dinner': 'ужин',
            'snack': 'перекус'
        }
        context.user_data['meal_type'] = meal_type
        await query.edit_message_text(f"🍽 Отлично! Что вы съели на {meal_names[meal_type]}?")
    elif query.data == 'show_daily_stats':
        # Показываем статистику за сегодня
        summary = db.get_daily_summary(user_id)
        user = db.get_user(user_id)
        
        if not summary['meals']['breakfast'] and not summary['meals']['lunch'] and \
           not summary['meals']['dinner'] and not summary['meals']['snack']:
            await query.edit_message_text("📊 За сегодня еще ничего не записано.")
            return
        
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
                    response += f"  • {item['name']} ({item['weight']}г): "
                    response += f"{item['calories']:.0f} ккал\n"
                response += "\n"
        
        total = summary['total']
        response += f"📈 ИТОГО ЗА ДЕНЬ:\n"
        response += f"🔥 Калории: {total['calories']:.0f} ккал"
        
        if user and user.daily_calories:
            percent = (total['calories'] / user.daily_calories) * 100
            response += f" ({percent:.1f}% от нормы)\n"
        else:
            response += "\n"
        
        response += f"💪 Белки: {total['proteins']:.1f}г\n"
        response += f"🧈 Жиры: {total['fats']:.1f}г\n"
        response += f"🍚 Углеводы: {total['carbs']:.1f}г\n"
        
        await query.edit_message_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений от пользователя"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверяем, ожидаем ли мы ввод параметров
    if 'awaiting' in context.user_data:
        await handle_parameter_input(update, context)
        return
    
    # Парсим сообщение с продуктами
    food_items = parser.parse_message(text)
    
    if not food_items:
        await update.message.reply_text(
            "😕 Не удалось распознать продукты. Попробуй написать по-другому, например:\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 3 ложки сахара\n"
            "• тарелка борща\n"
            "• шашлык 200г"
        )
        return
    
    # Определяем тип приема пищи
    meal_type = context.user_data.get('meal_type', 'breakfast')
    
    # Обрабатываем каждый продукт
    total = {
        'calories': 0,
        'proteins': 0,
        'fats': 0,
        'carbs': 0
    }
    
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
            "😕 Не удалось найти продукты в базе. Попробуй написать точнее.\n"
            "Например: 'творог 5%' вместо просто 'творог'"
        )
        return
    
    # Получаем пользователя для расчета процентов
    user = db.get_user(user_id)
    
    # Формируем ответ
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
    
    # Кнопки для выбора следующего действия
    keyboard = [
        [
            InlineKeyboardButton("🍳 Завтрак", callback_data='meal_breakfast'),
            InlineKeyboardButton("🍲 Обед", callback_data='meal_lunch'),
        ],
        [
            InlineKeyboardButton("🍽 Ужин", callback_data='meal_dinner'),
            InlineKeyboardButton("🍎 Перекус", callback_data='meal_snack'),
        ],
        [InlineKeyboardButton("📊 Статистика за день", callback_data='show_daily_stats')],
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
            if weight < 20 or weight > 300:
                await update.message.reply_text("❌ Пожалуйста, введите реальный вес (20-300 кг)")
                return
            db.update_user_params(user_id, weight=weight)
            await update.message.reply_text(f"✅ Вес установлен: {weight} кг")
            
        elif param_type == 'height':
            height = float(text.replace(',', '.'))
            if height < 100 or height > 250:
                await update.message.reply_text("❌ Пожалуйста, введите реальный рост (100-250 см)")
                return
            db.update_user_params(user_id, height=height)
            await update.message.reply_text(f"✅ Рост установлен: {height} см")
            
        elif param_type == 'age':
            age = int(text)
            if age < 10 or age > 120:
                await update.message.reply_text("❌ Пожалуйста, введите реальный возраст (10-120 лет)")
                return
            db.update_user_params(user_id, age=age)
            await update.message.reply_text(f"✅ Возраст установлен: {age}")
        
        # Очищаем состояние
        del context.user_data['awaiting']
        
        # Показываем текущую норму
        user = db.get_user(user_id)
        if user and user.daily_calories:
            await update.message.reply_text(
                f"📊 Ваша дневная норма калорий: {user.daily_calories:.0f} ккал\n"
                f"Для просмотра всех параметров используйте /settings"
            )
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("🚀 Бот запущен...")
    print("📝 Используйте команды: /start, /settings, /stats")
    application.run_polling(allowed_updates=Update.ALL_TYPES)  # ← Здесь была ошибка - не хватало скобки

if __name__ == '__main__':
    main()