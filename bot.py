import logging
import threading
import asyncio
import time
import json
import sqlite3
import os
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import Database
from food_parser import FoodParser
from config import BOT_TOKEN, ADMIN_IDS
from datetime import datetime
from bs4 import BeautifulSoup

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

def check_and_import_data():
    """Проверяет наличие продуктов в базе и при необходимости импортирует из data.json"""
    print("=" * 50)
    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    try:
        food_count = db.get_food_count()
        print(f"📊 Текущее количество продуктов: {food_count}")
    except Exception as e:
        print(f"❌ Ошибка при получении количества: {e}")
        food_count = 0
    
    if food_count == 0 or food_count < 1000:
        print("⚠️ База данных пуста или содержит мало продуктов! Начинаю импорт из data.json...")
        
        if not os.path.exists('data.json'):
            print("❌ Файл data.json не найден!")
            print(f"   Текущая директория: {os.getcwd()}")
            try:
                print(f"   Файлы в директории: {os.listdir('.')}")
            except:
                pass
            return False
        
        print(f"✅ Файл data.json найден, размер: {os.path.getsize('data.json')} байт")
        
        success = db.import_from_json()
        
        if success:
            new_count = db.get_food_count()
            print(f"✅ Импорт завершен! В базе {new_count} продуктов")
            return True
        else:
            print("❌ Ошибка при импорте данных")
            return False
    
    print(f"✅ База данных содержит {food_count} продуктов")
    return True

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

def send_telegram_message(chat_id, text):
    """Синхронная отправка сообщения в Telegram"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30
        )
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def detect_category_import(product_name):
    """Определяет категорию по названию продукта"""
    name_lower = product_name.lower()
    
    categories = {
        'dairy': ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана', 'ряженка', 'сливки', 'активиа', 'актимель', 'айран', 'тан', 'простокваша', 'варенец', 'снежок'],
        'meat': ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса', 'сосиски', 'ветчина', 'бекон', 'сало', 'мясо', 'шницель', 'эскалоп', 'ягнятина', 'конина', 'оленина', 'кролик'],
        'poultry': ['курица', 'индейка', 'утка', 'гусь', 'цыпленок', 'бройлер', 'перепел', 'цесарка'],
        'fish': ['рыба', 'лосось', 'семга', 'форель', 'скумбрия', 'сельдь', 'треска', 'минтай', 'хек', 'креветка', 'кальмар', 'щука', 'окунь', 'карп', 'тунец', 'горбуша', 'кета', 'кижуч', 'палтус', 'камбала', 'язь', 'судак', 'сом', 'налим', 'мойва', 'килька', 'сайра', 'ставрида', 'анчоус', 'муксун', 'нельма', 'омуль', 'пелядь', 'ряпушка', 'сиг', 'чир', 'голец', 'хариус'],
        'eggs': ['яйцо', 'яйца', 'омлет', 'яичница', 'меланж'],
        'vegetables': ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'чеснок', 'огурец', 'помидор', 'перец', 'кабачок', 'баклажан', 'тыква', 'редис', 'редька', 'спаржа', 'артишок', 'эндивий', 'брокколи', 'цветная капуста', 'брюссельская капуста', 'кале', 'руккола', 'салат', 'шпинат', 'щавель', 'петрушка', 'укроп', 'кинза', 'базилик', 'тимьян', 'розмарин'],
        'fruits': ['яблоко', 'банан', 'апельсин', 'мандарин', 'груша', 'виноград', 'клубника', 'малина', 'авокадо', 'ананас', 'арбуз', 'дыня', 'абрикос', 'персик', 'слива', 'вишня', 'черешня', 'киви', 'хурма', 'гранат', 'лимон', 'лайм', 'грейпфрут', 'помело', 'манго', 'папайя', 'фейхоа', 'инжир', 'финики', 'изюм', 'курага', 'чернослив'],
        'grains': ['гречка', 'рис', 'овсянка', 'пшено', 'перловка', 'манка', 'макароны', 'паста', 'спагетти', 'кускус', 'булгур', 'киноа', 'полба', 'ячмень', 'ячневая', 'овсяные хлопья', 'пшеничные хлопья', 'ржаные хлопья', 'кукурузная крупа'],
        'bakery': ['хлеб', 'батон', 'булка', 'лаваш', 'сухарь', 'гренки', 'бублик', 'сушка', 'багет', 'чиабатта', 'лепешка', 'пита', 'тортилья', 'круассан', 'сдоба', 'булочка', 'рогалик', 'кекс', 'маффин'],
        'fats': ['масло', 'маргарин', 'майонез', 'жир', 'смалец', 'спред'],
        'nuts': ['орех', 'арахис', 'миндаль', 'фундук', 'кешью', 'фисташка', 'семечка', 'семена', 'кедровый', 'грецкий', 'лесной', 'кокос', 'конопли', 'кешью', 'пекан', 'макадамия', 'бразильский'],
        'drinks': ['кофе', 'чай', 'сок', 'компот', 'кисель', 'квас', 'лимонад', 'кола', 'пепси', 'фанта', 'спрайт', 'пиво', 'вино', 'водка', 'коньяк', 'виски', 'ром', 'джин', 'ликер', 'энергетический', '7up', 'тарагон', 'коктейль', 'минеральная вода'],
        'sweets': ['шоколад', 'конфета', 'печенье', 'вафли', 'халва', 'зефир', 'мармелад', 'варенье', 'джем', 'мед', 'сахар', 'торт', 'пирожное', 'кекс', 'пряник', 'коврижка', 'пастила', 'ирис', 'карамель', 'нуга', 'марципан', 'лукум'],
        'soups': ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха', 'рассольник', 'бульон', 'харчо', 'мисо'],
        'salads': ['салат', 'оливье', 'винегрет', 'цезарь', 'греческий', 'мимоза', 'шуба', 'столичный', 'крабовый', 'сельдь под шубой'],
        'fastfood': ['бургер', 'гамбургер', 'чизбургер', 'картошка фри', 'наггетсы', 'пицца', 'шаурма', 'хот-дог', 'ролл', 'суши', 'доширак', 'лапша быстрого приготовления', 'сэндвич', 'воппер'],
        'semi': ['пельмени', 'вареники', 'манты', 'хинкали', 'блины', 'оладьи', 'сырники', 'котлеты', 'тефтели', 'зразы', 'чебуреки', 'беляши'],
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
        'квас': 250, 'лимонад': 250, 'кола': 250, 'пепси': 250, 'фанта': 250,
        'пиво': 500, 'вино': 150, 'водка': 50, 'коньяк': 50, 'виски': 50,
        'молоко': 200, 'кефир': 200, 'йогурт': 150, 'творог': 150, 'сметана': 20,
        'хлеб': 30, 'батон': 30, 'булка': 50, 'лаваш': 50,
        'яблоко': 150, 'банан': 150, 'апельсин': 150, 'мандарин': 100,
        'груша': 150, 'виноград': 150, 'клубника': 150, 'малина': 150,
        'картофель': 200, 'гречка': 200, 'рис': 200, 'овсянка': 200,
        'макароны': 200, 'суп': 300, 'борщ': 300, 'салат': 200,
        'шашлык': 200, 'пельмени': 200, 'котлеты': 150, 'блины': 150,
        'шоколад': 20, 'печенье': 30, 'конфеты': 15, 'арахис': 30,
    }
    
    for key, portion in portions.items():
        if key in name_lower:
            return portion
    
    return 100

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
            send_telegram_message(user_id, "📥 Загрузка файла data.json...")
            
            success = db.import_from_json()
            if success:
                food_count = db.get_food_count()
                send_telegram_message(
                    user_id,
                    f"✅ Импорт завершен!\n"
                    f"   Всего продуктов в базе: {food_count}"
                )
            else:
                send_telegram_message(user_id, "❌ Ошибка при импорте!")
        except Exception as e:
            import traceback
            traceback.print_exc()
            send_telegram_message(user_id, f"❌ Критическая ошибка: {str(e)}")
        finally:
            db_updating = False
    
    thread = threading.Thread(target=run_import)
    thread.start()

async def admin_parse_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Диагностика страницы для отладки парсера"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет прав.")
        return
    
    await update.message.reply_text("🔍 Анализирую страницу...")
    
    try:
        response = requests.get("https://calorizator.ru/product/all?page=0", timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        await update.message.reply_text(f"✅ Страница загружена: {len(response.text)} символов")
        
        view_content = soup.find('div', class_='view-content')
        if view_content:
            await update.message.reply_text("✅ Найден div.view-content")
            rows = view_content.find_all('div', class_='views-row')
            await update.message.reply_text(f"📋 Найдено views-row: {len(rows)}")
            
            if rows:
                for i, row in enumerate(rows[:3]):
                    title = row.find('div', class_='views-field-title')
                    if title:
                        await update.message.reply_text(f"Продукт {i+1}: {title.text.strip()}")
        else:
            await update.message.reply_text("❌ div.view-content не найден")
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
            # Проверяем наличие модуля update_foods
            try:
                from update_foods import update_database
                result = update_database(
                    bot_token=BOT_TOKEN,
                    chat_id=user_id
                )
                print(f"Обновление завершено: {result}")
            except ImportError:
                send_telegram_message(user_id, "❌ Модуль update_foods не найден. Используйте /admin_import для импорта данных.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            send_telegram_message(user_id, f"❌ Критическая ошибка: {str(e)}")
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
    
    food_count = db.get_food_count()
    
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
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'awaiting' in context.user_data:
        await handle_parameter_input(update, context)
        return
    
    meal_type = context.user_data.get('meal_type', 'breakfast')
    
    # Парсим сообщение
    items = parser.parse_message(text)
    
    if not items:
        await update.message.reply_text(
            "😕 Не удалось распознать. Попробуйте:\n"
            "• 100г творог 9%\n"
            "• бутерброд с колбасой\n"
            "• кофе 2 ложки сахара\n"
            "• тарелка борща\n"
            "• шашлык 200г"
        )
        return
    
    total = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
    meal_items = []
    not_found = []
    
    for item in items:
        # Ищем в базе
        food = db.find_food_by_word(item['name'])
        
        if food:
            result = db.add_meal_item(user_id, food.id, item['weight'], meal_type)
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
        [InlineKeyboardButton("🍳 Завтрак", callback_data='meal_breakfast'),
         InlineKeyboardButton("🍲 Обед", callback_data='meal_lunch')],
        [InlineKeyboardButton("🍽 Ужин", callback_data='meal_dinner'),
         InlineKeyboardButton("🍎 Перекус", callback_data='meal_snack')],
    ]
    
    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
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
    # Проверяем и импортируем данные перед запуском
    if not check_and_import_data():
        print("⚠️ Бот запускается с пустой базой данных!")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("stats", stats))
    
    # Админские команды
    application.add_handler(CommandHandler("admin_update_db", admin_update_db))
    application.add_handler(CommandHandler("admin_status", admin_status))
    application.add_handler(CommandHandler("admin_import", admin_import))
    application.add_handler(CommandHandler("admin_parse_debug", admin_parse_debug))
    
    # Обработчики кнопок и сообщений
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 50)
    print("🚀 Бот запущен...")
    print("📝 Команды:")
    print("   /start - начать работу")
    print("   /settings - настройки")
    print("   /stats - статистика")
    print("   /admin_update_db - обновить базу (только админ)")
    print("   /admin_status - статус базы (только админ)")
    print("   /admin_import - импорт из data.json (только админ)")
    print("   /admin_parse_debug - диагностика парсера (только админ)")
    print("=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()