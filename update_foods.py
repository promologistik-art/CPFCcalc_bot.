#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
Использует requests-html для выполнения JavaScript
"""
import requests
from requests_html import HTMLSession
import time
import sqlite3
import os
import re

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
    """Парсит все страницы с поддержкой JavaScript"""
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    send_message("📡 Запускаю браузер для загрузки страниц...")
    
    session = HTMLSession()
    
    total_pages = 86
    total_saved = 0
    
    for page_num in range(total_pages):
        if page_num == 0:
            url = f"{base_url}/product/all"
        else:
            url = f"{base_url}/product/all?page={page_num}"
        
        send_message(f"\n📄 Страница {page_num+1}/{total_pages}")
        
        try:
            # Загружаем страницу с выполнением JavaScript
            response = session.get(url, headers=headers)
            response.html.render(timeout=20, sleep=2)  # Ждем 2 секунды после загрузки
            
            # Ищем таблицу после выполнения JS
            table = response.html.find('table')
            
            if not table:
                send_message(f"   ⚠️ Таблица не найдена")
                continue
            
            products = parse_table(table[0])
            
            if products:
                send_message(f"   ✅ Найдено продуктов: {len(products)}")
                saved = save_to_sqlite(products)
                total_saved += saved
                if saved > 0:
                    send_message(f"   💾 Добавлено в БД: {saved} (новых)")
            else:
                send_message(f"   ⚠️ Продуктов не найдено")
            
            time.sleep(1)
            
        except Exception as e:
            send_message(f"   ⚠️ Ошибка: {e}")
            continue
    
    session.close()
    return f"Обновление завершено! Всего добавлено: {total_saved}"

def parse_table(table):
    """Парсит HTML-таблицу"""
    products = []
    
    rows = table.find('tr')
    
    if not rows:
        return products
    
    # Пропускаем заголовок
    for row in rows[1:]:
        cols = row.find('td')
        if cols:
            # Получаем все ячейки в строке
            cells = row.find('td')
            # Если find вернул одну ячейку, нужно получить все
            if not isinstance(cells, list):
                cells = [cells]
            
            if len(cells) >= 5:
                product_name = cells[0].text.strip()
                if not product_name or product_name == 'Продукт':
                    continue
                
                try:
                    protein = parse_value(cells[1].text)
                    fat = parse_value(cells[2].text)
                    carbs = parse_value(cells[3].text)
                    calories = parse_value(cells[4].text)
                except:
                    continue
                
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

def parse_value(text):
    if not text:
        return 0.0
    text = text.strip().replace(',', '.')
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

def detect_category(name):
    name_lower = name.lower()
    
    categories = {
        'dairy': ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана', 'сливки', 'активиа', 'актимель'],
        'meat': ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса', 'сосиски', 'ветчина', 'бекон', 'сало'],
        'poultry': ['курица', 'индейка', 'утка', 'гусь', 'цыпленок'],
        'fish': ['рыба', 'лосось', 'семга', 'форель', 'скумбрия', 'сельдь', 'треска', 'минтай', 'хек', 'креветка', 'кальмар'],
        'eggs': ['яйцо', 'яйца', 'омлет'],
        'vegetables': ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'огурец', 'помидор', 'перец', 'кабачок'],
        'fruits': ['яблоко', 'банан', 'апельсин', 'мандарин', 'груша', 'виноград', 'клубника', 'малина', 'авокадо', 'абрикос', 'персик', 'слива', 'вишня'],
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

def save_to_sqlite(products):
    db_path = 'kbju_bot.db'
    
    if not os.path.exists(db_path):
        from database import Database
        db = Database()
        db.init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM food_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    added = 0
    for p in products:
        category_id = categories.get(p['category'], 1)
        name = p['name']
        
        cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (name,))
        if not cursor.fetchone():
            safe_name = name.lower().replace(' ', '_')
            safe_name = re.sub(r'[^a-zа-я0-9_]', '', safe_name)
            
            cursor.execute("""
                INSERT INTO foods 
                (name, name_ru, calories, proteins, fats, carbs, category_id, default_portion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                safe_name[:200],
                name[:200],
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