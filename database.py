from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Food, FoodCategory, User, MealEntry
from datetime import datetime

class Database:
    def __init__(self, db_path='sqlite:///kbju_bot.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_database(self):
        """Инициализация базы данных с продуктами"""
        session = self.Session()
        
        if session.query(Food).count() > 0:
            session.close()
            return
            
        print("🚀 Инициализация базы данных...")
        
        categories = {}
        cat_list = [
            ('dairy', 'Молочные продукты'),
            ('meat', 'Мясо и мясные продукты'),
            ('poultry', 'Птица'),
            ('fish', 'Рыба и морепродукты'),
            ('eggs', 'Яйца'),
            ('vegetables', 'Овощи'),
            ('fruits', 'Фрукты и ягоды'),
            ('grains', 'Крупы и злаки'),
            ('bakery', 'Хлеб и выпечка'),
            ('fats', 'Масла и жиры'),
            ('nuts', 'Орехи и семена'),
            ('drinks', 'Напитки'),
            ('sweets', 'Сладости'),
            ('soups', 'Супы'),
            ('salads', 'Салаты'),
            ('main_dishes', 'Вторые блюда'),
            ('fastfood', 'Фастфуд'),
            ('other', 'Другое'),
        ]
        
        for name, desc in cat_list:
            cat = FoodCategory(name=name, description=desc)
            session.add(cat)
            session.flush()
            categories[name] = cat.id
        
        base_foods = [
            Food(name='cottage cheese 9%', name_ru='творог 9%', calories=169, proteins=18, fats=9, carbs=3, category_id=categories['dairy'], default_portion=150),
            Food(name='cottage cheese 5%', name_ru='творог 5%', calories=145, proteins=21, fats=5, carbs=3, category_id=categories['dairy'], default_portion=150),
            Food(name='milk 2.5%', name_ru='молоко 2.5%', calories=54, proteins=2.9, fats=2.5, carbs=4.7, category_id=categories['dairy'], is_liquid=True, default_portion=200),
            Food(name='kefir 2.5%', name_ru='кефир 2.5%', calories=50, proteins=3, fats=2.5, carbs=4, category_id=categories['dairy'], is_liquid=True, default_portion=200),
            Food(name='sour cream 20%', name_ru='сметана 20%', calories=206, proteins=2.5, fats=20, carbs=3, category_id=categories['dairy'], default_portion=20),
            Food(name='butter', name_ru='масло сливочное', calories=748, proteins=0.5, fats=82.5, carbs=0.8, category_id=categories['dairy'], default_portion=10),
            Food(name='cheese russian', name_ru='сыр российский', calories=363, proteins=24, fats=29, carbs=0, category_id=categories['dairy'], default_portion=30),
            Food(name='sausage boiled', name_ru='колбаса вареная', calories=250, proteins=12, fats=22, carbs=1.5, category_id=categories['meat'], default_portion=50),
            Food(name='sausage smoked', name_ru='колбаса копченая', calories=400, proteins=16, fats=38, carbs=2, category_id=categories['meat'], default_portion=50),
            Food(name='chicken breast', name_ru='куриная грудка', calories=165, proteins=31, fats=3.6, carbs=0, category_id=categories['poultry'], default_portion=150),
            Food(name='shashlik pork', name_ru='шашлык из свинины', calories=280, proteins=15, fats=24, carbs=1, category_id=categories['main_dishes'], default_portion=200),
            Food(name='beer light', name_ru='пиво светлое', calories=42, proteins=0.4, fats=0, carbs=3.5, category_id=categories['drinks'], is_liquid=True, default_portion=500),
            Food(name='peanuts', name_ru='арахис', calories=552, proteins=26, fats=45, carbs=10, category_id=categories['nuts'], default_portion=30),
            Food(name='avocado', name_ru='авокадо', calories=160, proteins=2, fats=15, carbs=6, category_id=categories['fruits'], default_portion=100),
            Food(name='coffee', name_ru='кофе', calories=2, proteins=0.1, fats=0, carbs=0.3, category_id=categories['drinks'], is_liquid=True, default_portion=200),
            Food(name='sugar', name_ru='сахар', calories=387, proteins=0, fats=0, carbs=99.8, category_id=categories['sweets'], default_portion=7),
            Food(name='bread white', name_ru='хлеб белый', calories=265, proteins=9, fats=3.2, carbs=49, category_id=categories['bakery'], default_portion=30),
            Food(name='borscht', name_ru='борщ', calories=50, proteins=2, fats=2, carbs=6, category_id=categories['soups'], is_liquid=True, default_portion=300),
            Food(name='salad olivier', name_ru='салат оливье', calories=200, proteins=5, fats=15, carbs=10, category_id=categories['salads'], default_portion=200),
            Food(name='eggs', name_ru='яйца', calories=157, proteins=12.7, fats=11.5, carbs=0.7, category_id=categories['eggs'], default_portion=100),
        ]
        
        for food in base_foods:
            session.add(food)
        
        session.commit()
        print(f"✅ Добавлено базовых продуктов: {len(base_foods)}")
        session.close()
    
    def find_food(self, name):
        """
        УНИВЕРСАЛЬНЫЙ поиск продукта в базе
        """
        session = self.Session()
        name = name.lower().strip()
        
        print(f"🔍 ИЩЕМ: '{name}'")
        
        # 1. Точное совпадение
        food = session.query(Food).filter(Food.name_ru == name).first()
        if food:
            print(f"✅ Найдено точное: {food.name_ru}")
            session.close()
            return food
        
        # 2. Поиск по вхождению (содержит)
        food = session.query(Food).filter(Food.name_ru.ilike(f'%{name}%')).first()
        if food:
            print(f"✅ Найдено по вхождению: {food.name_ru}")
            session.close()
            return food
        
        # 3. Поиск по словам (все слова должны быть в названии)
        words = [w for w in name.split() if len(w) > 2]
        if len(words) > 1:
            print(f"🔍 Ищем по словам: {words}")
            query = session.query(Food)
            for word in words:
                query = query.filter(Food.name_ru.ilike(f'%{word}%'))
            
            foods = query.all()
            if foods:
                print(f"✅ Найдено по словам: {len(foods)} вариантов")
                for f in foods[:3]:
                    print(f"   - {f.name_ru}")
                foods.sort(key=lambda x: len(x.name_ru))
                session.close()
                return foods[0]
        
        # 4. Поиск по одному слову
        for word in words:
            food = session.query(Food).filter(Food.name_ru.ilike(f'%{word}%')).first()
            if food:
                print(f"✅ Найдено по слову '{word}': {food.name_ru}")
                session.close()
                return food
        
        # 5. Поиск по английскому названию
        food = session.query(Food).filter(Food.name.ilike(f'%{name}%')).first()
        if food:
            print(f"✅ Найдено по английскому: {food.name_ru}")
            session.close()
            return food
        
        print(f"❌ НИЧЕГО НЕ НАЙДЕНО для '{name}'")
        session.close()
        return None
    
    def add_meal(self, telegram_id, food_name, weight, meal_type='breakfast'):
        """Добавление приема пищи"""
        session = self.Session()
        
        food = self.find_food(food_name)
        
        if not food:
            session.close()
            return None
        
        meal = MealEntry(
            user_id=telegram_id,
            food_id=food.id,
            weight=weight,
            date=datetime.now().strftime('%Y-%m-%d'),
            meal_type=meal_type
        )
        
        session.add(meal)
        session.commit()
        
        result = {
            'name': food.name_ru,
            'weight': weight,
            'calories': round(food.calories * weight / 100, 1),
            'proteins': round(food.proteins * weight / 100, 1),
            'fats': round(food.fats * weight / 100, 1),
            'carbs': round(food.carbs * weight / 100, 1)
        }
        
        session.close()
        return result
    
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
        meals = session.query(MealEntry).filter_by(
            user_id=telegram_id,
            date=date
        ).all()
        
        total = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
        meals_by_type = {'breakfast': [], 'lunch': [], 'dinner': [], 'snack': []}
        
        for meal in meals:
            food = meal.food
            k = meal.weight / 100
            meal_data = {
                'name': food.name_ru,
                'weight': meal.weight,
                'calories': food.calories * k,
                'proteins': food.proteins * k,
                'fats': food.fats * k,
                'carbs': food.carbs * k
            }
            
            meals_by_type[meal.meal_type].append(meal_data)
            
            total['calories'] += meal_data['calories']
            total['proteins'] += meal_data['proteins']
            total['fats'] += meal_data['fats']
            total['carbs'] += meal_data['carbs']
        
        session.close()
        
        return {'date': date, 'meals': meals_by_type, 'total': total}