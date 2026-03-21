#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
Парсит https://calorizator.ru/product/all?page=0...85
"""
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
import os
import re
from urllib.parse import urljoin

# Глобальные переменные для отправки сообщений
telegram_bot_url = None
telegram_chat_id = None

def set_telegram_target(bot_token, chat_id):
    global telegram_bot_url, telegram_chat_id
    telegram_bot_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    telegram_chat_id = chat_id

def send_message(text):
    print(text)
    if telegram_bot_url and telegram_chat_id:
        try:
            requests.post(telegram_bot_url, json={"chat_id": telegram_chat_id, "text": text}, timeout=10)
        except:
            pass

def update_database(bot_token=None, chat_id=None):
    try:
        if bot_token and chat_id:
            set_telegram_target(bot_token, chat_id)
        
        send_message("🚀 Начинаю обновление базы...")
        result = parse_calorizator()
        send_message(f"✅ {result}")
        return result
    except Exception as e:
        send_message(f"❌ Ошибка: {str(e)}")
        return str(e)

def parse_calorizator():
    """Парсит все страницы с продуктами"""
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    send_message("📡 Получаю список страниц...")
    
    # Всего страниц: 86 (от 0 до 85)
    total_pages = 86
    send_message(f"📁 Найдено страниц: {total_pages}")
    
    total_saved = 0
    
    for page_num in range(total_pages):
        # Формируем URL: для первой страницы (page=0) используем /product/all
        if page_num == 0:
            url = f"{base_url}/product/all"
        else:
            url = f"{base_url}/product/all?page={page_num}"
        
        send_message(f"\n📄 Страница {page_num+1}/{total_pages}")
        
        products = parse_page(url, headers)
        
        if products:
            send_message(f"   ✅ Найдено продуктов: {len(products)}")
            saved = save_to_sqlite(products)
            total_saved += saved
            send_message(f"   💾 Добавлено в БД: {saved} (новых)")
        else:
            send_message(f"   ⚠️ Продуктов не найдено")
        
        time.sleep(1)  # Пауза между страницами
    
    return f"Обновление завершено! Всего добавлено новых продуктов: {total_saved}"

def parse_page(url, headers):
    """Парсит одну страницу с продуктами"""
    products = []
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу
        table = soup.find('table')
        if not table:
            return products
        
        # Ищем все строки таблицы
        rows = table.find_all('tr')
        
        # Пропускаем заголовок (первую строку)
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                # Название продукта - первая колонка
                product_name = cols[0].text.strip()
                if not product_name or product_name == 'Продукт':
                    continue
                
                # Извлекаем КБЖУ из колонок
                try:
                    protein = parse_value(cols[1].text)
                    fat = parse_value(cols[2].text)
                    carbs = parse_value(cols[3].text)
                    calories = parse_value(cols[4].text)
                except:
                    continue
                
                # Определяем категорию по названию продукта
                category = detect_category(product_name)
                
                products.append({
                    'name': product_name,
                    'category': category,
                    'calories': calories,
                    'protein': protein,
                    'fat': fat,
                    'carbs': carbs,
                })
        
        return products
        
    except Exception as e:
        send_message(f"   ⚠️ Ошибка загрузки {url}: {e}")
        return []

def parse_value(text):
    """Извлекает число из текста"""
    if not text:
        return 0.0
    text = text.strip().replace(',', '.')
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

def detect_category(product_name):
    """Определяет категорию по названию продукта"""
    name_lower = product_name.lower()
    
    categories = {
        'dairy': ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана', 'ряженка', 'сливки', 'активиа', 'актимель', 'тан', 'айран', 'простокваша'],
        'meat': ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса', 'сосиски', 'ветчина', 'бекон', 'сало', 'мясо', 'шницель', 'эскалоп', 'ягнятина'],
        'poultry': ['курица', 'индейка', 'утка', 'гусь', 'цыпленок', 'бройлер', 'перепел'],
        'fish': ['рыба', 'лосось', 'семга', 'форель', 'скумбрия', 'сельдь', 'треска', 'минтай', 'хек', 'креветка', 'кальмар', 'щука', 'окунь', 'карп', 'сом', 'тунец', 'палтус', 'камбала', 'язь', 'юкола', 'ябби'],
        'eggs': ['яйцо', 'яйца', 'омлет', 'яичница'],
        'vegetables': ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'чеснок', 'огурец', 'помидор', 'перец', 'кабачок', 'баклажан', 'тыква', 'редис', 'редька', 'спаржа', 'артишок', 'эндивий', 'эринги'],
        'fruits': ['яблоко', 'банан', 'апельсин', 'мандарин', 'груша', 'виноград', 'клубника', 'малина', 'авокадо', 'ананас', 'арбуз', 'дыня', 'абрикос', 'персик', 'слива', 'вишня', 'черешня', 'киви', 'хурма', 'гранат', 'ягоды', 'ягода', 'инжир', 'финики', 'курага', 'чернослив', 'изюм'],
        'grains': ['гречка', 'рис', 'овсянка', 'пшено', 'перловка', 'манка', 'макароны', 'паста', 'спагетти', 'кускус', 'булгур', 'киноа', 'полба', 'ячмень', 'ячневая', 'овсяные', 'хлопья'],
        'bakery': ['хлеб', 'батон', 'булка', 'лаваш', 'сухарь', 'гренки', 'бублик', 'сушка', 'багет', 'чиабатта', 'лепешка', 'пита', 'тортилья'],
        'fats': ['масло', 'маргарин', 'майонез', 'жир', 'смалец'],
        'nuts': ['орех', 'арахис', 'миндаль', 'фундук', 'кешью', 'фисташка', 'семечка', 'семена', 'кедровый', 'грецкий', 'лесной', 'кокос', 'конопли'],
        'drinks': ['кофе', 'чай', 'сок', 'компот', 'кисель', 'квас', 'лимонад', 'кола', 'пепси', 'фанта', 'спрайт', 'пиво', 'вино', 'водка', 'коньяк', 'виски', 'ром', 'джин', 'ликер', 'энергетический', '7up', 'тарагон'],
        'sweets': ['шоколад', 'конфета', 'печенье', 'вафли', 'халва', 'зефир', 'мармелад', 'варенье', 'джем', 'мед', 'сахар', 'торт', 'пирожное', 'кекс', 'пряник', 'коврижка', 'пастила', 'яблочная пастила'],
        'soups': ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха', 'рассольник', 'бульон'],
        'salads': ['салат', 'оливье', 'винегрет', 'цезарь', 'греческий', 'мимоза', 'шуба'],
        'fastfood': ['бургер', 'гамбургер', 'чизбургер', 'картошка фри', 'наггетсы', 'пицца', 'шаурма', 'хот-дог', 'ролл', 'суши', 'доширак', 'лапша быстрого приготовления'],
        'semi': ['пельмени', 'вареники', 'манты', 'хинкали', 'блины', 'оладьи', 'сырники', 'котлеты', 'тефтели', 'зразы'],
    }
    
    for cat, keywords in categories.items():
        for keyword in keywords:
            if keyword in name_lower:
                return cat
    
    return 'other'

def save_to_sqlite(products):
    """Сохраняет продукты в SQLite"""
    db_path = 'kbju_bot.db'
    
    if not os.path.exists(db_path):
        send_message("   ⚠️ База данных не найдена, создаю...")
        from database import Database
        db = Database()
        db.init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем категории
    cursor.execute("SELECT id, name FROM food_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    added = 0
    for p in products:
        category_id = categories.get(p['category'], 1)
        
        # Проверяем, есть ли уже такой продукт
        cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (p['name'],))
        if not cursor.fetchone():
            # Генерируем уникальное имя для name (латиница)
            safe_name = p['name'].lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('&', '').replace('/', '_')
            safe_name = re.sub(r'[^a-zа-я0-9_]', '', safe_name)
            if not safe_name:
                safe_name = f"product_{hash(p['name'])}"
            
            cursor.execute("""
                INSERT INTO foods 
                (name, name_ru, calories, proteins, fats, carbs, category_id, default_portion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                safe_name[:200],  # ограничиваем длину
                p['name'][:200],
                p['calories'],
                p['protein'],
                p['fat'],
                p['carbs'],
                category_id,
                100
            ))
            added += 1
    
    conn.commit()
    conn.close()
    return added

if __name__ == "__main__":
    result = update_database()
    print(result)