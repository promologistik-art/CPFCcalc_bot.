#!/usr/bin/env python3
"""
Модуль для обновления базы продуктов
Вызывается из бота по команде админа
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import sqlite3
from urllib.parse import urljoin
import re
import os

def update_database():
    """
    Обновление базы данных продуктами
    Возвращает строку с результатом для отправки в Telegram
    """
    try:
        print("🚀 Начинаю обновление базы...")
        
        # Парсим и сохраняем
        result = parse_calorizator()
        
        print("✅ Обновление завершено")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return f"❌ Ошибка при обновлении: {str(e)}"

def parse_calorizator():
    """Парсинг calorizator.ru"""
    base_url = "https://calorizator.ru"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("📡 Получаем список категорий...")
    
    # Получаем список категорий
    url = f"{base_url}/product"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    categories = []
    category_links = soup.select('div.item-list ul li a')
    
    for link in category_links:
        cat_name = link.text.strip()
        cat_url = urljoin(base_url, link['href'])
        if cat_name and 'product' in cat_url:
            categories.append((cat_name, cat_url))
    
    print(f"📁 Найдено категорий: {len(categories)}")
    
    total_products = 0
    
    for cat_name, cat_url in categories:
        print(f"\n📂 Парсим: {cat_name}")
        products = parse_category(cat_url, cat_name, headers, base_url)
        total_products += len(products)
        print(f"   ✅ Найдено продуктов: {len(products)}")
        
        # Сохраняем в базу после каждой категории
        save_to_sqlite(products)
        
        time.sleep(1)  # Пауза между категориями
    
    return f"✅ Обновление завершено!\n📊 Добавлено продуктов: {total_products}"

def parse_category(category_url, category_name, headers, base_url):
    """Парсит категорию"""
    products = []
    page = 1
    
    while True:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        print(f"   Страница {page}...", end=" ")
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_rows = soup.select('table.views-table tbody tr')
            
            if not product_rows:
                print("пусто")
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
                        
                        time.sleep(0.5)  # Небольшая пауза между запросами
            
            print(f"✅ {page_products} продуктов")
            page += 1
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            break
    
    return products

def parse_product_page(product_url, product_name, category_name, headers):
    """Парсит страницу продукта"""
    try:
        response = requests.get(product_url, headers=headers)
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
        
    except Exception as e:
        # Не печатаем каждую ошибку, чтобы не засорять лог
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
    
    # Проверяем, существует ли база
    if not os.path.exists(db_path):
        print("   ⚠️ База данных не найдена, создаем...")
        from database import Database
        db = Database()
        db.init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем категории
    cursor.execute("SELECT id, name FROM food_categories")
    categories = {name: id for id, name in cursor.fetchall()}
    
    added = 0
    skipped = 0
    
    for p in products:
        # Определяем категорию
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
                guess_portion(p['name'])
            ))
            added += 1
        else:
            skipped += 1
    
    conn.commit()
    conn.close()
    
    if added > 0:
        print(f"   💾 Добавлено в БД: {added} продуктов (пропущено: {skipped})")

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

def guess_portion(name):
    """Определяет стандартную порцию по названию"""
    name_lower = name.lower()
    
    portions = {
        'творог': 150,
        'молоко': 200,
        'кефир': 200,
        'йогурт': 150,
        'сметана': 20,
        'масло': 10,
        'хлеб': 30,
        'батон': 30,
        'булка': 50,
        'сыр': 30,
        'колбаса': 50,
        'сосиски': 50,
        'ветчина': 50,
        'яйцо': 50,
        'яйца': 100,
        'яблоко': 150,
        'банан': 150,
        'апельсин': 150,
        'мандарин': 100,
        'груша': 150,
        'виноград': 150,
        'клубника': 150,
        'малина': 150,
        'авокадо': 100,
        'картофель': 200,
        'картошка': 200,
        'гречка': 200,
        'рис': 200,
        'овсянка': 200,
        'каша': 200,
        'макароны': 200,
        'паста': 200,
        'кофе': 200,
        'чай': 200,
        'сахар': 7,
        'пиво': 500,
        'вино': 150,
        'борщ': 300,
        'суп': 300,
        'салат': 200,
        'шашлык': 200,
        'пельмени': 200,
        'вареники': 200,
        'блины': 150,
        'котлеты': 150,
        'шоколад': 20,
        'конфеты': 15,
        'печенье': 30,
        'арахис': 30,
        'орехи': 30,
    }
    
    for key, portion in portions.items():
        if key in name_lower:
            return portion
    
    return 100

if __name__ == "__main__":
    # Для запуска из командной строки
    result = update_database()
    print(result)