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
            
        print("Инициализация базы данных...")
        
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
            ('bbq', 'Шашлык и гриль'),
            ('other', 'Другое'),
        ]
        
        for name, desc in cat_list:
            cat = FoodCategory(name=name, description=desc)
            session.add(cat)
            session.flush()
            categories[name] = cat.id
        
        # Добавляем продукты (СОКРАЩЕННЫЙ СПИСОК ДЛЯ ТЕСТА)
        foods = [
            # Молочные
            Food(name='cottage cheese 9%', name_ru='творог 9%', calories=169, proteins=18, fats=9, carbs=3, category_id=categories['dairy'], default_portion=150),
            Food(name='cottage cheese 5%', name_ru='творог 5%', calories=145, proteins=21, fats=5, carbs=3, category_id=categories['dairy'], default_portion=150),
            Food(name='milk 2.5%', name_ru='молоко 2.5%', calories=54, proteins=2.9, fats=2.5, carbs=4.7, category_id=categories['dairy'], is_liquid=True, default_portion=200),
            Food(name='kefir 2.5%', name_ru='кефир 2.5%', calories=50, proteins=3, fats=2.5, carbs=4, category_id=categories['dairy'], is_liquid=True, default_portion=200),
            Food(name='sour cream 20%', name_ru='сметана 20%', calories=206, proteins=2.5, fats=20, carbs=3, category_id=categories['dairy'], default_portion=20),
            Food(name='butter', name_ru='масло сливочное', calories=748, proteins=0.5, fats=82.5, carbs=0.8, category_id=categories['dairy'], default_portion=10),
            Food(name='cheese russian', name_ru='сыр российский', calories=363, proteins=24, fats=29, carbs=0, category_id=categories['dairy'], default_portion=30),
            
            # Мясо
            Food(name='pork', name_ru='свинина', calories=320, proteins=14, fats=30, carbs=0, category_id=categories['meat'], default_portion=150),
            Food(name='beef', name_ru='говядина', calories=218, proteins=19, fats=15, carbs=0, category_id=categories['meat'], default_portion=150),
            Food(name='sausage boiled', name_ru='колбаса вареная', calories=250, proteins=12, fats=22, carbs=1.5, category_id=categories['meat'], default_portion=50),
            Food(name='sausage smoked', name_ru='колбаса копченая', calories=400, proteins=16, fats=38, carbs=2, category_id=categories['meat'], default_portion=50),
            
            # Птица
            Food(name='chicken breast', name_ru='куриная грудка', calories=165, proteins=31, fats=3.6, carbs=0, category_id=categories['poultry'], default_portion=150),
            
            # Рыба
            Food(name='salmon', name_ru='лосось', calories=208, proteins=20, fats=13, carbs=0, category_id=categories['fish'], default_portion=150),
            
            # Яйца
            Food(name='eggs', name_ru='яйца', calories=157, proteins=12.7, fats=11.5, carbs=0.7, category_id=categories['eggs'], default_portion=100),
            
            # Овощи
            Food(name='potato', name_ru='картофель', calories=77, proteins=2, fats=0.4, carbs=16, category_id=categories['vegetables'], default_portion=200),
            Food(name='cucumber', name_ru='огурец', calories=15, proteins=0.8, fats=0.1, carbs=3, category_id=categories['vegetables'], default_portion=100),
            Food(name='tomato', name_ru='помидор', calories=18, proteins=0.9, fats=0.2, carbs=3.9, category_id=categories['vegetables'], default_portion=100),
            Food(name='cabbage', name_ru='капуста', calories=25, proteins=1.8, fats=0.1, carbs=4.7, category_id=categories['vegetables'], default_portion=150),
            Food(name='carrot', name_ru='морковь', calories=41, proteins=1.3, fats=0.1, carbs=7, category_id=categories['vegetables'], default_portion=100),
            Food(name='onion', name_ru='лук', calories=40, proteins=1.1, fats=0.1, carbs=8.2, category_id=categories['vegetables'], default_portion=50),
            
            # Фрукты
            Food(name='apple', name_ru='яблоко', calories=52, proteins=0.3, fats=0.2, carbs=11.4, category_id=categories['fruits'], default_portion=150),
            Food(name='banana', name_ru='банан', calories=95, proteins=1.5, fats=0.2, carbs=21.8, category_id=categories['fruits'], default_portion=150),
            Food(name='orange', name_ru='апельсин', calories=43, proteins=0.9, fats=0.2, carbs=8.1, category_id=categories['fruits'], default_portion=150),
            Food(name='avocado', name_ru='авокадо', calories=160, proteins=2, fats=15, carbs=6, category_id=categories['fruits'], default_portion=100),
            
            # Крупы
            Food(name='buckwheat', name_ru='гречка', calories=343, proteins=13, fats=3.3, carbs=68, category_id=categories['grains'], default_portion=200),
            Food(name='rice', name_ru='рис', calories=344, proteins=6.7, fats=0.7, carbs=78, category_id=categories['grains'], default_portion=200),
            Food(name='oatmeal', name_ru='овсянка', calories=366, proteins=12, fats=6, carbs=62, category_id=categories['grains'], default_portion=200),
            Food(name='pasta', name_ru='макароны', calories=350, proteins=12, fats=1.5, carbs=72, category_id=categories['grains'], default_portion=200),
            
            # Хлеб
            Food(name='bread white', name_ru='хлеб белый', calories=265, proteins=9, fats=3.2, carbs=49, category_id=categories['bakery'], default_portion=30),
            Food(name='bread rye', name_ru='хлеб ржаной', calories=200, proteins=6.6, fats=1.2, carbs=34, category_id=categories['bakery'], default_portion=30),
            
            # Масла
            Food(name='oil sunflower', name_ru='масло подсолнечное', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'], default_portion=10),
            Food(name='oil olive', name_ru='масло оливковое', calories=898, proteins=0, fats=99.8, carbs=0, category_id=categories['fats'], default_portion=10),
            
            # Орехи
            Food(name='peanuts', name_ru='арахис', calories=552, proteins=26, fats=45, carbs=10, category_id=categories['nuts'], default_portion=30),
            Food(name='peanuts salted', name_ru='арахис соленый', calories=580, proteins=24, fats=48, carbs=12, category_id=categories['nuts'], default_portion=30),
            Food(name='walnuts', name_ru='грецкие орехи', calories=654, proteins=15, fats=65, carbs=14, category_id=categories['nuts'], default_portion=30),
            
            # Напитки
            Food(name='coffee', name_ru='кофе', calories=2, proteins=0.1, fats=0, carbs=0.3, category_id=categories['drinks'], is_liquid=True, default_portion=200),
            Food(name='tea black', name_ru='чай черный', calories=1, proteins=0, fats=0, carbs=0.3, category_id=categories['drinks'], is_liquid=True, default_portion=200),
            Food(name='sugar', name_ru='сахар', calories=387, proteins=0, fats=0, carbs=99.8, category_id=categories['sweets'], default_portion=7),
            Food(name='beer light', name_ru='пиво светлое', calories=42, proteins=0.4, fats=0, carbs=3.5, category_id=categories['drinks'], is_liquid=True, default_portion=500),
            Food(name='beer dark', name_ru='пиво темное', calories=48, proteins=0.5, fats=0, carbs=4, category_id=categories['drinks'], is_liquid=True, default_portion=500),
            
            # Супы
            Food(name='borscht', name_ru='борщ', calories=50, proteins=2, fats=2, carbs=6, category_id=categories['soups'], is_liquid=True, default_portion=300),
            
            # Салаты
            Food(name='salad olivier', name_ru='салат оливье', calories=200, proteins=5, fats=15, carbs=10, category_id=categories['salads'], default_portion=200),
            Food(name='salad caesar', name_ru='салат цезарь', calories=180, proteins=8, fats=10, carbs=8, category_id=categories['salads'], default_portion=200),
            
            # Шашлык
            Food(name='shashlik pork', name_ru='шашлык из свинины', calories=280, proteins=15, fats=24, carbs=1, category_id=categories['bbq'], default_portion=200),
            Food(name='shashlik chicken', name_ru='шашлык из курицы', calories=160, proteins=22, fats=7, carbs=1, category_id=categories['bbq'], default_portion=200),
        ]
        
        for food in foods:
            session.add(food)
        
        session.commit()
        print(f"✅ Добавлено продуктов: {len(foods)}")
        session.close()
    
    def find_food(self, name):
        """Поиск продукта"""
        session = self.Session()
        name = name.lower().strip()
        
        # Точное совпадение
        food = session.query(Food).filter(Food.name_ru == name).first()
        if food:
            session.close()
            return food
        
        # Частичное совпадение
        foods = session.query(Food).filter(Food.name_ru.ilike(f'%{name}%')).all()
        if foods:
            # Сортируем по длине (самое короткое - самое точное)
            foods.sort(key=lambda x: len(x.name_ru))
            session.close()
            return foods[0]
        
        # Поиск по английскому названию
        food = session.query(Food).filter(Food.name.ilike(f'%{name}%')).first()
        if food:
            session.close()
            return food
        
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