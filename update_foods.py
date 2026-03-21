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
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    send_message("📡 Получаю список категорий...")
    
    url = f"{base_url}/product"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        send_message(f"❌ Не удалось загрузить страницу: {e}")
        return "Не удалось подключиться"
    
    # Ищем категории в меню
    categories = []
    
    # Пробуем разные селекторы
    possible_selectors = [
        'ul.nav.nav-tabs li a',
        'div.views-grouping-header a',
        'div.item-list ul li a',
        'div.view-content ul li a',
        'a[href*="/product/"]'
    ]
    
    for selector in possible_selectors:
        links = soup.select(selector)
        if links:
            for link in links:
                cat_name = link.text.strip()
                cat_url = urljoin(base_url, link['href'])
                if cat_name and len(cat_name) < 50 and '/product/' in cat_url:
                    categories.append((cat_name, cat_url))
            if categories:
                break
    
    # Если ничего не нашли, ищем все ссылки с /product/
    if not categories:
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            if '/product/' in link['href']:
                cat_name = link.text.strip()
                cat_url = urljoin(base_url, link['href'])
                if cat_name and cat_name not in ['Главная', 'О сайте', 'Контакты', 'Все']:
                    categories.append((cat_name, cat_url))
        # Убираем дубликаты
        categories = list(dict.fromkeys(categories))
    
    if not categories:
        send_message("⚠️ Не удалось найти категории. Загружаю резервный список...")
        # Резервный список категорий
        categories = [
            ("Молочные продукты", f"{base_url}/product/molochnye-produkty"),
            ("Мясо", f"{base_url}/product/mjaso"),
            ("Птица", f"{base_url}/product/ptitsa"),
            ("Рыба", f"{base_url}/product/ryba"),
            ("Яйца", f"{base_url}/product/yajca"),
            ("Овощи", f"{base_url}/product/ovoshchi"),
            ("Фрукты", f"{base_url}/product/frukty"),
            ("Крупы", f"{base_url}/product/krupy"),
            ("Хлеб", f"{base_url}/product/hleb"),
            ("Масла", f"{base_url}/product/masla"),
            ("Орехи", f"{base_url}/product/orekhi"),
            ("Напитки", f"{base_url}/product/napitki"),
            ("Сладости", f"{base_url}/product/sladosti"),
            ("Супы", f"{base_url}/product/supy"),
            ("Салаты", f"{base_url}/product/salaty"),
        ]
    
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
        
        time.sleep(1)
    
    return f"Обновление завершено! Добавлено продуктов: {total_products}"

def parse_category(category_url, category_name, headers, base_url):
    products = []
    page = 1
    
    while True:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем таблицу с продуктами
            product_rows = soup.select('table.views-table tbody tr')
            if not product_rows:
                product_rows = soup.select('table tbody tr')
            
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
                        
                        time.sleep(0.3)
            
            if page_products == 0:
                break
                
            send_message(f"   Страница {page}: +{page_products} продуктов")
            page += 1
            
        except Exception as e:
            send_message(f"   ⚠️ Ошибка на странице {page}: {e}")
            break
    
    return products

def parse_product_page(product_url, product_name, category_name, headers):
    try:
        response = requests.get(product_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу с пищевой ценностью
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
    try:
        row = table.find('th', string=re.compile(label, re.IGNORECASE))
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
    db_path = 'kbju_bot.db'
    
    if not os.path.exists(db_path):
        send_message("   ⚠️ База данных не найдена")
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM food_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    added = 0
    for p in products:
        cat_name = map_category(p['category'])
        category_id = categories.get(cat_name, 1)
        
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
    }
    return mapping.get(cat_name, 'other')