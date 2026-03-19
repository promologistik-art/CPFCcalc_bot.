#!/usr/bin/env python3
"""
Скрипт для проверки базы данных продуктов
"""
from database import Database
from models import Food, FoodCategory

def main():
    print("=" * 60)
    print("🍎 Проверка базы данных продуктов")
    print("=" * 60)
    
    db = Database()
    session = db.Session()
    
    # Получаем статистику
    food_count = session.query(Food).count()
    category_count = session.query(FoodCategory).count()
    
    print(f"\n📊 Статистика:")
    print(f"   Категорий: {category_count}")
    print(f"   Продуктов: {food_count}")
    
    # Показываем категории
    print(f"\n📋 Категории:")
    categories = session.query(FoodCategory).all()
    for cat in categories:
        cat_food_count = session.query(Food).filter_by(category_id=cat.id).count()
        print(f"   • {cat.name}: {cat_food_count} продуктов")
    
    # Поиск продуктов
    print(f"\n🔍 Поиск продуктов:")
    search_terms = ['творог', 'сыр', 'мясо', 'рыба', 'хлеб', 'молоко', 'шашлык', 'борщ']
    
    for term in search_terms:
        foods = session.query(Food).filter(Food.name_ru.ilike(f'%{term}%')).limit(5).all()
        if foods:
            print(f"\n   {term}:")
            for food in foods[:3]:  # Показываем первые 3
                print(f"     • {food.name_ru}: {food.calories} ккал, "
                      f"Б:{food.proteins}г, Ж:{food.fats}г, У:{food.carbs}г")
    
    # Проверка сложных блюд
    print(f"\n🍲 Сложные блюда:")
    complex_dishes = [
        'борщ', 'окрошка', 'пельмени', 'блины', 'шашлык',
        'салат оливье', 'котлеты', 'пюре', 'каша'
    ]
    
    from food_parser import FoodParser
    parser = FoodParser()
    
    for dish in complex_dishes:
        result = parser.parse_message(dish)
        if result:
            print(f"\n   {dish}:")
            for item in result:
                food = db.find_food(item['name'])
                if food:
                    print(f"     • {item['name']} ({item['weight']}г): "
                          f"{food.calories * item['weight'] / 100:.0f} ккал")
    
    session.close()
    
    print("\n" + "=" * 60)
    print("✅ Проверка завершена")

if __name__ == '__main__':
    main()