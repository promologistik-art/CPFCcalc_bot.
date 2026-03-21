#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
Вызывается из бота по команде админа
"""
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
import os
import re
from urllib.parse import urljoin
import asyncio

# Глобальная переменная для хранения функции отправки сообщений
send_callback = None
loop = None

def set_send_callback(callback, event_loop=None):
    """Устанавливает функцию для отправки сообщений в Telegram"""
    global send_callback, loop
    send_callback = callback
    loop = event_loop

def send_message(text):
    """Отправляет сообщение через callback (синхронная обертка)"""
    global send_callback, loop
    if send_callback and loop:
        try:
            # Запускаем асинхронную функцию в существующем цикле
            asyncio.run_coroutine_threadsafe(send_callback(text), loop)
        except Exception as e:
            print(f"Ошибка отправки: {e}")
    print(text)

def update_database(chat_id=None, bot=None, event_loop=None):
    """
    Обновление базы данных продуктами
    Если передан bot и chat_id, отправляет сообщения в Telegram
    """
    try:
        # Если есть bot, устанавливаем callback
        if bot and chat_id and event_loop:
            set_send_callback(
                lambda msg: bot.send_message(chat_id=chat_id, text=msg),
                event_loop
            )
        
        send_message("🚀 Начинаю обновление базы...")
        result = parse_calorizator()
        
        send_message(f"✅ {result}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        send_message(error_msg)
        return error_msg

def parse_calorizator():
    """Парсинг calorizator.ru"""
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    send_message("📡 Получаю список категорий...")
    
    # Получаем список категорий
    url = f"{base_url}/product"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        send_message(f"❌ Не удалось загрузить страницу: {e}")
        return "Не удалось подключиться к calorizator.ru"
    
    categories = []
    category_links = soup.select('div.item-list ul li a')
    
    for link in category_links:
        cat_name = link.text.strip()
        cat_url = urljoin(base_url, link['href'])
        if cat_name and 'product' in cat_url:
            categories.append((cat_name, cat_url))
    
    send_message(f"📁 Найдено категорий: {len(categories)}")
    
    total_products = 0
    
    for idx, (cat_name, cat_url) in enumerate(categories):
        send_message(f"\n📂 [{idx+1}/{len(categories)}] Парсинг: {cat_name}")
        
        products = parse_category(cat_url, cat_name, headers, base_url)
        total_products += len(products)
        
        if products:
            send_message(f"   ✅ Найдено продуктов: {len(products)}")
            saved = save_to_sqlite(products)
            send_message(f"   💾 Добавлено в БД: {saved}")
        else:
            send_message(f"   ⚠️ Продуктов не найдено")
        
        time.sleep(1)  # Пауза между категориями
    
    return f"Обновление завершено! Добавлено продуктов: {total_products}"

def parse_category(category_url, category_name, headers, base_url):
    """Парсит категорию"""
    products = []
    page = 1
    
    while True:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_rows = soup.select('table.views-table tbody tr')
            
            if not product_rows:
                break
            
            page_products = 0
            for row in product_rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    product_link = cols[0].find('a')
                    if product_link:
                        product_name = product_link.text.strip()
                        product_url = urljoin(base_url, product_link['href'])
                        
                        product_data = parse_product_page(product_url, product_name, category_name, headers)
                        if product_data:
                            products.append(product_data)
                            page_products += 1
                        
                        time.sleep(0.3)  # Небольшая пауза
            
            send_message(f"   Страница {page}: +{page_products} продуктов")
            page += 1
            
        except requests.exceptions.Timeout:
            send_message(f"   ⚠️ Таймаут на странице {page}, пропускаем")
            break
        except Exception as e:
            send_message(f"   ⚠️ Ошибка: {e}")
            break
    
    return products

def parse_product_page(product_url, product_name, category_name, headers):
    """Парсит страницу продукта"""
    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        nutrition_table = soup.find('table', class_='nutrition-info')
        if not nutrition_table:
            nutrition_table = soup.find('table', class_='views-table')
        
        if nutrition_table:
            calories = extract_value(nutrition_table, 'Калорийность')
            protein = extract_value(nutrition_table, 'Белки')
            fat = extract_value(nutrition_table, 'Жиры')
            carbs = extract_value(nutrition_table, 'Углеводы')
            
            return {
                'name': product_name,
                'category': category_name,
                'calories': calories,
                'protein': protein,
                'fat': fat,
                'carbs': carbs,
            }
        
    except:
        pass
    
    return None

def extract_value(table, label):
    """Извлекает числовое значение из таблицы"""
    try:
        row = table.find('th', string=re.compile(label))
        if row:
            parent_row = row.find_parent('tr')
            if parent_row:
                value_cell = parent_row.find('td')
                if value_cell:
                    value_text = value_cell.text.strip()
                    value_match = re.search(r'(\d+[,.]?\d*)', value_text)
                    if value_match:
                        return float(value_match.group(1).replace(',', '.'))
    except:
        pass
    return 0.0

def save_to_sqlite(products):
    """Сохраняет продукты в SQLite"""
    db_path = 'kbju_bot.db'
    
    if not os.path.exists(db_path):
        send_message("   ⚠️ База данных не найдена")
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем категории
    cursor.execute("SELECT id, name FROM food_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    added = 0
    for p in products:
        cat_name = map_category(p['category'])
        category_id = categories.get(cat_name, 1)  # 1 = other
        
        # Проверяем, есть ли уже такой продукт
        cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (p['name'],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO foods 
                (name, name_ru, calories, proteins, fats, carbs, category_id, default_portion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p['name'].lower().replace(' ', '_').replace('-', '_'),
                p['name'],
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

def map_category(cat_name):
    """Маппинг категорий с calorizator.ru на категории бота"""
    mapping = {
        'Молочные продукты': 'dairy',
        'Мясо': 'meat',
        'Птица': 'poultry',
        'Рыба': 'fish',
        'Яйца': 'eggs',
        'Овощи': 'vegetables',
        'Фрукты': 'fruits',
        'Крупы': 'grains',
        'Хлеб': 'bakery',
        'Масла': 'fats',
        'Орехи': 'nuts',
        'Напитки': 'drinks',
        'Сладости': 'sweets',
        'Супы': 'soups',
        'Салаты': 'salads',
        'Вторые блюда': 'main_dishes',
        'Полуфабрикаты': 'fastfood',
        'Фаст-фуд': 'fastfood',
    }
    return mapping.get(cat_name, 'other')

if __name__ == "__main__":
    # Для запуска из командной строки
    result = update_database()
    print(result)