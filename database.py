from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Food, FoodCategory, User, MealEntry
from datetime import datetime
import os
import json
import re
import sqlite3


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv('DATABASE_URL', 'sqlite:///kbju_bot.db')

        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def init_database(self):
        session = self.Session()
        if session.query(Food).count() > 0:
            session.close()
            return

        print("🚀 Инициализация базы данных...")

        categories = {}
        cat_list = [
            ('dairy', 'Молочные продукты'), ('meat', 'Мясо'), ('poultry', 'Птица'),
            ('fish', 'Рыба'), ('eggs', 'Яйца'), ('vegetables', 'Овощи'),
            ('fruits', 'Фрукты'), ('grains', 'Крупы'), ('bakery', 'Хлеб'),
            ('fats', 'Жиры'), ('nuts', 'Орехи'), ('drinks', 'Напитки'),
            ('sweets', 'Сладости'), ('soups', 'Супы'), ('salads', 'Салаты'),
            ('main_dishes', 'Горячее'), ('fastfood', 'Фастфуд'), ('other', 'Другое'),
        ]

        for name, desc in cat_list:
            cat = FoodCategory(name=name, description=desc)
            session.add(cat)
            session.flush()
            categories[name] = cat.id

        base_foods = [
            Food(name='eggs', name_ru='яйца', calories=157, proteins=12.7, fats=11.5, carbs=0.7,
                 category_id=categories['eggs'], default_portion=100),
            Food(name='coffee', name_ru='кофе', calories=2, proteins=0.1, fats=0, carbs=0.3,
                 category_id=categories['drinks'], is_liquid=True, default_portion=200),
            Food(name='sugar', name_ru='сахар', calories=387, proteins=0, fats=0, carbs=99.8,
                 category_id=categories['sweets'], default_portion=7),
            Food(name='bread white', name_ru='хлеб белый', calories=265, proteins=9, fats=3.2, carbs=49,
                 category_id=categories['bakery'], default_portion=30),
            Food(name='butter', name_ru='масло сливочное', calories=748, proteins=0.5, fats=82.5, carbs=0.8,
                 category_id=categories['dairy'], default_portion=10),
            Food(name='cheese', name_ru='сыр российский', calories=363, proteins=24, fats=29, carbs=0,
                 category_id=categories['dairy'], default_portion=30),
            Food(name='milk', name_ru='молоко 2.5%', calories=54, proteins=2.9, fats=2.5, carbs=4.7,
                 category_id=categories['dairy'], is_liquid=True, default_portion=200),
            Food(name='kefir', name_ru='кефир 2.5%', calories=50, proteins=3, fats=2.5, carbs=4,
                 category_id=categories['dairy'], is_liquid=True, default_portion=200),
        ]

        for food in base_foods:
            session.add(food)

        session.commit()
        print(f"✅ Добавлено базовых продуктов: {len(base_foods)}")
        session.close()

    def import_from_json(self):
        print("🔄 Импорт из data.json...")

        if not os.path.exists('data.json'):
            print("❌ Файл data.json не найден!")
            return False

        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                products = json.load(f)

            print(f"📦 Загружено: {len(products)} продуктов")

            conn = sqlite3.connect('kbju_bot.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id, name FROM food_categories")
            categories = {name: id for id, name in cursor.fetchall()}

            added = 0
            skipped = 0

            for name, data in products.items():
                category = self._detect_category(name)
                category_id = categories.get(category, 1)

                cursor.execute("SELECT id FROM foods WHERE name_ru = ?", (name,))
                if cursor.fetchone():
                    skipped += 1
                    continue

                safe_name = re.sub(r'[^a-zа-я0-9_]', '_', name.lower().replace(' ', '_'))[:200]
                if not safe_name:
                    safe_name = f"product_{hash(name)}"

                cursor.execute("""
                    INSERT INTO foods 
                    (name, name_ru, calories, proteins, fats, carbs, category_id, default_portion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    safe_name, name[:200],
                    data.get('calories', 0),
                    data.get('protein', 0),
                    data.get('fat', 0),
                    data.get('carbohydrates', 0),
                    category_id,
                    self._guess_portion(name)
                ))
                added += 1

                if added % 1000 == 0:
                    conn.commit()
                    print(f"   Импортировано {added}...")

            conn.commit()
            conn.close()
            print(f"✅ Добавлено: {added}, Пропущено: {skipped}")
            return True

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def _detect_category(self, name):
        name_lower = name.lower()
        cats = {
            'dairy': ['молоко', 'кефир', 'йогурт', 'творог', 'сыр', 'сметана'],
            'meat': ['говядина', 'свинина', 'телятина', 'баранина', 'колбаса'],
            'poultry': ['курица', 'индейка', 'утка', 'гусь'],
            'fish': ['рыба', 'лосось', 'семга', 'форель', 'сельдь', 'треска', 'минтай'],
            'eggs': ['яйцо', 'яйца', 'омлет', 'яичница'],
            'vegetables': ['картофель', 'капуста', 'морковь', 'свекла', 'лук', 'огурец', 'помидор'],
            'fruits': ['яблоко', 'банан', 'апельсин', 'груша', 'виноград'],
            'grains': ['гречка', 'рис', 'овсянка', 'пшено', 'манка', 'макароны'],
            'bakery': ['хлеб', 'батон', 'булка', 'лаваш'],
            'drinks': ['кофе', 'чай', 'сок', 'компот', 'пиво', 'вино'],
            'sweets': ['шоколад', 'конфета', 'печенье', 'варенье', 'мед', 'сахар'],
            'soups': ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха', 'рассольник'],
            'salads': ['салат', 'оливье', 'винегрет', 'цезарь'],
            'fastfood': ['бургер', 'пицца', 'шаурма'],
        }
        for cat, keywords in cats.items():
            for kw in keywords:
                if kw in name_lower:
                    return cat
        return 'other'

    def _guess_portion(self, name):
        name_lower = name.lower()
        portions = {
            'кофе': 200, 'чай': 200, 'сок': 200, 'молоко': 200, 'кефир': 200,
            'йогурт': 150, 'творог': 150, 'сметана': 20, 'хлеб': 30,
            'яблоко': 150, 'банан': 150, 'картофель': 200,
            'гречка': 200, 'рис': 200, 'овсянка': 200, 'макароны': 200,
            'суп': 350, 'борщ': 350, 'щи': 350, 'солянка': 350,
            'салат': 200, 'шашлык': 200, 'пельмени': 200,
        }
        for key, portion in portions.items():
            if key in name_lower:
                return portion
        return 100

    def find_food_by_word(self, word):
        """
        Ищет продукт по одному слову
        """
        session = self.Session()
        word = word.lower().strip()
        
        print(f"      🔍 Ищем слово: '{word}'")
        
        # 1. Точное совпадение
        food = session.query(Food).filter(Food.name_ru == word).first()
        if food:
            print(f"      ✅ Точное: {food.name_ru}")
            session.close()
            return food
        
        # 2. Название начинается с искомого слова
        food = session.query(Food).filter(Food.name_ru.ilike(f'{word}%')).first()
        if food:
            print(f"      ✅ Начинается с: {food.name_ru}")
            session.close()
            return food
        
        # 3. Ищем по отдельным словам в названии
        all_foods = session.query(Food).all()
        for food in all_foods:
            food_words = food.name_ru.lower().split()
            if word in food_words:
                print(f"      ✅ Найдено по слову: {food.name_ru}")
                session.close()
                return food
        
        print(f"      ❌ Не найдено")
        session.close()
        return None

    def add_meal(self, telegram_id, food_name, weight, meal_type='breakfast'):
        session = self.Session()
        
        # Разбиваем на слова
        words = food_name.lower().split()
        print(f"   Разбор: {words}")
        
        results = []
        
        for word in words:
            # Пропускаем предлоги
            if word in ['с', 'со', 'из', 'на', 'в', 'и', 'или', 'а', 'но']:
                continue
            
            # Специальная обработка для бутерброда
            if word in ['бутерброд', 'бутерброда', 'бутерброде']:
                # Добавляем хлеб
                bread = self.find_food_by_word("хлеб")
                if bread:
                    results.append({
                        'name': bread.name_ru,
                        'weight': 50,
                        'calories': bread.calories * 0.5,
                        'proteins': bread.proteins * 0.5,
                        'fats': bread.fats * 0.5,
                        'carbs': bread.carbs * 0.5
                    })
                    print(f"      ✅ Добавлен хлеб для бутерброда: {bread.name_ru} (50г)")
                continue
            
            # Ищем продукт по слову
            food = self.find_food_by_word(word)
            if food:
                # Определяем вес
                if 'яичница' in word:
                    # Яичница: считаем количество яиц
                    match = re.search(r'(\d+)\s*яйц', food_name)
                    if match:
                        egg_count = int(match.group(1))
                        weight = egg_count * 50
                    else:
                        weight = 200
                else:
                    weight = self._get_portion(word)
                
                results.append({
                    'name': food.name_ru,
                    'weight': weight,
                    'calories': food.calories * weight / 100,
                    'proteins': food.proteins * weight / 100,
                    'fats': food.fats * weight / 100,
                    'carbs': food.carbs * weight / 100
                })
                print(f"      ✅ Найден: {food.name_ru} ({weight}г)")
        
        if not results:
            session.close()
            return None
        
        # Сохраняем каждый найденный продукт
        for result in results:
            meal = MealEntry(
                user_id=telegram_id,
                food_id=session.query(Food).filter(Food.name_ru == result['name']).first().id,
                weight=result['weight'],
                date=datetime.now().strftime('%Y-%m-%d'),
                meal_type=meal_type
            )
            session.add(meal)
        
        session.commit()
        
        # Возвращаем итог
        total = {
            'calories': sum(r['calories'] for r in results),
            'proteins': sum(r['proteins'] for r in results),
            'fats': sum(r['fats'] for r in results),
            'carbs': sum(r['carbs'] for r in results)
        }
        
        session.close()
        
        return {
            'items': results,
            'total': total
        }

    def _get_portion(self, word):
        """Стандартный вес для слова"""
        portions = {
            'кофе': 200, 'чай': 200, 'сок': 200,
            'молоко': 200, 'кефир': 200, 'йогурт': 150,
            'творог': 150, 'сметана': 20,
            'хлеб': 50,
            'яйцо': 50, 'яичница': 200,
            'яблоко': 150, 'банан': 150,
            'картофель': 200,
            'овсяная': 250, 'гречневая': 250, 'манная': 250,
            'каша': 250,
            'суп': 350, 'борщ': 350, 'щи': 350, 'солянка': 350,
            'салат': 200, 'пельмени': 200, 'шашлык': 200,
            'семга': 80, 'авокадо': 80, 'сыр': 30,
        }
        
        for key, portion in portions.items():
            if key in word:
                return portion
        return 100

    def get_user(self, telegram_id):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        session.close()
        return user

    def create_user(self, telegram_id):
        session = self.Session()
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
        session.close()
        return user

    def update_user_params(self, telegram_id, **kwargs):
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            daily_norm = user.calculate_daily_norm()
            if daily_norm:
                user.daily_calories = daily_norm
            session.commit()
        session.close()

    def get_daily_summary(self, telegram_id, date=None):
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        session = self.Session()
        meals = session.query(MealEntry).filter_by(user_id=telegram_id, date=date).all()

        total = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
        meals_by_type = {'breakfast': [], 'lunch': [], 'dinner': [], 'snack': []}

        for meal in meals:
            food = meal.food
            k = meal.weight / 100
            data = {
                'name': food.name_ru, 'weight': meal.weight,
                'calories': food.calories * k, 'proteins': food.proteins * k,
                'fats': food.fats * k, 'carbs': food.carbs * k
            }
            meals_by_type[meal.meal_type].append(data)
            for key in total:
                total[key] += data[key]

        session.close()
        return {'date': date, 'meals': meals_by_type, 'total': total}

    def get_food_count(self):
        session = self.Session()
        count = session.query(Food).count()
        session.close()
        return count