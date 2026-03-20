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
        
        # Создаем категории
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
            ('international', 'Национальные блюда'),
            ('other', 'Другое'),
        ]
        
        for name, desc in cat_list:
            cat = FoodCategory(name=name, description=desc)
            session.add(cat)
            session.flush()
            categories[name] = cat.id
        
        # Добавляем базовый набор продуктов (остальное добавится через парсер)
        base_foods = [
            # Несколько основных продуктов для теста
            Food(name='avocado', name_ru='авокадо', calories=160, proteins=2, fats=15, carbs=6, category_id=categories['fruits'], default_portion=100),
            Food(name='salad_olivier', name_ru='салат оливье', calories=200, proteins=5, fats=15, carbs=10, category_id=categories['salads'], default_portion=200),
            Food(name='borscht', name_ru='борщ', calories=50, proteins=2, fats=2, carbs=6, category_id=categories['soups'], default_portion=300),
            Food(name='beer_light', name_ru='пиво светлое', calories=42, proteins=0.4, fats=0, carbs=3.5, category_id=categories['drinks'], is_liquid=True, default_portion=500),
            Food(name='peanuts', name_ru='арахис', calories=552, proteins=26, fats=45, carbs=10, category_id=categories['nuts'], default_portion=30),
            Food(name='coffee', name_ru='кофе', calories=2, proteins=0.1, fats=0, carbs=0.3, category_id=categories['drinks'], is_liquid=True, default_portion=200),
            Food(name='sugar', name_ru='сахар', calories=387, proteins=0, fats=0, carbs=99.8, category_id=categories['sweets'], default_portion=7),
        ]
        
        for food in base_foods:
            session.add(food)
        
        session.commit()
        print(f"✅ Добавлено базовых продуктов: {len(base_foods)}")
        session.close()
    
    def find_food(self, name):
        """
        БЫСТРЫЙ поиск продукта
        Возвращает Food объект или None
        """
        session = self.Session()
        name = name.lower().strip()
        
        # 1. Точное совпадение (самое быстрое)
        food = session.query(Food).filter(Food.name_ru == name).first()
        if food:
            session.close()
            return food
        
        # 2. Поиск по вхождению (like)
        foods = session.query(Food).filter(Food.name_ru.ilike(f'%{name}%')).all()
        
        if foods:
            # Сортируем по длине (самое короткое совпадение = самое точное)
            foods.sort(key=lambda x: len(x.name_ru))
            session.close()
            return foods[0]
        
        # 3. Поиск по словам
        words = name.split()
        for word in words:
            if len(word) > 2:  # Игнорируем короткие слова
                food = session.query(Food).filter(Food.name_ru.ilike(f'%{word}%')).first()
                if food:
                    session.close()
                    return food
        
        session.close()
        return None
    
    def find_food_fuzzy(self, name):
        """
        НЕЧЕТКИЙ поиск (если точный не сработал)
        Использует LIKE для поиска похожих названий
        """
        session = self.Session()
        name = name.lower().strip()
        
        # Разбиваем на слова
        words = name.split()
        query = session.query(Food)
        
        for word in words:
            if len(word) > 2:
                query = query.filter(Food.name_ru.ilike(f'%{word}%'))
        
        foods = query.limit(5).all()
        session.close()
        
        if foods:
            return foods[0]
        return None
    
    def add_food_from_user(self, name, calories=None, proteins=None, fats=None, carbs=None):
        """
        Добавление продукта пользователем
        """
        session = self.Session()
        
        # Проверяем, нет ли уже такого
        existing = session.query(Food).filter(Food.name_ru == name).first()
        if existing:
            session.close()
            return existing
        
        # Создаем новый продукт с базовыми значениями
        new_food = Food(
            name=name.lower().replace(' ', '_'),
            name_ru=name,
            calories=calories or 100,
            proteins=proteins or 5,
            fats=fats or 5,
            carbs=carbs or 10,
            category_id=1,  # other
            default_portion=100
        )
        
        session.add(new_food)
        session.commit()
        session.close()
        return new_food
    
    def add_meal(self, telegram_id, food_name, weight, meal_type='breakfast'):
        """Добавление приема пищи"""
        session = self.Session()
        food = self.find_food(food_name)
        
        if not food:
            # Если не нашли, создаем временный продукт
            food = self.add_food_from_user(food_name)
        
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
        """Получение пользователя"""
        session = self.Session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        session.close()
        return user
    
    def create_user(self, telegram_id):
        """Создание пользователя"""
        session = self.Session()
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
        session.close()
        return user
    
    def update_user_params(self, telegram_id, **kwargs):
        """Обновление параметров пользователя"""
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
        """Статистика за день"""
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