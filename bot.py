import logging
import threading
import asyncio
import time
import json
import sqlite3
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import Database
from food_parser import FoodParser
from config import BOT_TOKEN, ADMIN_IDS
from datetime import datetime

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

async def admin_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для админа - импорт продуктов из data.json"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return
    
    global db_updating
    if db_updating:
        await update.message.reply_text("🔄 Обновление/импорт уже выполняется. Подождите...")
        return
    
    await update.message.reply_text("🚀 Начинаю импорт продуктов из data.json...\n⏱️ Это займет 1-3 минуты.")
    
    def run_import():
        global db_updating
        db_updating = True
        try:
            # Отправляем сообщение о начале
            context.bot.send_message(chat_id=user_id, text="📥 Загрузка файла data.json...")
            
            # Проверяем существование файла
            if not os.path.exists('data.json'):
                context.bot.send_message(chat_id=user_id, text="❌ Файл data.json не найден!")
                return
            
            # Загружаем JSON
            with open('data.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            context.bot.send_message(chat_id=user_id, text=f"📦 Загружено продуктов: {len(products)}")
            
            # Подключаемся к базе
            db_path = 'kbju_bot.db'
            if not os.path.exists(db_path):
                context.bot.send_message(chat_id=user_id, text="❌ База данных не найдена!")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Получаем категории
            cursor.execute("SELECT id, name FROM food_categories")
            categories = {name: id for id, name in cursor.fetchall()}
            
            # Статистика
            added = 0
            skipped = 0
            total = len(products)
            
            context.bot.send_message(chat_id=user_id, text="💾 Начинаю импорт...\n0%")
            
            for idx, (name, data) in enumerate(products.items()):
                # Определяем категорию по названию
                category = detect_category_import(name)
                category_id = categories.get(category, 1)
                
                # Проверяем, есть ли уже такой продукт
                cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (name,))
                if cursor.fetchone():
                    skipped += 1
                    continue
                
                # Генерируем безопасное имя
                safe_name = name.lower().replace(' ', '_').replace('-', '_')
                safe_name = re.sub(r'[^a-zа-я0-9_]', '', safe_name)
                if not safe_name:
                    safe_name = f"product_{hash(name)}"
                
                # Добавляем продукт
                cursor.execute("""
                    INSERT INTO foods 
                    (name, name_ru, calories, proteins, fats, carbs, category_id, default_portion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    safe_name[:200],
                    name[:200],
                    data.get('calories', 0),
                    data.get('protein', 0),
                    data.get('fat', 0),
                    data.get('carbohydrates', 0),
                    category_id,
                    guess_portion_import(name)
                ))
                added += 1
                
                # Отправляем прогресс каждые 500 продуктов
                if added % 500 == 0:
                    percent = int(added / total * 100)
                    context.bot.send_message(
                        chat_id=user_id,
                        text=f"📊 Прогресс: {percent}% (добавлено {added} продуктов)"
                    )
                    conn.commit()
            
            conn.commit()
            conn.close()
            
            context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Импорт завершен!\n"
                     f"   Добавлено: {added} продуктов\n"
                     f"   Пропущено (уже есть): {skipped} продуктов"
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Ошибка при импорте: {str(e)}"
            )
        finally:
            db_updating = False
    
    thread = threading.Thread(target=run_import)
    thread.start()

def detect_category_import(product_name):
    """Определяет категорию по названию продукта"""
    name_lower = product_name.lower()
    
    categories = {
        'dairy': ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана', 'ряженка', 'сливки', 'активиа', 'актимель'],
        'meat': ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса', 'сосиски', 'ветчина', 'бекон', 'сало', 'мясо'],
        'poultry': ['курица', 'индейка', 'утка', 'гусь', 'цыпленок'],
        'fish': ['рыба', 'лосось', 'семга', 'форель', 'скумбрия', 'сельдь', 'треска', 'минтай', 'хек', 'креветка', 'кальмар'],
        'eggs': ['яйцо', 'яйца', 'омлет'],
        'vegetables': ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'огурец', 'помидор', 'перец', 'кабачок'],
        'fruits': ['яблоко', 'банан', 'апельсин', 'мандарин', 'груша', 'виноград', 'клубника', 'малина', 'авокадо'],
        'grains': ['гречка', 'рис', 'овсянка', 'пшено', 'перловка', 'манка', 'макароны', 'паста'],
        'bakery': ['хлеб', 'батон', 'булка', 'лаваш', 'сухарь'],
        'fats': ['масло', 'маргарин', 'майонез'],
        'nuts': ['орех', 'арахис', 'миндаль', 'фундук', 'кешью'],
        'drinks': ['кофе', 'чай', 'сок', 'компот', 'квас', 'лимонад', 'пиво', 'вино', 'водка', '7up'],
        'sweets': ['шоколад', 'конфета', 'печенье', 'вафли', 'халва', 'зефир', 'мармелад', 'мед', 'сахар'],
        'soups': ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха'],
        'salads': ['салат', 'оливье', 'винегрет', 'цезарь'],
    }
    
    for cat, keywords in categories.items():
        for keyword in keywords:
            if keyword in name_lower:
                return cat
    return 'other'

def guess_portion_import(name):
    """Определяет стандартную порцию"""
    name_lower = name.lower()
    
    portions = {
        'кофе': 200, 'чай': 200, 'сок': 200, 'компот': 200, 'кисель': 200,
        'квас': 250, 'лимонад': 250, 'пиво': 500, 'вино': 150, 'водка': 50,
        'молоко': 200, 'кефир': 200, 'йогурт': 150, 'творог': 150, 'сметана': 20,
        'хлеб': 30, 'батон': 30, 'яблоко': 150, 'банан': 150, 'апельсин': 150,
        'картофель': 200, 'гречка': 200, 'рис': 200, 'овсянка': 200,
        'макароны': 200, 'суп': 300, 'борщ': 300, 'салат': 200,
        'шашлык': 200, 'пельмени': 200, 'котлеты': 150, 'блины': 150,
        'шоколад': 20, 'печенье': 30, 'конфеты': 15, 'арахис': 30,
    }
    
    for key, portion in portions.items():
        if key in name_lower:
            return portion
    
    return 100

async def admin_parse_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Диагностика страницы для отладки парсера"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет прав.")
        return
    
    await update.message.reply_text("🔍 Анализирую страницу...")
    
    import requests
    from bs4 import BeautifulSoup
    
    url = "https://calorizator.ru/product/all?page=0"
    
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Показываем структуру
        await update.message.reply_text(f"✅ Страница загружена: {len(response.text)} символов")
        
        # Ищем div с классом view-content
        view_content = soup.find('div', class_='view-content')
        if view_content:
            await update.message.reply_text("✅ Найден div.view-content")
            
            # Ищем все строки внутри
            rows = view_content.find_all('div', class_='views-row')
            await update.message.reply_text(f"📋 Найдено views-row: {len(rows)}")
            
            if rows:
                # Показываем первые 3 продукта
                for i, row in enumerate(rows[:3]):
                    # Ищем название
                    title = row.find('div', class_='views-field-title')
                    if title:
                        name = title.text.strip()
                        await update.message.reply_text(f"Продукт {i+1}: {name}")
                    
                    # Ищем КБЖУ
                    fields = row.find_all('div', class_='views-field')
                    for field in fields:
                        field_text = field.text.strip()
                        if 'ккал' in field_text or 'Белки' in field_text:
                            await update.message.reply_text(f"  {field_text[:100]}")
        else:
            await update.message.reply_text("❌ div.view-content не найден")
            
        # Показываем HTML
        await update.message.reply_text(f"📄 HTML первых 2000 символов:\n{response.text[:2000]}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def admin_update_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для админа - обновление базы продуктов"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return
    
    global db_updating
    if db_updating:
        await update.message.reply_text("🔄 Обновление базы уже выполняется. Подождите...")
        return
    
    await update.message.reply_text("🚀 Начинаю обновление базы продуктов...\n⏱️ Это займет 10-20 минут.")
    
    def run_update():
        global db_updating
        db_updating = True
        try:
            from update_foods import update_database
            
            # Передаем токен и chat_id
            result = update_database(
                bot_token=BOT_TOKEN,
                chat_id=user_id
            )
            
            print(f"Обновление завершено: {result}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                import requests
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": user_id, "text": f"❌ Критическая ошибка: {str(e)}"},
                    timeout=30
                )
            except:
                pass
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
        f"Чтобы обновить базу, используй /admin_update_db\n"
        f"Чтобы импортировать data.json, используй /admin_import"
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
            "• шашлык 200г"
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
    application.add_handler(CommandHandler("admin_import", admin_import))
    application.add_handler(CommandHandler("admin_parse_debug", admin_parse_debug))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Бот запущен...")
    print("📝 Команды:")
    print("   /start - начать работу")
    print("   /settings - настройки")
    print("   /stats - статистика")
    print("   /admin_update_db - обновить базу (только админ)")
    print("   /admin_status - статус базы (только админ)")
    print("   /admin_import - импорт из data.json (только админ)")
    print("   /admin_parse_debug - диагностика парсера (только админ)")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()