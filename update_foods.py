#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
Прямой парсинг таблицы с calorizator.ru
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
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    total_pages = 86
    total_saved = 0
    
    for page_num in range(total_pages):
        if page_num == 0:
            url = f"{base_url}/product/all"
        else:
            url = f"{base_url}/product/all?page={page_num}"
        
        send_message(f"\n📄 Страница {page_num+1}/{total_pages}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем таблицу по классу или содержимому
            # Способ 1: ищем таблицу с заголовком "Продукт"
            table = None
            for t in soup.find_all('table'):
                if t.find(string=re.compile('Продукт')):
                    table = t
                    break
            
            # Способ 2: ищем div с классом view-content, внутри которого таблица
            if not table:
                view_content = soup.find('div', class_='view-content')
                if view_content:
                    table = view_content.find('table')
            
            # Способ 3: ищем любую таблицу, которая содержит слово "ккал" в заголовке
            if not table:
                for t in soup.find_all('table'):
                    if t.find(string=re.compile('ккал', re.IGNORECASE)):
                        table = t
                        break
            
            # Способ 4: просто берем первую таблицу, если она есть
            if not table:
                tables = soup.find_all('table')
                if tables:
                    table = tables[0]
            
            if not table:
                send_message(f"   ❌ Таблица не найдена")
                continue
            
            # Парсим строки
            rows = table.find_all('tr')
            products = []
            
            # Ищем индекс строки с заголовками
            header_idx = 0
            for i, row in enumerate(rows):
                if row.find(string=re.compile('Продукт')):
                    header_idx = i
                    break
            
            # Обрабатываем строки после заголовка
            for row in rows[header_idx + 1:]:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    product_name = cols[0].text.strip()
                    if not product_name or product_name == 'Продукт':
                        continue
                    
                    try:
                        protein = parse_value(cols[1].text)
                        fat = parse_value(cols[2].text)
                        carbs = parse_value(cols[3].text)
                        calories = parse_value(cols[4].text)
                    except Exception as e:
                        continue
                    
                    products.append({
                        'name': product_name,
                        'calories': calories,
                        'protein': protein,
                        'fat': fat,
                        'carbs': carbs,
                    })
            
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
    
    return f"Обновление завершено! Всего добавлено: {total_saved}"

def parse_value(text):
    if not text:
        return 0.0
    text = text.strip().replace(',', '.')
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return 0.0

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
        name_lower = p['name'].lower()
        category = 'other'
        
        if any(word in name_lower for word in ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана', 'ряженка', 'актимель', 'активиа']):
            category = 'dairy'
        elif any(word in name_lower for word in ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса', 'сосиски', 'ветчина', 'бекон', 'сало']):
            category = 'meat'
        elif any(word in name_lower for word in ['курица', 'индейка', 'утка', 'гусь', 'цыпленок']):
            category = 'poultry'
        elif any(word in name_lower for word in ['рыба', 'лосось', 'семга', 'форель', 'скумбрия', 'сельдь', 'треска', 'минтай', 'хек', 'креветка', 'кальмар']):
            category = 'fish'
        elif any(word in name_lower for word in ['яйцо', 'яйца', 'омлет']):
            category = 'eggs'
        elif any(word in name_lower for word in ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'огурец', 'помидор', 'перец', 'кабачок', 'баклажан']):
            category = 'vegetables'
        elif any(word in name_lower for word in ['яблоко', 'банан', 'апельсин', 'мандарин', 'груша', 'виноград', 'клубника', 'малина', 'авокадо', 'ананас', 'арбуз', 'дыня', 'абрикос', 'персик', 'слива', 'вишня']):
            category = 'fruits'
        elif any(word in name_lower for word in ['гречка', 'рис', 'овсянка', 'пшено', 'перловка', 'манка', 'макароны', 'паста', 'спагетти']):
            category = 'grains'
        elif any(word in name_lower for word in ['хлеб', 'батон', 'булка', 'лаваш', 'сухарь']):
            category = 'bakery'
        elif any(word in name_lower for word in ['масло', 'маргарин', 'майонез']):
            category = 'fats'
        elif any(word in name_lower for word in ['орех', 'арахис', 'миндаль', 'фундук', 'кешью']):
            category = 'nuts'
        elif any(word in name_lower for word in ['кофе', 'чай', 'сок', 'компот', 'квас', 'лимонад', 'пиво', 'вино', 'водка', '7up']):
            category = 'drinks'
        elif any(word in name_lower for word in ['шоколад', 'конфета', 'печенье', 'вафли', 'халва', 'зефир', 'мармелад', 'мед', 'сахар']):
            category = 'sweets'
        elif any(word in name_lower for word in ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха']):
            category = 'soups'
        elif any(word in name_lower for word in ['салат', 'оливье', 'винегрет', 'цезарь']):
            category = 'salads'
        
        category_id = categories.get(category, 1)
        name = p['name']
        
        cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (name,))
        if not cursor.fetchone():
            safe_name = name.lower().replace(' ', '_')
            safe_name = re.sub(r'[^a-zа-я0-9_]', '', safe_name)
            if not safe_name:
                safe_name = f"product_{hash(name)}"
            
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