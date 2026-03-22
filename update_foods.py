#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
"""
import requests
from bs4 import BeautifulSoup
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
    """Парсит все страницы"""
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    send_message("📡 Получаю первую страницу для проверки...")
    
    # Сначала проверим первую страницу и покажем HTML
    test_url = f"{base_url}/product/all"
    try:
        response = requests.get(test_url, headers=headers, timeout=30)
        html = response.text
        
        send_message(f"✅ Страница загружена: {len(html)} символов")
        
        # Ищем таблицу
        if '<table' in html:
            send_message("✅ Найдено <table> в HTML")
        else:
            send_message("❌ <table> не найдено в HTML")
        
        # Ищем .view-content
        if 'view-content' in html:
            send_message("✅ Найдено .view-content в HTML")
        else:
            send_message("❌ .view-content не найдено")
        
        # Ищем любой контент
        if 'Продукт' in html:
            send_message("✅ Найдено слово 'Продукт' в HTML")
            
            # Найдем позицию первого 'Продукт'
            pos = html.find('Продукт')
            send_message(f"   Позиция: {pos}")
            send_message(f"   Контекст: ...{html[max(0,pos-50):pos+100]}...")
        else:
            send_message("❌ 'Продукт' не найдено")
        
        # Проверим, есть ли защита
        if 'captcha' in html.lower():
            send_message("⚠️ Обнаружена капча!")
        if 'access denied' in html.lower():
            send_message("⚠️ Доступ запрещен!")
            
    except Exception as e:
        send_message(f"❌ Ошибка проверки: {e}")
        return f"Ошибка: {e}"
    
    send_message("📡 Начинаю парсинг всех страниц...")
    
    total_pages = 86
    total_saved = 0
    
    for page_num in range(total_pages):
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
            if saved > 0:
                send_message(f"   💾 Добавлено в БД: {saved} (новых)")
        else:
            send_message(f"   ⚠️ Продуктов не найдено")
        
        time.sleep(1)
    
    return f"Обновление завершено! Всего добавлено: {total_saved}"

def parse_page(url, headers):
    """Парсит одну страницу"""
    products = []
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу
        tables = soup.find_all('table')
        
        if not tables:
            return products
        
        # Берем таблицу с наибольшим количеством строк
        best_table = None
        max_rows = 0
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > max_rows:
                max_rows = len(rows)
                best_table = table
        
        if not best_table:
            return products
        
        rows = best_table.find_all('tr')
        
        # Ищем строку с заголовками
        header_row = None
        for row in rows[:5]:
            if 'Продукт' in row.text:
                header_row = row
                break
        
        if not header_row:
            # Если не нашли заголовок, начинаем со второй строки
            start_idx = 1
        else:
            start_idx = rows.index(header_row) + 1
        
        for row in rows[start_idx:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                product_name = cols[0].text.strip()
                if not product_name:
                    continue
                
                try:
                    protein = parse_value(cols[1].text)
                    fat = parse_value(cols[2].text)
                    carbs = parse_value(cols[3].text)
                    calories = parse_value(cols[4].text)
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
        
    except Exception as e:
        send_message(f"   ⚠️ Ошибка: {e}")
        return []

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