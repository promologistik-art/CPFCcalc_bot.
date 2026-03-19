#!/usr/bin/env python3
"""
Скрипт для добавления новых продуктов в базу данных
"""
from database import Database
from models import Food, FoodCategory

def main():
    print("=" * 60)
    print("🍎 Добавление нового продукта")
    print("=" * 60)
    
    db = Database()
    session = db.Session()
    
    # Показываем категории
    print("\n📋 Доступные категории:")
    categories = session.query(FoodCategory).all()
    for cat in categories:
        print(f"   {cat.id}. {cat.name} - {cat.description}")
    
    try:
        # Ввод данных
        print("\n📝 Введите данные продукта:")
        name_en = input("   Английское название: ").strip()
        name_ru = input("   Русское название: ").strip()
        
        calories = float(input("   Калории на 100г: "))
        proteins = float(input("   Белки на 100г: "))
        fats = float(input("   Жиры на 100г: "))
        carbs = float(input("   Углеводы на 100г: "))
        
        category_id = int(input("   ID категории: "))
        
        is_liquid = input("   Жидкий? (y/n): ").lower() == 'y'
        
        default_portion = input("   Стандартная порция в г (Enter если нет): ").strip()
        default_portion = float(default_portion) if default_portion else None
        
        # Проверяем существование категории
        category = session.query(FoodCategory).get(category_id)
        if not category:
            print(f"❌ Категория с ID {category_id} не найдена")
            return
        
        # Создаем продукт
        food = Food(
            name=name_en,
            name_ru=name_ru,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbs=carbs,
            category_id=category_id,
            is_liquid=is_liquid,
            default_portion=default_portion
        )
        
        session.add(food)
        session.commit()
        
        print(f"\n✅ Продукт '{name_ru}' успешно добавлен!")
        
    except ValueError as e:
        print(f"❌ Ошибка ввода: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    main()