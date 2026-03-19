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
        """Полная инициализация базы данных с категориями и продуктами"""
        session = self.Session()
        
        # Проверяем, есть ли уже данные
        if session.query(Food).count() > 0:
            session.close()
            return
            
        print("Инициализация базы данных...")
        
        # Создаем категории
        categories = {
            'dairy': FoodCategory(name='dairy', description='Молочные продукты'),
            'meat': FoodCategory(name='meat', description='Мясо и мясные продукты'),
            'poultry': FoodCategory(name='poultry', description='Птица'),
            'fish': FoodCategory(name='fish', description='Рыба и морепродукты'),
            'eggs': FoodCategory(name='eggs', description='Яйца'),
            'vegetables': FoodCategory(name='vegetables', description='Овощи'),
            'fruits': FoodCategory(name='fruits', description='Фрукты и ягоды'),
            'grains': FoodCategory(name='grains', description='Крупы и злаки'),
            'bakery': FoodCategory(name='bakery', description='Хлеб и выпечка'),
            'fats': FoodCategory(name='fats', description='Масла и жиры'),
            'nuts': FoodCategory(name='nuts', description='Орехи и семена'),
            'drinks': FoodCategory(name='drinks', description='Напитки'),
            'sweets': FoodCategory(name='sweets', description='Сладости'),
            'sauces': FoodCategory(name='sauces', description='Соусы и приправы'),
            'legumes': FoodCategory(name='legumes', description='Бобовые'),
            'mushrooms': FoodCategory(name='mushrooms', description='Грибы'),
            'fastfood': FoodCategory(name='fastfood', description='Фастфуд'),
            'soups': FoodCategory(name='soups', description='Супы'),
            'bbq': FoodCategory(name='bbq', description='Шашлык и гриль'),
            'canned': FoodCategory(name='canned', description='Консервы'),
            'other': FoodCategory(name='other', description='Другое'),
        }
        
        for cat in categories.values():
            session.add(cat)
        session.flush()  # Чтобы получить id категорий
        
        # Добавляем продукты
        foods = [
            # Молочные продукты
            Food(name='cottage cheese 9%', name_ru='творог 9%', calories=169, proteins=18, fats=9, carbs=3, category_id=categories['dairy'].id, default_portion=150),
            Food(name='cottage cheese 5%', name_ru='творог 5%', calories=145, proteins=21, fats=5, carbs=3, category_id=categories['dairy'].id, default_portion=150),
            Food(name='cottage cheese 2%', name_ru='творог 2%', calories=110, proteins=20, fats=2, carbs=3, category_id=categories['dairy'].id, default_portion=150),
            Food(name='cottage cheese 0%', name_ru='творог обезжиренный', calories=85, proteins=18, fats=0.5, carbs=3, category_id=categories['dairy'].id, default_portion=150),
            Food(name='milk 3.2%', name_ru='молоко 3.2%', calories=60, proteins=2.9, fats=3.2, carbs=4.7, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='milk 2.5%', name_ru='молоко 2.5%', calories=54, proteins=2.9, fats=2.5, carbs=4.7, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='milk 1.5%', name_ru='молоко 1.5%', calories=45, proteins=3, fats=1.5, carbs=4.7, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='milk 0.5%', name_ru='молоко 0.5%', calories=35, proteins=3, fats=0.5, carbs=4.7, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='kefir 3.2%', name_ru='кефир 3.2%', calories=60, proteins=3, fats=3.2, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='kefir 2.5%', name_ru='кефир 2.5%', calories=50, proteins=3, fats=2.5, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='kefir 1%', name_ru='кефир 1%', calories=38, proteins=3, fats=1, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='kefir 0%', name_ru='кефир обезжиренный', calories=30, proteins=3, fats=0.1, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='yogurt natural', name_ru='йогурт натуральный', calories=68, proteins=5, fats=3.2, carbs=3.5, category_id=categories['dairy'].id, default_portion=150),
            Food(name='yogurt fruit', name_ru='йогурт фруктовый', calories=90, proteins=4, fats=2, carbs=15, category_id=categories['dairy'].id, default_portion=150),
            Food(name='yogurt greek', name_ru='йогурт греческий', calories=120, proteins=10, fats=8, carbs=4, category_id=categories['dairy'].id, default_portion=150),
            Food(name='sour cream 30%', name_ru='сметана 30%', calories=290, proteins=2.4, fats=30, carbs=2.8, category_id=categories['dairy'].id, default_portion=30),
            Food(name='sour cream 25%', name_ru='сметана 25%', calories=248, proteins=2.5, fats=25, carbs=3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='sour cream 20%', name_ru='сметана 20%', calories=206, proteins=2.5, fats=20, carbs=3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='sour cream 15%', name_ru='сметана 15%', calories=160, proteins=2.6, fats=15, carbs=3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='sour cream 10%', name_ru='сметана 10%', calories=115, proteins=3, fats=10, carbs=3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cream 35%', name_ru='сливки 35%', calories=350, proteins=2.2, fats=35, carbs=3, category_id=categories['dairy'].id, is_liquid=True, default_portion=50),
            Food(name='cream 33%', name_ru='сливки 33%', calories=330, proteins=2.2, fats=33, carbs=3, category_id=categories['dairy'].id, is_liquid=True, default_portion=50),
            Food(name='cream 20%', name_ru='сливки 20%', calories=205, proteins=2.5, fats=20, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=50),
            Food(name='cream 10%', name_ru='сливки 10%', calories=118, proteins=3, fats=10, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=50),
            Food(name='butter', name_ru='масло сливочное', calories=748, proteins=0.5, fats=82.5, carbs=0.8, category_id=categories['dairy'].id, default_portion=15),
            Food(name='butter ghee', name_ru='масло топленое', calories=900, proteins=0.3, fats=99, carbs=0, category_id=categories['dairy'].id, default_portion=15),
            Food(name='cheese russian', name_ru='сыр российский', calories=363, proteins=24, fats=29, carbs=0, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese parmesan', name_ru='сыр пармезан', calories=392, proteins=36, fats=26, carbs=3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese mozzarella', name_ru='сыр моцарелла', calories=280, proteins=22, fats=20, carbs=2, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese cheddar', name_ru='сыр чеддер', calories=400, proteins=25, fats=33, carbs=1.3, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese gouda', name_ru='сыр гауда', calories=356, proteins=25, fats=27, carbs=2, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese processed', name_ru='сыр плавленый', calories=300, proteins=20, fats=23, carbs=2.5, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese feta', name_ru='сыр фета', calories=264, proteins=14, fats=21, carbs=4, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese suluguni', name_ru='сыр сулугуни', calories=290, proteins=20, fats=22, carbs=1, category_id=categories['dairy'].id, default_portion=30),
            Food(name='cheese adygei', name_ru='сыр адыгейский', calories=240, proteins=18, fats=16, carbs=1.5, category_id=categories['dairy'].id, default_portion=30),
            Food(name='ryazhenka', name_ru='ряженка', calories=85, proteins=3, fats=6, carbs=4, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='varenets', name_ru='варенец', calories=80, proteins=3, fats=5, carbs=5, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='snezhok', name_ru='снежок', calories=90, proteins=3, fats=4, carbs=12, category_id=categories['dairy'].id, default_portion=200),
            Food(name='acidophilus', name_ru='ацидофилин', calories=50, proteins=3, fats=1, carbs=5, category_id=categories['dairy'].id, is_liquid=True, default_portion=200),
            Food(name='ice cream milk', name_ru='мороженое молочное', calories=180, proteins=3.5, fats=3.5, carbs=21, category_id=categories['dairy'].id, default_portion=100),
            Food(name='ice cream creamy', name_ru='мороженое сливочное', calories=200, proteins=3.3, fats=10, carbs=20, category_id=categories['dairy'].id, default_portion=100),
            Food(name='ice cream plombir', name_ru='мороженое пломбир', calories=230, proteins=3.5, fats=15, carbs=20, category_id=categories['dairy'].id, default_portion=100),
            
            # Мясо
            Food(name='pork', name_ru='свинина', calories=320, proteins=14, fats=30, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='pork lean', name_ru='свинина постная', calories=250, proteins=19, fats=19, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='pork neck', name_ru='свиная шея', calories=340, proteins=13, fats=31, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='pork chop', name_ru='свиная отбивная', calories=300, proteins=15, fats=26, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='pork ribs', name_ru='свиные ребра', calories=320, proteins=15, fats=28, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='pork knuckle', name_ru='свиная рулька', calories=350, proteins=14, fats=32, carbs=0, category_id=categories['meat'].id, default_portion=200),
            Food(name='bacon', name_ru='бекон', calories=500, proteins=14, fats=50, carbs=1, category_id=categories['meat'].id, default_portion=30),
            Food(name='salo', name_ru='сало', calories=800, proteins=2, fats=89, carbs=0, category_id=categories['meat'].id, default_portion=30),
            Food(name='salo smoked', name_ru='сало копченое', calories=820, proteins=1.5, fats=90, carbs=0, category_id=categories['meat'].id, default_portion=30),
            Food(name='beef', name_ru='говядина', calories=218, proteins=19, fats=15, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='beef lean', name_ru='говядина постная', calories=158, proteins=22, fats=7, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='beef tenderloin', name_ru='говяжья вырезка', calories=180, proteins=20, fats=10, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='beef steak', name_ru='говяжий стейк', calories=220, proteins=19, fats=16, carbs=0, category_id=categories['meat'].id, default_portion=200),
            Food(name='beef ribs', name_ru='говяжьи ребра', calories=280, proteins=17, fats=23, carbs=0, category_id=categories['meat'].id, default_portion=200),
            Food(name='beef tongue', name_ru='говяжий язык', calories=210, proteins=16, fats=15, carbs=2, category_id=categories['meat'].id, default_portion=100),
            Food(name='beef liver', name_ru='говяжья печень', calories=135, proteins=20, fats=4, carbs=4, category_id=categories['meat'].id, default_portion=100),
            Food(name='beef heart', name_ru='говяжье сердце', calories=112, proteins=16, fats=3.5, carbs=2, category_id=categories['meat'].id, default_portion=100),
            Food(name='beef kidneys', name_ru='говяжьи почки', calories=100, proteins=15, fats=3, carbs=1, category_id=categories['meat'].id, default_portion=100),
            Food(name='veal', name_ru='телятина', calories=131, proteins=20, fats=5, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='lamb', name_ru='баранина', calories=294, proteins=16, fats=25, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='lamb ribs', name_ru='бараньи ребра', calories=320, proteins=15, fats=28, carbs=0, category_id=categories['meat'].id, default_portion=200),
            Food(name='horse meat', name_ru='конина', calories=187, proteins=20, fats=10, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='rabbit', name_ru='кролик', calories=183, proteins=21, fats=11, carbs=0, category_id=categories['meat'].id, default_portion=150),
            
            # Мясные продукты
            Food(name='sausage boiled', name_ru='колбаса вареная', calories=250, proteins=12, fats=22, carbs=1.5, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausage milk', name_ru='колбаса молочная', calories=260, proteins=11, fats=23, carbs=1, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausage doctor', name_ru='колбаса докторская', calories=257, proteins=12, fats=22, carbs=1.5, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausage smoked', name_ru='колбаса копченая', calories=400, proteins=16, fats=38, carbs=2, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausage cervelat', name_ru='сервелат', calories=420, proteins=18, fats=38, carbs=0, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausage salami', name_ru='салями', calories=500, proteins=20, fats=45, carbs=1, category_id=categories['meat'].id, default_portion=50),
            Food(name='ham', name_ru='ветчина', calories=240, proteins=15, fats=20, carbs=1, category_id=categories['meat'].id, default_portion=50),
            Food(name='ham chicken', name_ru='ветчина куриная', calories=150, proteins=18, fats=8, carbs=2, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausages', name_ru='сосиски', calories=300, proteins=11, fats=27, carbs=1.5, category_id=categories['meat'].id, default_portion=50),
            Food(name='sausages milk', name_ru='сосиски молочные', calories=270, proteins=11, fats=24, carbs=1, category_id=categories['meat'].id, default_portion=50),
            Food(name='wieners', name_ru='сардельки', calories=280, proteins=10, fats=25, carbs=2, category_id=categories['meat'].id, default_portion=50),
            Food(name='minced meat', name_ru='фарш мясной', calories=250, proteins=17, fats=20, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='minced pork', name_ru='фарш свиной', calories=320, proteins=14, fats=28, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='minced beef', name_ru='фарш говяжий', calories=218, proteins=18, fats=16, carbs=0, category_id=categories['meat'].id, default_portion=150),
            Food(name='minced chicken', name_ru='фарш куриный', calories=140, proteins=18, fats=7, carbs=0, category_id=categories['meat'].id, default_portion=150),
            
            # Птица
            Food(name='chicken breast', name_ru='куриная грудка', calories=165, proteins=31, fats=3.6, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken fillet', name_ru='куриное филе', calories=165, proteins=31, fats=3.6, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken thigh', name_ru='куриное бедро', calories=210, proteins=19, fats=14, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken leg', name_ru='куриная голень', calories=180, proteins=20, fats=10, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken wing', name_ru='куриное крыло', calories=190, proteins=18, fats=13, carbs=0, category_id=categories['poultry'].id, default_portion=100),
            Food(name='chicken drumstick', name_ru='куриная ножка', calories=185, proteins=19, fats=11, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken back', name_ru='куриная спинка', calories=200, proteins=17, fats=14, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='chicken liver', name_ru='куриная печень', calories=140, proteins=20, fats=6, carbs=1, category_id=categories['poultry'].id, default_portion=100),
            Food(name='chicken heart', name_ru='куриные сердечки', calories=158, proteins=16, fats=10, carbs=1, category_id=categories['poultry'].id, default_portion=100),
            Food(name='chicken stomachs', name_ru='куриные желудки', calories=114, proteins=18, fats=4, carbs=0.5, category_id=categories['poultry'].id, default_portion=100),
            Food(name='turkey breast', name_ru='индейка грудка', calories=135, proteins=30, fats=2, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='turkey thigh', name_ru='индейка бедро', calories=170, proteins=25, fats=7, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='turkey fillet', name_ru='филе индейки', calories=140, proteins=29, fats=2.5, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='duck', name_ru='утка', calories=337, proteins=16, fats=28, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='duck breast', name_ru='утиная грудка', calories=200, proteins=20, fats=13, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='goose', name_ru='гусь', calories=364, proteins=16, fats=33, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            Food(name='quail', name_ru='перепелка', calories=230, proteins=20, fats=16, carbs=0, category_id=categories['poultry'].id, default_portion=150),
            
            # Рыба и морепродукты
            Food(name='salmon', name_ru='лосось', calories=208, proteins=20, fats=13, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='salmon atlantic', name_ru='семга', calories=220, proteins=20, fats=15, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='trout', name_ru='форель', calories=141, proteins=19, fats=6, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='trout rainbow', name_ru='радужная форель', calories=150, proteins=20, fats=7, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='mackerel', name_ru='скумбрия', calories=205, proteins=18, fats=14, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='herring', name_ru='сельдь', calories=246, proteins=17, fats=19, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='herring salted', name_ru='сельдь соленая', calories=260, proteins=16, fats=21, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='cod', name_ru='треска', calories=82, proteins=18, fats=0.7, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='pollock', name_ru='минтай', calories=72, proteins=16, fats=1, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='hake', name_ru='хек', calories=86, proteins=17, fats=2, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='pike', name_ru='щука', calories=84, proteins=18, fats=1, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='perch', name_ru='окунь', calories=82, proteins=18, fats=1, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='carp', name_ru='карп', calories=112, proteins=16, fats=5, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='crucian carp', name_ru='карась', calories=87, proteins=18, fats=2, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='tuna', name_ru='тунец', calories=130, proteins=24, fats=4, carbs=0, category_id=categories['fish'].id, default_portion=150),
            Food(name='tuna canned', name_ru='тунец консервированный', calories=120, proteins=23, fats=3, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='sardine', name_ru='сардина', calories=210, proteins=20, fats=14, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='sprats', name_ru='шпроты', calories=360, proteins=17, fats=32, carbs=0, category_id=categories['fish'].id, default_portion=50),
            Food(name='red caviar', name_ru='икра красная', calories=250, proteins=32, fats=15, carbs=0, category_id=categories['fish'].id, default_portion=30),
            Food(name='black caviar', name_ru='икра черная', calories=280, proteins=35, fats=15, carbs=0, category_id=categories['fish'].id, default_portion=30),
            Food(name='pollock caviar', name_ru='икра минтая', calories=130, proteins=28, fats=2, carbs=0, category_id=categories['fish'].id, default_portion=50),
            Food(name='shrimp', name_ru='креветки', calories=85, proteins=18, fats=1, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='shrimp king', name_ru='королевские креветки', calories=95, proteins=19, fats=1.5, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='squid', name_ru='кальмар', calories=100, proteins=18, fats=2, carbs=2, category_id=categories['fish'].id, default_portion=100),
            Food(name='octopus', name_ru='осьминог', calories=82, proteins=15, fats=2, carbs=2, category_id=categories['fish'].id, default_portion=100),
            Food(name='mussels', name_ru='мидии', calories=86, proteins=12, fats=2, carbs=3, category_id=categories['fish'].id, default_portion=100),
            Food(name='oysters', name_ru='устрицы', calories=90, proteins=10, fats=2, carbs=5, category_id=categories['fish'].id, default_portion=100),
            Food(name='crabs', name_ru='крабы', calories=95, proteins=18, fats=1.5, carbs=0, category_id=categories['fish'].id, default_portion=100),
            Food(name='crab sticks', name_ru='крабовые палочки', calories=95, proteins=6, fats=1, carbs=10, category_id=categories['fish'].id, default_portion=100),
            Food(name='sea kale', name_ru='морская капуста', calories=25, proteins=1, fats=0.2, carbs=3, category_id=categories['fish'].id, default_portion=100),
            
            # Яйца
            Food(name='eggs', name_ru='яйца', calories=157, proteins=12.7, fats=11.5, carbs=0.7, category_id=categories['eggs'].id, default_portion=50),  # 1 яйцо ~50г
            Food(name='eggs chicken', name_ru='яйца куриные', calories=157, proteins=12.7, fats=11.5, carbs=0.7, category_id=categories['eggs'].id, default_portion=50),
            Food(name='eggs quail', name_ru='яйца перепелиные', calories=168, proteins=12, fats=13, carbs=0.6, category_id=categories['eggs'].id, default_portion=10),  # 1 перепелиное ~10г
            Food(name='eggs duck', name_ru='яйца утиные', calories=185, proteins=13, fats=14, carbs=1, category_id=categories['eggs'].id, default_portion=70),
            Food(name='eggs goose', name_ru='яйца гусиные', calories=200, proteins=14, fats=15, carbs=1, category_id=categories['eggs'].id, default_portion=100),
            Food(name='egg white', name_ru='яичный белок', calories=48, proteins=11, fats=0, carbs=1, category_id=categories['eggs'].id, default_portion=30),
            Food(name='egg yolk', name_ru='желток', calories=322, proteins=16, fats=28, carbs=1, category_id=categories['eggs'].id, default_portion=20),
            Food(name='omelette', name_ru='омлет', calories=150, proteins=8, fats=12, carbs=2, category_id=categories['eggs'].id, default_portion=150),
            
            # Овощи
            Food(name='potato', name_ru='картофель', calories=77, proteins=2, fats=0.4, carbs=16, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='potato young', name_ru='картофель молодой', calories=70, proteins=2, fats=0.3, carbs=15, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='potato sweet', name_ru='батат', calories=86, proteins=1.6, fats=0.1, carbs=20, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='cucumber', name_ru='огурец', calories=15, proteins=0.8, fats=0.1, carbs=3, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='cucumber pickled', name_ru='огурец соленый', calories=11, proteins=0.8, fats=0.1, carbs=1.7, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='tomato', name_ru='помидор', calories=18, proteins=0.9, fats=0.2, carbs=3.9, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='tomato cherry', name_ru='помидоры черри', calories=18, proteins=0.9, fats=0.2, carbs=3.9, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='cabbage', name_ru='капуста белокочанная', calories=25, proteins=1.8, fats=0.1, carbs=4.7, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='cabbage red', name_ru='капуста краснокочанная', calories=26, proteins=1.4, fats=0.2, carbs=5, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='cabbage savoy', name_ru='капуста савойская', calories=27, proteins=2, fats=0.1, carbs=6, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='cabbage brussels', name_ru='брюссельская капуста', calories=43, proteins=3.4, fats=0.3, carbs=9, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='broccoli', name_ru='брокколи', calories=34, proteins=2.8, fats=0.4, carbs=6.6, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='cauliflower', name_ru='цветная капуста', calories=30, proteins=2.5, fats=0.3, carbs=5, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='kohlrabi', name_ru='кольраби', calories=27, proteins=1.7, fats=0.1, carbs=6, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='carrot', name_ru='морковь', calories=41, proteins=1.3, fats=0.1, carbs=7, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='onion', name_ru='лук репчатый', calories=40, proteins=1.1, fats=0.1, carbs=8.2, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='onion red', name_ru='лук красный', calories=40, proteins=1.1, fats=0.1, carbs=8, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='onion green', name_ru='лук зеленый', calories=20, proteins=1.3, fats=0.1, carbs=3.5, category_id=categories['vegetables'].id, default_portion=30),
            Food(name='leek', name_ru='лук-порей', calories=36, proteins=1.5, fats=0.2, carbs=6.5, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='garlic', name_ru='чеснок', calories=149, proteins=6.5, fats=0.5, carbs=30, category_id=categories['vegetables'].id, default_portion=10),
            Food(name='pepper bell', name_ru='перец болгарский', calories=27, proteins=1.3, fats=0.1, carbs=5.3, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='pepper red', name_ru='перец красный', calories=31, proteins=1.3, fats=0.3, carbs=5.9, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='pepper green', name_ru='перец зеленый', calories=20, proteins=0.9, fats=0.2, carbs=4.6, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='pepper chili', name_ru='перец чили', calories=40, proteins=2, fats=0.4, carbs=8, category_id=categories['vegetables'].id, default_portion=10),
            Food(name='zucchini', name_ru='кабачок', calories=24, proteins=0.6, fats=0.3, carbs=4.6, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='zucchini squash', name_ru='цуккини', calories=16, proteins=1.2, fats=0.1, carbs=3.1, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='eggplant', name_ru='баклажан', calories=24, proteins=1.2, fats=0.1, carbs=4.5, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='pumpkin', name_ru='тыква', calories=22, proteins=1, fats=0.1, carbs=4.4, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='radish', name_ru='редис', calories=20, proteins=1.2, fats=0.1, carbs=3.4, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='radish daikon', name_ru='дайкон', calories=18, proteins=0.6, fats=0.1, carbs=4.1, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='beet', name_ru='свекла', calories=43, proteins=1.6, fats=0.2, carbs=8.8, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='celery root', name_ru='сельдерей корень', calories=42, proteins=1.5, fats=0.3, carbs=9, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='celery stalks', name_ru='сельдерей стебли', calories=16, proteins=0.7, fats=0.2, carbs=3, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='parsley root', name_ru='петрушка корень', calories=51, proteins=1.5, fats=0.6, carbs=10, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='parsnip', name_ru='пастернак', calories=75, proteins=1.4, fats=0.5, carbs=18, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='turnip', name_ru='репа', calories=30, proteins=1, fats=0.1, carbs=6, category_id=categories['vegetables'].id, default_portion=150),
            Food(name='radish black', name_ru='редька', calories=36, proteins=1.9, fats=0.2, carbs=6.7, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='horseradish', name_ru='хрен', calories=44, proteins=1.4, fats=0.4, carbs=8, category_id=categories['vegetables'].id, default_portion=30),
            Food(name='artichoke', name_ru='артишок', calories=47, proteins=3.3, fats=0.2, carbs=9, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='asparagus', name_ru='спаржа', calories=20, proteins=2.2, fats=0.1, carbs=3, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='spinach', name_ru='шпинат', calories=23, proteins=2.9, fats=0.4, carbs=3.6, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='sorrel', name_ru='щавель', calories=22, proteins=2, fats=0.7, carbs=3, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='lettuce', name_ru='салат листовой', calories=15, proteins=1.4, fats=0.2, carbs=2, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='arugula', name_ru='руккола', calories=25, proteins=2.6, fats=0.7, carbs=2, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='dill', name_ru='укроп', calories=40, proteins=2.5, fats=0.5, carbs=6, category_id=categories['vegetables'].id, default_portion=20),
            Food(name='parsley', name_ru='петрушка', calories=47, proteins=3.7, fats=0.8, carbs=7, category_id=categories['vegetables'].id, default_portion=20),
            Food(name='cilantro', name_ru='кинза', calories=23, proteins=2.1, fats=0.5, carbs=3, category_id=categories['vegetables'].id, default_portion=20),
            Food(name='basil', name_ru='базилик', calories=27, proteins=3.1, fats=0.6, carbs=2.7, category_id=categories['vegetables'].id, default_portion=20),
            Food(name='green peas', name_ru='горошек зеленый', calories=73, proteins=5, fats=0.2, carbs=13, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='corn', name_ru='кукуруза', calories=86, proteins=3.2, fats=1.2, carbs=19, category_id=categories['vegetables'].id, default_portion=100),
            Food(name='olives', name_ru='оливки', calories=145, proteins=1, fats=15, carbs=1, category_id=categories['vegetables'].id, default_portion=50),
            Food(name='olives black', name_ru='маслины', calories=150, proteins=1, fats=16, carbs=1, category_id=categories['vegetables'].id, default_portion=50),
            
            # Фрукты и ягоды
            Food(name='apple', name_ru='яблоко', calories=52, proteins=0.3, fats=0.2, carbs=11.4, category_id=categories['fruits'].id, default_portion=150),
            Food(name='apple green', name_ru='яблоко зеленое', calories=47, proteins=0.4, fats=0.4, carbs=10, category_id=categories['fruits'].id, default_portion=150),
            Food(name='apple red', name_ru='яблоко красное', calories=59, proteins=0.3, fats=0.2, carbs=14, category_id=categories['fruits'].id, default_portion=150),
            Food(name='banana', name_ru='банан', calories=95, proteins=1.5, fats=0.2, carbs=21.8, category_id=categories['fruits'].id, default_portion=150),
            Food(name='orange', name_ru='апельсин', calories=43, proteins=0.9, fats=0.2, carbs=8.1, category_id=categories['fruits'].id, default_portion=150),
            Food(name='mandarin', name_ru='мандарин', calories=38, proteins=0.8, fats=0.2, carbs=7.5, category_id=categories['fruits'].id, default_portion=100),
            Food(name='lemon', name_ru='лимон', calories=29, proteins=0.9, fats=0.3, carbs=3, category_id=categories['fruits'].id, default_portion=50),
            Food(name='lime', name_ru='лайм', calories=30, proteins=0.7, fats=0.2, carbs=7, category_id=categories['fruits'].id, default_portion=50),
            Food(name='grapefruit', name_ru='грейпфрут', calories=35, proteins=0.8, fats=0.1, carbs=6.5, category_id=categories['fruits'].id, default_portion=200),
            Food(name='pomelo', name_ru='помело', calories=38, proteins=0.8, fats=0, carbs=9, category_id=categories['fruits'].id, default_portion=200),
            Food(name='pear', name_ru='груша', calories=57, proteins=0.4, fats=0.3, carbs=13.1, category_id=categories['fruits'].id, default_portion=150),
            Food(name='quince', name_ru='айва', calories=57, proteins=0.4, fats=0.1, carbs=15, category_id=categories['fruits'].id, default_portion=150),
            Food(name='peach', name_ru='персик', calories=45, proteins=0.9, fats=0.1, carbs=9.5, category_id=categories['fruits'].id, default_portion=150),
            Food(name='nectarine', name_ru='нектарин', calories=48, proteins=1.1, fats=0.2, carbs=11, category_id=categories['fruits'].id, default_portion=150),
            Food(name='apricot', name_ru='абрикос', calories=44, proteins=0.9, fats=0.1, carbs=9, category_id=categories['fruits'].id, default_portion=100),
            Food(name='plum', name_ru='слива', calories=46, proteins=0.7, fats=0.3, carbs=10, category_id=categories['fruits'].id, default_portion=100),
            Food(name='cherry', name_ru='вишня', calories=52, proteins=0.8, fats=0.2, carbs=10.6, category_id=categories['fruits'].id, default_portion=100),
            Food(name='sweet cherry', name_ru='черешня', calories=50, proteins=1.1, fats=0.4, carbs=11, category_id=categories['fruits'].id, default_portion=100),
            Food(name='strawberry', name_ru='клубника', calories=32, proteins=0.7, fats=0.3, carbs=5.7, category_id=categories['fruits'].id, default_portion=150),
            Food(name='raspberry', name_ru='малина', calories=46, proteins=0.8, fats=0.5, carbs=8.3, category_id=categories['fruits'].id, default_portion=150),
            Food(name='blackberry', name_ru='ежевика', calories=43, proteins=1.4, fats=0.5, carbs=4.3, category_id=categories['fruits'].id, default_portion=150),
            Food(name='blueberry', name_ru='голубика', calories=57, proteins=0.7, fats=0.3, carbs=14, category_id=categories['fruits'].id, default_portion=150),
            Food(name='blueberry', name_ru='черника', calories=44, proteins=1.1, fats=0.6, carbs=7.6, category_id=categories['fruits'].id, default_portion=150),
            Food(name='cranberry', name_ru='клюква', calories=46, proteins=0.4, fats=0.1, carbs=12, category_id=categories['fruits'].id, default_portion=100),
            Food(name='lingonberry', name_ru='брусника', calories=46, proteins=0.7, fats=0.5, carbs=8, category_id=categories['fruits'].id, default_portion=100),
            Food(name='currant red', name_ru='смородина красная', calories=43, proteins=0.6, fats=0.2, carbs=7.7, category_id=categories['fruits'].id, default_portion=100),
            Food(name='currant black', name_ru='смородина черная', calories=44, proteins=1, fats=0.4, carbs=7.3, category_id=categories['fruits'].id, default_portion=100),
            Food(name='gooseberry', name_ru='крыжовник', calories=45, proteins=0.7, fats=0.2, carbs=9, category_id=categories['fruits'].id, default_portion=100),
            Food(name='grape', name_ru='виноград', calories=72, proteins=0.6, fats=0.6, carbs=15.4, category_id=categories['fruits'].id, default_portion=150),
            Food(name='raisins', name_ru='изюм', calories=299, proteins=2.9, fats=0.6, carbs=66, category_id=categories['fruits'].id, default_portion=30),
            Food(name='dried apricots', name_ru='курага', calories=241, proteins=3.4, fats=0.5, carbs=55, category_id=categories['fruits'].id, default_portion=30),
            Food(name='prunes', name_ru='чернослив', calories=240, proteins=2.3, fats=0.7, carbs=57, category_id=categories['fruits'].id, default_portion=30),
            Food(name='dates', name_ru='финики', calories=282, proteins=2.5, fats=0.5, carbs=65, category_id=categories['fruits'].id, default_portion=30),
            Food(name='figs', name_ru='инжир', calories=74, proteins=0.8, fats=0.3, carbs=19, category_id=categories['fruits'].id, default_portion=50),
            Food(name='persimmon', name_ru='хурма', calories=67, proteins=0.5, fats=0.4, carbs=15, category_id=categories['fruits'].id, default_portion=150),
            Food(name='pomegranate', name_ru='гранат', calories=72, proteins=0.7, fats=0.6, carbs=14.5, category_id=categories['fruits'].id, default_portion=150),
            Food(name='kiwi', name_ru='киви', calories=47, proteins=0.8, fats=0.4, carbs=8.1, category_id=categories['fruits'].id, default_portion=100),
            Food(name='pineapple', name_ru='ананас', calories=49, proteins=0.4, fats=0.2, carbs=11.5, category_id=categories['fruits'].id, default_portion=150),
            Food(name='mango', name_ru='манго', calories=60, proteins=0.8, fats=0.4, carbs=13, category_id=categories['fruits'].id, default_portion=150),
            Food(name='avocado', name_ru='авокадо', calories=160, proteins=2, fats=15, carbs=6, category_id=categories['fruits'].id, default_portion=100),
            Food(name='papaya', name_ru='папайя', calories=43, proteins=0.5, fats=0.3, carbs=11, category_id=categories['fruits'].id, default_portion=150),
            Food(name='feijoa', name_ru='фейхоа', calories=55, proteins=1, fats=0.6, carbs=13, category_id=categories['fruits'].id, default_portion=100),
            Food(name='coconut', name_ru='кокос', calories=354, proteins=3.3, fats=34, carbs=15, category_id=categories['fruits'].id, default_portion=100),
            
            # Крупы и злаки
            Food(name='buckwheat', name_ru='гречка', calories=343, proteins=13, fats=3.3, carbs=68, category_id=categories['grains'].id, default_portion=200),
            Food(name='buckwheat cooked', name_ru='гречка вареная', calories=110, proteins=4, fats=1, carbs=21, category_id=categories['grains'].id, default_portion=200),
            Food(name='rice white', name_ru='рис белый', calories=344, proteins=6.7, fats=0.7, carbs=78, category_id=categories['grains'].id, default_portion=200),
            Food(name='rice white cooked', name_ru='рис белый вареный', calories=116, proteins=2.2, fats=0.2, carbs=24, category_id=categories['grains'].id, default_portion=200),
            Food(name='rice brown', name_ru='рис коричневый', calories=337, proteins=7.4, fats=1.8, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='rice brown cooked', name_ru='рис коричневый вареный', calories=123, proteins=2.7, fats=0.4, carbs=26, category_id=categories['grains'].id, default_portion=200),
            Food(name='rice wild', name_ru='рис дикий', calories=357, proteins=15, fats=1.1, carbs=75, category_id=categories['grains'].id, default_portion=200),
            Food(name='oatmeal', name_ru='овсянка', calories=366, proteins=12, fats=6, carbs=62, category_id=categories['grains'].id, default_portion=200),
            Food(name='oatmeal cooked', name_ru='овсянка вареная', calories=88, proteins=3, fats=1.7, carbs=15, category_id=categories['grains'].id, default_portion=200),
            Food(name='oatmeal instant', name_ru='овсянка быстрого приготовления', calories=360, proteins=11, fats=5, carbs=70, category_id=categories['grains'].id, default_portion=200),
            Food(name='muesli', name_ru='мюсли', calories=350, proteins=9, fats=6, carbs=65, category_id=categories['grains'].id, default_portion=100),
            Food(name='pasta', name_ru='макароны', calories=350, proteins=12, fats=1.5, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='pasta cooked', name_ru='макароны вареные', calories=135, proteins=4.5, fats=0.5, carbs=28, category_id=categories['grains'].id, default_portion=200),
            Food(name='spaghetti', name_ru='спагетти', calories=350, proteins=12, fats=1.5, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='noodles', name_ru='лапша', calories=350, proteins=11, fats=1.5, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='vermicelli', name_ru='вермишель', calories=350, proteins=11, fats=1.5, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='millet', name_ru='пшено', calories=348, proteins=11.5, fats=3.3, carbs=69, category_id=categories['grains'].id, default_portion=200),
            Food(name='millet cooked', name_ru='пшенная каша', calories=110, proteins=3.5, fats=1, carbs=22, category_id=categories['grains'].id, default_portion=200),
            Food(name='pearl barley', name_ru='перловка', calories=346, proteins=9.3, fats=1.1, carbs=73, category_id=categories['grains'].id, default_portion=200),
            Food(name='pearl barley cooked', name_ru='перловая каша', calories=123, proteins=3.5, fats=0.4, carbs=28, category_id=categories['grains'].id, default_portion=200),
            Food(name='barley', name_ru='ячневая крупа', calories=324, proteins=10, fats=1.3, carbs=66, category_id=categories['grains'].id, default_portion=200),
            Food(name='corn grits', name_ru='кукурузная крупа', calories=337, proteins=8.3, fats=1.2, carbs=75, category_id=categories['grains'].id, default_portion=200),
            Food(name='corn flakes', name_ru='кукурузные хлопья', calories=379, proteins=7, fats=1.2, carbs=85, category_id=categories['grains'].id, default_portion=100),
            Food(name='semolina', name_ru='манка', calories=333, proteins=10.3, fats=1, carbs=70, category_id=categories['grains'].id, default_portion=200),
            Food(name='semolina cooked', name_ru='манная каша', calories=100, proteins=3, fats=0.3, carbs=20, category_id=categories['grains'].id, default_portion=200),
            Food(name='couscous', name_ru='кускус', calories=350, proteins=12.8, fats=0.6, carbs=72, category_id=categories['grains'].id, default_portion=200),
            Food(name='bulgur', name_ru='булгур', calories=342, proteins=12.3, fats=1.3, carbs=63, category_id=categories['grains'].id, default_portion=200),
            Food(name='quinoa', name_ru='киноа', calories=368, proteins=14, fats=6, carbs=64, category_id=categories['grains'].id, default_portion=200),
            Food(name='amaranth', name_ru='амарант', calories=371, proteins=14, fats=7, carbs=65, category_id=categories['grains'].id, default_portion=200),
            
            # Хлеб и выпечка
            Food(name='bread white', name_ru='хлеб белый', calories=265, proteins=9, fats=3.2, carbs=49, category_id=categories['bakery'].id, default_portion=30),
            Food(name='bread rye', name_ru='хлеб ржаной', calories=200, proteins=6.6, fats=1.2, carbs=34, category_id=categories['bakery'].id, default_portion=30),
            Food(name='bread rye-wheat', name_ru='хлеб ржано-пшеничный', calories=240, proteins=7.5, fats=1.5, carbs=45, category_id=categories['bakery'].id, default_portion=30),
            Food(name='bread whole grain', name_ru='хлеб цельнозерновой', calories=250, proteins=8, fats=3, carbs=45, category_id=categories['bakery'].id, default_portion=30),
            Food(name='bread bran', name_ru='хлеб с отрубями', calories=230, proteins=8, fats=2, carbs=40, category_id=categories['bakery'].id, default_portion=30),
            Food(name='bread corn', name_ru='хлеб кукурузный', calories=270, proteins=7, fats=3, carbs=52, category_id=categories['bakery'].id, default_portion=30),
            Food(name='loaf', name_ru='батон', calories=260, proteins=7.5, fats=2.9, carbs=51, category_id=categories['bakery'].id, default_portion=30),
            Food(name='loaf sliced', name_ru='батон нарезной', calories=260, proteins=7.5, fats=2.9, carbs=51, category_id=categories['bakery'].id, default_portion=30),
            Food(name='baguette', name_ru='багет', calories=270, proteins=9, fats=2, carbs=55, category_id=categories['bakery'].id, default_portion=50),
            Food(name='ciabatta', name_ru='чиабатта', calories=260, proteins=8, fats=1.5, carbs=52, category_id=categories['bakery'].id, default_portion=50),
            Food(name='lavash', name_ru='лаваш', calories=236, proteins=7.5, fats=1, carbs=48, category_id=categories['bakery'].id, default_portion=50),
            Food(name='pita', name_ru='пита', calories=275, proteins=8, fats=1, carbs=55, category_id=categories['bakery'].id, default_portion=50),
            Food(name='bun', name_ru='булочка', calories=300, proteins=8, fats=7, carbs=52, category_id=categories['bakery'].id, default_portion=60),
            Food(name='bun butter', name_ru='булочка сдобная', calories=330, proteins=7, fats=9, carbs=55, category_id=categories['bakery'].id, default_portion=60),
            Food(name='croissant', name_ru='круассан', calories=406, proteins=8, fats=21, carbs=45, category_id=categories['bakery'].id, default_portion=60),
            Food(name='bagel', name_ru='бублик', calories=280, proteins=9, fats=2, carbs=55, category_id=categories['bakery'].id, default_portion=50),
            Food(name='drying', name_ru='сушка', calories=330, proteins=11, fats=1, carbs=73, category_id=categories['bakery'].id, default_portion=20),
            Food(name='crackers', name_ru='сухари', calories=330, proteins=11, fats=2, carbs=70, category_id=categories['bakery'].id, default_portion=30),
            Food(name='breadcrumbs', name_ru='панировочные сухари', calories=350, proteins=12, fats=2, carbs=72, category_id=categories['bakery'].id, default_portion=20),
            Food(name='biscuits', name_ru='бисквит', calories=300, proteins=8, fats=5, carbs=55, category_id=categories['bakery'].id, default_portion=50),
            Food(name='gingerbread', name_ru='пряники', calories=350, proteins=5, fats=3, carbs=78, category_id=categories['bakery'].id, default_portion=50),
            Food(name='waffles', name_ru='вафли', calories=520, proteins=8, fats=28, carbs=60, category_id=categories['bakery'].id, default_portion=30),
            Food(name='cookies', name_ru='печенье', calories=450, proteins=7, fats=15, carbs=70, category_id=categories['bakery'].id, default_portion=30),
            Food(name='cookies oatmeal', name_ru='овсяное печенье', calories=420, proteins=8, fats=12, carbs=70, category_id=categories['bakery'].id, default_portion=30),
            Food(name='crackers salty', name_ru='крекеры', calories=400, proteins=8, fats=10, carbs=70, category_id=categories['bakery'].id, default_portion=30),
            Food(name='rusk', name_ru='сухарь', calories=330, proteins=11, fats=2, carbs=70, category_id=categories['bakery'].id, default_portion=20),
            
            # Масла и жиры
            Food(name='oil sunflower', name_ru='масло подсолнечное', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil olive', name_ru='масло оливковое', calories=898, proteins=0, fats=99.8, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil olive extra virgin', name_ru='масло оливковое extra virgin', calories=898, proteins=0, fats=99.8, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil corn', name_ru='масло кукурузное', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil soybean', name_ru='масло соевое', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil rapeseed', name_ru='масло рапсовое', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil flaxseed', name_ru='льняное масло', calories=898, proteins=0, fats=99.8, carbs=0, category_id=categories['fats'].id, default_portion=10),
            Food(name='oil sesame', name_ru='кунжутное масло', calories=899, proteins=0, fats=99.9, carbs=0, category_id=categories['fats'].id, default_portion=10),
            Food(name='oil coconut', name_ru='кокосовое масло', calories=862, proteins=0, fats=99, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='oil palm', name_ru='пальмовое масло', calories=884, proteins=0, fats=99, carbs=0, category_id=categories['fats'].id, default_portion=15),
            Food(name='mayonnaise', name_ru='майонез', calories=680, proteins=2, fats=75, carbs=3, category_id=categories['fats'].id, default_portion=20),
            Food(name='mayonnaise light', name_ru='майонез легкий', calories=350, proteins=1, fats=35, carbs=5, category_id=categories['fats'].id, default_portion=20),
            Food(name='margarine', name_ru='маргарин', calories=720, proteins=0.5, fats=80, carbs=1, category_id=categories['fats'].id, default_portion=15),
            Food(name='spread', name_ru='спред', calories=600, proteins=0.5, fats=65, carbs=1, category_id=categories['fats'].id, default_portion=15),
            Food(name='lard', name_ru='жир животный', calories=900, proteins=0, fats=99, carbs=0, category_id=categories['fats'].id, default_portion=15),
            
            # Орехи и семена
            Food(name='walnuts', name_ru='грецкие орехи', calories=654, proteins=15, fats=65, carbs=14, category_id=categories['nuts'].id, default_portion=30),
            Food(name='almonds', name_ru='миндаль', calories=609, proteins=19, fats=54, carbs=13, category_id=categories['nuts'].id, default_portion=30),
            Food(name='hazelnuts', name_ru='фундук', calories=651, proteins=15, fats=62, carbs=9, category_id=categories['nuts'].id, default_portion=30),
            Food(name='cashews', name_ru='кешью', calories=600, proteins=18, fats=48, carbs=27, category_id=categories['nuts'].id, default_portion=30),
            Food(name='peanuts', name_ru='арахис', calories=552, proteins=26, fats=45, carbs=10, category_id=categories['nuts'].id, default_portion=30),
            Food(name='peanuts salted', name_ru='арахис соленый', calories=580, proteins=24, fats=48, carbs=12, category_id=categories['nuts'].id, default_portion=30),
            Food(name='pistachios', name_ru='фисташки', calories=560, proteins=20, fats=45, carbs=17, category_id=categories['nuts'].id, default_portion=30),
            Food(name='pine nuts', name_ru='кедровые орехи', calories=673, proteins=14, fats=68, carbs=13, category_id=categories['nuts'].id, default_portion=30),
            Food(name='brazil nut', name_ru='бразильский орех', calories=659, proteins=14, fats=67, carbs=12, category_id=categories['nuts'].id, default_portion=30),
            Food(name='pecan', name_ru='пекан', calories=691, proteins=9, fats=72, carbs=14, category_id=categories['nuts'].id, default_portion=30),
            Food(name='macadamia', name_ru='макадамия', calories=718, proteins=8, fats=76, carbs=14, category_id=categories['nuts'].id, default_portion=30),
            Food(name='coconut flakes', name_ru='кокосовая стружка', calories=592, proteins=6, fats=53, carbs=27, category_id=categories['nuts'].id, default_portion=20),
            Food(name='sesame', name_ru='кунжут', calories=573, proteins=18, fats=50, carbs=23, category_id=categories['nuts'].id, default_portion=20),
            Food(name='poppy', name_ru='мак', calories=556, proteins=18, fats=47, carbs=15, category_id=categories['nuts'].id, default_portion=10),
            Food(name='flax seeds', name_ru='семена льна', calories=534, proteins=18, fats=42, carbs=29, category_id=categories['nuts'].id, default_portion=20),
            Food(name='chia seeds', name_ru='семена чиа', calories=486, proteins=16, fats=31, carbs=42, category_id=categories['nuts'].id, default_portion=20),
            Food(name='sunflower seeds', name_ru='семечки подсолнуха', calories=584, proteins=21, fats=51, carbs=12, category_id=categories['nuts'].id, default_portion=30),
            Food(name='pumpkin seeds', name_ru='семечки тыквенные', calories=559, proteins=30, fats=49, carbs=5, category_id=categories['nuts'].id, default_portion=30),
            Food(name='nut paste', name_ru='ореховая паста', calories=600, proteins=15, fats=50, carbs=20, category_id=categories['nuts'].id, default_portion=20),
            Food(name='peanut butter', name_ru='арахисовая паста', calories=588, proteins=25, fats=50, carbs=12, category_id=categories['nuts'].id, default_portion=20),
            Food(name='nutella', name_ru='нутелла', calories=530, proteins=6, fats=30, carbs=57, category_id=categories['nuts'].id, default_portion=20),
            
            # Напитки
            Food(name='coffee', name_ru='кофе', calories=2, proteins=0.1, fats=0, carbs=0.3, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='coffee instant', name_ru='кофе растворимый', calories=5, proteins=0.2, fats=0, carbs=1, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='coffee espresso', name_ru='эспрессо', calories=2, proteins=0.1, fats=0, carbs=0.3, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='coffee cappuccino', name_ru='капучино', calories=50, proteins=2, fats=2, carbs=5, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='coffee latte', name_ru='латте', calories=70, proteins=3, fats=3, carbs=7, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='coffee americano', name_ru='американо', calories=5, proteins=0.2, fats=0, carbs=1, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='tea black', name_ru='чай черный', calories=1, proteins=0, fats=0, carbs=0.3, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='tea green', name_ru='чай зеленый', calories=1, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='tea herbal', name_ru='травяной чай', calories=1, proteins=0, fats=0, carbs=0.2, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='tea fruit', name_ru='фруктовый чай', calories=2, proteins=0, fats=0, carbs=0.5, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='cocoa', name_ru='какао', calories=30, proteins=1.5, fats=1, carbs=4, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='sugar', name_ru='сахар', calories=387, proteins=0, fats=0, carbs=99.8, category_id=categories['sweets'].id, default_portion=7),
            Food(name='sugar brown', name_ru='сахар коричневый', calories=380, proteins=0, fats=0, carbs=98, category_id=categories['sweets'].id, default_portion=7),
            Food(name='honey', name_ru='мед', calories=329, proteins=0.8, fats=0, carbs=80, category_id=categories['sweets'].id, default_portion=20),
            Food(name='honey buckwheat', name_ru='мед гречишный', calories=340, proteins=1, fats=0, carbs=82, category_id=categories['sweets'].id, default_portion=20),
            Food(name='juice orange', name_ru='сок апельсиновый', calories=45, proteins=0.7, fats=0.2, carbs=10.4, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='juice apple', name_ru='сок яблочный', calories=46, proteins=0.5, fats=0.1, carbs=11, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='juice grape', name_ru='сок виноградный', calories=70, proteins=0.3, fats=0, carbs=17, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='juice pomegranate', name_ru='сок гранатовый', calories=64, proteins=0.3, fats=0, carbs=14, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='juice tomato', name_ru='сок томатный', calories=20, proteins=1, fats=0, carbs=4, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='nectar peach', name_ru='нектар персиковый', calories=50, proteins=0.3, fats=0, carbs=12, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='compote', name_ru='компот', calories=50, proteins=0.2, fats=0, carbs=12, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='kissel', name_ru='кисель', calories=55, proteins=0.1, fats=0, carbs=13, category_id=categories['drinks'].id, is_liquid=True, default_portion=200),
            Food(name='lemonade', name_ru='лимонад', calories=40, proteins=0, fats=0, carbs=10, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='cola', name_ru='кола', calories=42, proteins=0, fats=0, carbs=10.4, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='sprite', name_ru='спрайт', calories=40, proteins=0, fats=0, carbs=10, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='fanta', name_ru='фанта', calories=48, proteins=0, fats=0, carbs=12, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='mineral water', name_ru='минеральная вода', calories=0, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='energy drink', name_ru='энергетик', calories=45, proteins=0, fats=0, carbs=11, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='kvass', name_ru='квас', calories=30, proteins=0.2, fats=0, carbs=7, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
            Food(name='beer', name_ru='пиво', calories=45, proteins=0.5, fats=0, carbs=3.5, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='wine dry', name_ru='вино сухое', calories=85, proteins=0.1, fats=0, carbs=0.6, category_id=categories['drinks'].id, is_liquid=True, default_portion=150),
            Food(name='wine semi-sweet', name_ru='вино полусладкое', calories=95, proteins=0.1, fats=0, carbs=3, category_id=categories['drinks'].id, is_liquid=True, default_portion=150),
            Food(name='champagne', name_ru='шампанское', calories=88, proteins=0.2, fats=0, carbs=5, category_id=categories['drinks'].id, is_liquid=True, default_portion=150),
            Food(name='vodka', name_ru='водка', calories=235, proteins=0, fats=0, carbs=0.1, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='cognac', name_ru='коньяк', calories=240, proteins=0, fats=0, carbs=1.5, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='whiskey', name_ru='виски', calories=250, proteins=0, fats=0, carbs=0.1, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            
            # Сладости
            Food(name='chocolate dark', name_ru='шоколад темный', calories=550, proteins=6, fats=35, carbs=50, category_id=categories['sweets'].id, default_portion=20),
            Food(name='chocolate dark 70%', name_ru='шоколад темный 70%', calories=570, proteins=8, fats=40, carbs=30, category_id=categories['sweets'].id, default_portion=20),
            Food(name='chocolate dark 80%', name_ru='шоколад темный 80%', calories=590, proteins=9, fats=45, carbs=20, category_id=categories['sweets'].id, default_portion=20),
            Food(name='chocolate milk', name_ru='шоколад молочный', calories=550, proteins=7, fats=32, carbs=55, category_id=categories['sweets'].id, default_portion=20),
            Food(name='chocolate white', name_ru='шоколад белый', calories=550, proteins=6, fats=33, carbs=58, category_id=categories['sweets'].id, default_portion=20),
            Food(name='candies chocolate', name_ru='конфеты шоколадные', calories=550, proteins=5, fats=35, carbs=55, category_id=categories['sweets'].id, default_portion=20),
            Food(name='candies caramel', name_ru='конфеты карамель', calories=380, proteins=1, fats=5, carbs=85, category_id=categories['sweets'].id, default_portion=15),
            Food(name='candies lollipops', name_ru='леденцы', calories=380, proteins=0, fats=0, carbs=95, category_id=categories['sweets'].id, default_portion=10),
            Food(name='candies iris', name_ru='ирис', calories=400, proteins=3, fats=8, carbs=80, category_id=categories['sweets'].id, default_portion=15),
            Food(name='marmalade', name_ru='мармелад', calories=330, proteins=0.2, fats=0, carbs=80, category_id=categories['sweets'].id, default_portion=30),
            Food(name='marshmallow', name_ru='зефир', calories=320, proteins=0.8, fats=0, carbs=80, category_id=categories['sweets'].id, default_portion=30),
            Food(name='pastila', name_ru='пастила', calories=320, proteins=0.5, fats=0, carbs=80, category_id=categories['sweets'].id, default_portion=30),
            Food(name='halva', name_ru='халва', calories=520, proteins=12, fats=30, carbs=50, category_id=categories['sweets'].id, default_portion=30),
            Food(name='halva sunflower', name_ru='халва подсолнечная', calories=520, proteins=12, fats=30, carbs=50, category_id=categories['sweets'].id, default_portion=30),
            Food(name='kazinaki', name_ru='козинаки', calories=500, proteins=15, fats=30, carbs=45, category_id=categories['sweets'].id, default_portion=30),
            Food(name='cake', name_ru='торт', calories=350, proteins=5, fats=15, carbs=50, category_id=categories['sweets'].id, default_portion=150),
            Food(name='cake cream', name_ru='пирожное', calories=400, proteins=5, fats=20, carbs=50, category_id=categories['sweets'].id, default_portion=100),
            Food(name='cake Napoleon', name_ru='наполеон', calories=400, proteins=6, fats=20, carbs=48, category_id=categories['sweets'].id, default_portion=150),
            Food(name='cake honey', name_ru='медовик', calories=380, proteins=5, fats=18, carbs=50, category_id=categories['sweets'].id, default_portion=150),
            Food(name='eclair', name_ru='эклер', calories=350, proteins=5, fats=18, carbs=40, category_id=categories['sweets'].id, default_portion=80),
            Food(name='profiterole', name_ru='профитроль', calories=300, proteins=5, fats=15, carbs=35, category_id=categories['sweets'].id, default_portion=50),
            Food(name='biscuit roll', name_ru='рулет бисквитный', calories=350, proteins=5, fats=10, carbs=60, category_id=categories['sweets'].id, default_portion=100),
            Food(name='jam', name_ru='варенье', calories=250, proteins=0.3, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='preserves', name_ru='джем', calories=260, proteins=0.3, fats=0.1, carbs=65, category_id=categories['sweets'].id, default_portion=20),
            Food(name='condensed milk', name_ru='сгущенка', calories=330, proteins=7, fats=8, carbs=55, category_id=categories['sweets'].id, default_portion=30),
            Food(name='condensed milk boiled', name_ru='сгущенка вареная', calories=350, proteins=6, fats=9, carbs=60, category_id=categories['sweets'].id, default_portion=30),
            
            # Соусы и приправы
            Food(name='ketchup', name_ru='кетчуп', calories=100, proteins=1.5, fats=0.5, carbs=22, category_id=categories['sauces'].id, default_portion=20),
            Food(name='mustard', name_ru='горчица', calories=150, proteins=7, fats=10, carbs=8, category_id=categories['sauces'].id, default_portion=10),
            Food(name='soy sauce', name_ru='соевый соус', calories=70, proteins=7, fats=0, carbs=8, category_id=categories['sauces'].id, is_liquid=True, default_portion=15),
            Food(name='teriyaki sauce', name_ru='соус терияки', calories=100, proteins=4, fats=0, carbs=20, category_id=categories['sauces'].id, is_liquid=True, default_portion=20),
            Food(name='barbecue sauce', name_ru='соус барбекю', calories=150, proteins=1, fats=5, carbs=25, category_id=categories['sauces'].id, default_portion=20),
            Food(name='tartar sauce', name_ru='соус тартар', calories=350, proteins=1, fats=35, carbs=8, category_id=categories['sauces'].id, default_portion=20),
            Food(name='cheese sauce', name_ru='сырный соус', calories=300, proteins=5, fats=25, carbs=10, category_id=categories['sauces'].id, default_portion=20),
            Food(name='pesto', name_ru='песто', calories=500, proteins=5, fats=50, carbs=8, category_id=categories['sauces'].id, default_portion=20),
            Food(name='adjika', name_ru='аджика', calories=60, proteins=2, fats=2, carbs=8, category_id=categories['sauces'].id, default_portion=15),
            Food(name='horseradish sauce', name_ru='хрен', calories=50, proteins=1.5, fats=0.5, carbs=8, category_id=categories['sauces'].id, default_portion=15),
            Food(name='vinegar', name_ru='уксус', calories=20, proteins=0, fats=0, carbs=1, category_id=categories['sauces'].id, is_liquid=True, default_portion=10),
            Food(name='salt', name_ru='соль', calories=0, proteins=0, fats=0, carbs=0, category_id=categories['sauces'].id, default_portion=2),
            Food(name='pepper', name_ru='перец', calories=20, proteins=1, fats=0.5, carbs=4, category_id=categories['sauces'].id, default_portion=1),
            Food(name='bay leaf', name_ru='лавровый лист', calories=10, proteins=0.5, fats=0.2, carbs=2, category_id=categories['sauces'].id, default_portion=1),
            
            # Бобовые
            Food(name='beans', name_ru='фасоль', calories=132, proteins=8, fats=0.5, carbs=21, category_id=categories['legumes'].id, default_portion=150),
            Food(name='beans red', name_ru='фасоль красная', calories=130, proteins=8, fats=0.5, carbs=20, category_id=categories['legumes'].id, default_portion=150),
            Food(name='beans white', name_ru='фасоль белая', calories=140, proteins=8, fats=0.5, carbs=22, category_id=categories['legumes'].id, default_portion=150),
            Food(name='beans green', name_ru='фасоль стручковая', calories=30, proteins=2, fats=0.2, carbs=5, category_id=categories['legumes'].id, default_portion=150),
            Food(name='lentils', name_ru='чечевица', calories=116, proteins=9, fats=0.4, carbs=20, category_id=categories['legumes'].id, default_portion=150),
            Food(name='lentils red', name_ru='чечевица красная', calories=110, proteins=8, fats=0.4, carbs=19, category_id=categories['legumes'].id, default_portion=150),
            Food(name='lentils green', name_ru='чечевица зеленая', calories=120, proteins=9, fats=0.5, carbs=21, category_id=categories['legumes'].id, default_portion=150),
            Food(name='peas', name_ru='горох', calories=118, proteins=8, fats=0.4, carbs=20, category_id=categories['legumes'].id, default_portion=150),
            Food(name='peas split', name_ru='горох колотый', calories=118, proteins=8, fats=0.4, carbs=20, category_id=categories['legumes'].id, default_portion=150),
            Food(name='chickpeas', name_ru='нут', calories=164, proteins=9, fats=2.6, carbs=27, category_id=categories['legumes'].id, default_portion=150),
            Food(name='soy', name_ru='соя', calories=130, proteins=12, fats=6, carbs=8, category_id=categories['legumes'].id, default_portion=100),
            Food(name='tofu', name_ru='тофу', calories=76, proteins=8, fats=4, carbs=2, category_id=categories['legumes'].id, default_portion=100),
            
            # Грибы
            Food(name='mushrooms champignons', name_ru='шампиньоны', calories=27, proteins=4.3, fats=1, carbs=0.5, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms oyster', name_ru='вешенки', calories=33, proteins=3.3, fats=0.4, carbs=4, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms porcini', name_ru='белые грибы', calories=34, proteins=3.7, fats=1.7, carbs=1.1, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms aspen', name_ru='подосиновики', calories=22, proteins=3.3, fats=0.5, carbs=1.2, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms birch', name_ru='подберезовики', calories=20, proteins=2.3, fats=0.9, carbs=1.2, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms honey', name_ru='опята', calories=22, proteins=2.2, fats=1.2, carbs=0.5, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms chanterelles', name_ru='лисички', calories=20, proteins=1.5, fats=1, carbs=1, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms milk', name_ru='грузди', calories=18, proteins=1.8, fats=0.5, carbs=1, category_id=categories['mushrooms'].id, default_portion=100),
            Food(name='mushrooms dried', name_ru='грибы сушеные', calories=280, proteins=30, fats=5, carbs=25, category_id=categories['mushrooms'].id, default_portion=30),
            Food(name='mushrooms pickled', name_ru='грибы маринованные', calories=25, proteins=2, fats=0.5, carbs=3, category_id=categories['mushrooms'].id, default_portion=100),
            
            # Супы
            Food(name='borscht', name_ru='борщ', calories=50, proteins=2, fats=2, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='borscht with meat', name_ru='борщ с мясом', calories=80, proteins=4, fats=4, carbs=7, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='borscht green', name_ru='щи зеленые', calories=45, proteins=2, fats=1.5, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='shchi', name_ru='щи', calories=45, proteins=2, fats=1.5, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='shchi sour', name_ru='щи кислые', calories=50, proteins=2, fats=2, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup chicken', name_ru='суп куриный', calories=40, proteins=3, fats=2, carbs=3, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup noodle', name_ru='суп с лапшой', calories=45, proteins=2, fats=1.5, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup pea', name_ru='суп гороховый', calories=65, proteins=4, fats=2, carbs=8, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup mushroom', name_ru='суп грибной', calories=40, proteins=2, fats=1.5, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup fish', name_ru='уха', calories=40, proteins=3, fats=1, carbs=4, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup tomato', name_ru='суп томатный', calories=35, proteins=1, fats=1, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup pumpkin', name_ru='суп тыквенный', calories=40, proteins=1, fats=1, carbs=7, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='soup cream', name_ru='суп-пюре', calories=60, proteins=2, fats=3, carbs=7, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='solyanka', name_ru='солянка', calories=90, proteins=5, fats=5, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='rassolnik', name_ru='рассольник', calories=55, proteins=2, fats=2, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='okroshka', name_ru='окрошка', calories=60, proteins=3, fats=3, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='okroshka kefir', name_ru='окрошка на кефире', calories=55, proteins=3, fats=2, carbs=5, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='cold soup', name_ru='холодник', calories=40, proteins=2, fats=1, carbs=6, category_id=categories['soups'].id, is_liquid=True, default_portion=300),
            Food(name='broth chicken', name_ru='бульон куриный', calories=20, proteins=2, fats=1, carbs=1, category_id=categories['soups'].id, is_liquid=True, default_portion=250),
            Food(name='broth meat', name_ru='бульон мясной', calories=25, proteins=2, fats=1.5, carbs=1, category_id=categories['soups'].id, is_liquid=True, default_portion=250),
            
            # Шашлык и гриль
            Food(name='shashlik pork', name_ru='шашлык из свинины', calories=280, proteins=15, fats=24, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='shashlik beef', name_ru='шашлык из говядины', calories=220, proteins=18, fats=16, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='shashlik lamb', name_ru='шашлык из баранины', calories=250, proteins=16, fats=20, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='shashlik chicken', name_ru='шашлык из курицы', calories=160, proteins=22, fats=7, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='shashlik turkey', name_ru='шашлык из индейки', calories=150, proteins=24, fats=5, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='shashlik salmon', name_ru='шашлык из лосося', calories=200, proteins=18, fats=13, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='kebab', name_ru='кебаб', calories=250, proteins=16, fats=19, carbs=2, category_id=categories['bbq'].id, default_portion=200),
            Food(name='lula kebab', name_ru='люля-кебаб', calories=280, proteins=15, fats=23, carbs=2, category_id=categories['bbq'].id, default_portion=200),
            Food(name='grilled chicken', name_ru='курица гриль', calories=200, proteins=20, fats=12, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            Food(name='grilled vegetables', name_ru='овощи гриль', calories=80, proteins=2, fats=4, carbs=10, category_id=categories['bbq'].id, default_portion=200),
            Food(name='grilled fish', name_ru='рыба на гриле', calories=150, proteins=18, fats=8, carbs=1, category_id=categories['bbq'].id, default_portion=200),
            
            # Консервы
            Food(name='canned fish', name_ru='рыбные консервы', calories=200, proteins=18, fats=14, carbs=0, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned saury', name_ru='сайра консервированная', calories=230, proteins=18, fats=17, carbs=0, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned sardine', name_ru='сардина консервированная', calories=210, proteins=20, fats=14, carbs=0, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned tuna', name_ru='тунец консервированный', calories=120, proteins=23, fats=3, carbs=0, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned mackerel', name_ru='скумбрия консервированная', calories=200, proteins=18, fats=14, carbs=0, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned meat', name_ru='мясные консервы', calories=250, proteins=15, fats=20, carbs=1, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned stew', name_ru='тушенка', calories=220, proteins=16, fats=17, carbs=1, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned peas', name_ru='горошек консервированный', calories=55, proteins=3, fats=0.5, carbs=10, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned corn', name_ru='кукуруза консервированная', calories=60, proteins=2, fats=1, carbs=12, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned beans', name_ru='фасоль консервированная', calories=90, proteins=6, fats=0.5, carbs=16, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned olives', name_ru='оливки консервированные', calories=145, proteins=1, fats=15, carbs=1, category_id=categories['canned'].id, default_portion=50),
            Food(name='canned pineapple', name_ru='ананас консервированный', calories=80, proteins=0.5, fats=0.2, carbs=20, category_id=categories['canned'].id, default_portion=100),
            Food(name='canned peaches', name_ru='персики консервированные', calories=70, proteins=0.5, fats=0.1, carbs=17, category_id=categories['canned'].id, default_portion=100),
            
            # Фастфуд
            Food(name='pizza', name_ru='пицца', calories=266, proteins=12, fats=10, carbs=33, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='pizza margherita', name_ru='пицца маргарита', calories=250, proteins=11, fats=8, carbs=34, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='pizza pepperoni', name_ru='пицца пепперони', calories=300, proteins=13, fats=14, carbs=32, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='pizza four cheese', name_ru='пицца четыре сыра', calories=280, proteins=12, fats=12, carbs=33, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='pizza hawaiian', name_ru='пицца гавайская', calories=260, proteins=11, fats=9, carbs=35, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='burger', name_ru='бургер', calories=295, proteins=16, fats=15, carbs=25, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='cheeseburger', name_ru='чизбургер', calories=320, proteins=17, fats=17, carbs=26, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='double burger', name_ru='двойной бургер', calories=450, proteins=25, fats=25, carbs=30, category_id=categories['fastfood'].id, default_portion=250),
                       Food(name='chicken burger', name_ru='чизбургер куриный', calories=280, proteins=18, fats=12, carbs=27, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='fish burger', name_ru='фишбургер', calories=260, proteins=14, fats=11, carbs=28, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='fries', name_ru='картошка фри', calories=312, proteins=3.4, fats=15, carbs=38, category_id=categories['fastfood'].id, default_portion=150),
            Food(name='nuggets', name_ru='наггетсы', calories=300, proteins=15, fats=20, carbs=15, category_id=categories['fastfood'].id, default_portion=100),
            Food(name='chicken wings', name_ru='куриные крылышки', calories=250, proteins=18, fats=18, carbs=5, category_id=categories['fastfood'].id, default_portion=150),
            Food(name='hot dog', name_ru='хот-дог', calories=250, proteins=9, fats=15, carbs=22, category_id=categories['fastfood'].id, default_portion=150),
            Food(name='shawarma', name_ru='шаурма', calories=220, proteins=12, fats=10, carbs=20, category_id=categories['fastfood'].id, default_portion=300),
            Food(name='shawarma chicken', name_ru='шаурма с курицей', calories=200, proteins=14, fats=8, carbs=18, category_id=categories['fastfood'].id, default_portion=300),
            Food(name='doner', name_ru='донер', calories=230, proteins=13, fats=11, carbs=21, category_id=categories['fastfood'].id, default_portion=300),
            Food(name='taco', name_ru='тако', calories=210, proteins=10, fats=11, carbs=20, category_id=categories['fastfood'].id, default_portion=150),
            Food(name='burrito', name_ru='буррито', calories=250, proteins=12, fats=10, carbs=28, category_id=categories['fastfood'].id, default_portion=300),
            Food(name='quesadilla', name_ru='кесадилья', calories=280, proteins=14, fats=14, carbs=26, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='nachos', name_ru='начос', calories=350, proteins=7, fats=18, carbs=40, category_id=categories['fastfood'].id, default_portion=150),
            Food(name='sushi', name_ru='суши', calories=300, proteins=10, fats=5, carbs=55, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='rolls', name_ru='роллы', calories=320, proteins=8, fats=8, carbs=55, category_id=categories['fastfood'].id, default_portion=200),
            Food(name='philadelphia roll', name_ru='ролл филадельфия', calories=350, proteins=9, fats=12, carbs=50, category_id=categories['fastfood'].id, default_portion=250),
            Food(name='california roll', name_ru='ролл калифорния', calories=330, proteins=8, fats=10, carbs=52, category_id=categories['fastfood'].id, default_portion=250),
            
            # Полуфабрикаты
            Food(name='pelmeni', name_ru='пельмени', calories=250, proteins=12, fats=12, carbs=25, category_id=categories['other'].id, default_portion=200),
            Food(name='pelmeni beef', name_ru='пельмени говяжьи', calories=240, proteins=13, fats=10, carbs=26, category_id=categories['other'].id, default_portion=200),
            Food(name='pelmeni pork', name_ru='пельмени свиные', calories=280, proteins=11, fats=16, carbs=24, category_id=categories['other'].id, default_portion=200),
            Food(name='vareniki cottage cheese', name_ru='вареники с творогом', calories=200, proteins=10, fats=5, carbs=30, category_id=categories['other'].id, default_portion=200),
            Food(name='vareniki potato', name_ru='вареники с картошкой', calories=180, proteins=5, fats=3, carbs=33, category_id=categories['other'].id, default_portion=200),
            Food(name='vareniki cherry', name_ru='вареники с вишней', calories=190, proteins=4, fats=2, carbs=40, category_id=categories['other'].id, default_portion=200),
            Food(name='dumplings', name_ru='клецки', calories=220, proteins=6, fats=5, carbs=38, category_id=categories['other'].id, default_portion=150),
            Food(name='manti', name_ru='манты', calories=220, proteins=11, fats=9, carbs=24, category_id=categories['other'].id, default_portion=200),
            Food(name='khinkali', name_ru='хинкали', calories=230, proteins=12, fats=10, carbs=25, category_id=categories['other'].id, default_portion=200),
            Food(name='cheburek', name_ru='чебурек', calories=350, proteins=10, fats=20, carbs=32, category_id=categories['other'].id, default_portion=150),
            Food(name='belyash', name_ru='беляш', calories=320, proteins=12, fats=18, carbs=28, category_id=categories['other'].id, default_portion=150),
            Food(name='pie meat', name_ru='пирожок с мясом', calories=300, proteins=10, fats=14, carbs=35, category_id=categories['other'].id, default_portion=100),
            Food(name='pie cabbage', name_ru='пирожок с капустой', calories=250, proteins=6, fats=10, carbs=35, category_id=categories['other'].id, default_portion=100),
            Food(name='pie potato', name_ru='пирожок с картошкой', calories=240, proteins=5, fats=9, carbs=36, category_id=categories['other'].id, default_portion=100),
            Food(name='pie apple', name_ru='пирожок с яблоком', calories=220, proteins=4, fats=7, carbs=37, category_id=categories['other'].id, default_portion=100),
            Food(name='blini', name_ru='блины', calories=200, proteins=6, fats=5, carbs=32, category_id=categories['other'].id, default_portion=150),
            Food(name='blini with meat', name_ru='блины с мясом', calories=250, proteins=12, fats=10, carbs=28, category_id=categories['other'].id, default_portion=200),
            Food(name='blini with cottage cheese', name_ru='блины с творогом', calories=230, proteins=11, fats=8, carbs=29, category_id=categories['other'].id, default_portion=200),
            Food(name='blini with caviar', name_ru='блины с икрой', calories=270, proteins=14, fats=12, carbs=26, category_id=categories['other'].id, default_portion=150),
            Food(name='oladushki', name_ru='оладьи', calories=220, proteins=6, fats=8, carbs=33, category_id=categories['other'].id, default_portion=150),
            Food(name='syrniki', name_ru='сырники', calories=220, proteins=12, fats=10, carbs=22, category_id=categories['other'].id, default_portion=150),
            Food(name='zrazy', name_ru='зразы', calories=210, proteins=12, fats=10, carbs=18, category_id=categories['other'].id, default_portion=150),
            Food(name='cutlets', name_ru='котлеты', calories=250, proteins=14, fats=18, carbs=12, category_id=categories['other'].id, default_portion=150),
            Food(name='cutlets chicken', name_ru='котлеты куриные', calories=160, proteins=18, fats=8, carbs=8, category_id=categories['other'].id, default_portion=150),
            Food(name='cutlets fish', name_ru='котлеты рыбные', calories=140, proteins=15, fats=6, carbs=8, category_id=categories['other'].id, default_portion=150),
            Food(name='meatballs', name_ru='тефтели', calories=220, proteins=13, fats=14, carbs=12, category_id=categories['other'].id, default_portion=150),
            Food(name='goulash', name_ru='гуляш', calories=200, proteins=15, fats=12, carbs=8, category_id=categories['other'].id, default_portion=150),
                       Food(name='azasu', name_ru='азу', calories=180, proteins=14, fats=10, carbs=8, category_id=categories['other'].id, default_portion=150),
            Food(name='beef stroganoff', name_ru='бефстроганов', calories=190, proteins=15, fats=12, carbs=6, category_id=categories['other'].id, default_portion=150),
            Food(name='lobio', name_ru='лобио', calories=130, proteins=7, fats=5, carbs=15, category_id=categories['legumes'].id, default_portion=150),
            Food(name='hummus', name_ru='хумус', calories=250, proteins=8, fats=15, carbs=20, category_id=categories['legumes'].id, default_portion=100),
            Food(name='falafel', name_ru='фалафель', calories=280, proteins=8, fats=15, carbs=30, category_id=categories['legumes'].id, default_portion=150),
            
            # Гарниры
            Food(name='mashed potatoes', name_ru='пюре картофельное', calories=90, proteins=2, fats=3, carbs=14, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='mashed potatoes with milk', name_ru='пюре картофельное с молоком', calories=100, proteins=2.5, fats=3.5, carbs=15, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='mashed potatoes with butter', name_ru='пюре картофельное с маслом', calories=110, proteins=2, fats=4, carbs=16, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='fried potatoes', name_ru='картофель жареный', calories=200, proteins=3, fats=10, carbs=25, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='boiled potatoes', name_ru='картофель отварной', calories=80, proteins=2, fats=0.5, carbs=17, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='baked potatoes', name_ru='картофель запеченный', calories=95, proteins=2.5, fats=1, carbs=19, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='stewed cabbage', name_ru='тушеная капуста', calories=60, proteins=2, fats=3, carbs=7, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='braised cabbage', name_ru='капуста тушеная', calories=65, proteins=2, fats=3.5, carbs=7, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='ratatouille', name_ru='рататуй', calories=70, proteins=1.5, fats=4, carbs=7, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='vegetable stew', name_ru='рагу овощное', calories=80, proteins=2, fats=4, carbs=9, category_id=categories['vegetables'].id, default_portion=200),
            Food(name='rice with vegetables', name_ru='рис с овощами', calories=120, proteins=3, fats=3, carbs=21, category_id=categories['grains'].id, default_portion=200),
            Food(name='buckwheat with mushrooms', name_ru='гречка с грибами', calories=110, proteins=4, fats=3, carbs=17, category_id=categories['grains'].id, default_portion=200),
            Food(name='buckwheat with butter', name_ru='гречка с маслом', calories=130, proteins=4, fats=4, carbs=20, category_id=categories['grains'].id, default_portion=200),
            Food(name='pasta with cheese', name_ru='макароны с сыром', calories=180, proteins=7, fats=6, carbs=25, category_id=categories['grains'].id, default_portion=200),
            Food(name='pasta with sauce', name_ru='макароны с соусом', calories=170, proteins=5, fats=5, carbs=27, category_id=categories['grains'].id, default_portion=200),
            Food(name='spaghetti bolognese', name_ru='спагетти болоньезе', calories=200, proteins=9, fats=7, carbs=26, category_id=categories['grains'].id, default_portion=250),
            Food(name='spaghetti carbonara', name_ru='спагетти карбонара', calories=250, proteins=10, fats=12, carbs=25, category_id=categories['grains'].id, default_portion=250),
            Food(name='lasagna', name_ru='лазанья', calories=180, proteins=9, fats=8, carbs=18, category_id=categories['other'].id, default_portion=250),
            Food(name='risotto', name_ru='ризотто', calories=160, proteins=5, fats=5, carbs=24, category_id=categories['grains'].id, default_portion=250),
            Food(name='paella', name_ru='паэлья', calories=170, proteins=8, fats=5, carbs=23, category_id=categories['grains'].id, default_portion=300),
            
            # Соусы дополнительные
            Food(name='béchamel', name_ru='соус бешамель', calories=150, proteins=3, fats=10, carbs=12, category_id=categories['sauces'].id, default_portion=50),
            Food(name='holandaise', name_ru='соус голландез', calories=300, proteins=2, fats=30, carbs=2, category_id=categories['sauces'].id, default_portion=30),
            Food(name='carbonara sauce', name_ru='соус карбонара', calories=280, proteins=5, fats=25, carbs=8, category_id=categories['sauces'].id, default_portion=50),
            Food(name='marinara sauce', name_ru='соус маринара', calories=80, proteins=2, fats=4, carbs=10, category_id=categories['sauces'].id, default_portion=50),
            Food(name='pesto genovese', name_ru='песто генуэзский', calories=520, proteins=5, fats=52, carbs=8, category_id=categories['sauces'].id, default_portion=20),
            Food(name='salsa', name_ru='сальса', calories=40, proteins=1, fats=0.5, carbs=8, category_id=categories['sauces'].id, default_portion=50),
            Food(name='guacamole', name_ru='гуакамоле', calories=150, proteins=2, fats=13, carbs=8, category_id=categories['sauces'].id, default_portion=50),
            Food(name='tartar', name_ru='тартар', calories=350, proteins=1, fats=35, carbs=8, category_id=categories['sauces'].id, default_portion=30),
            Food(name='tzatziki', name_ru='цацики', calories=120, proteins=3, fats=10, carbs=5, category_id=categories['sauces'].id, default_portion=50),
            Food(name='aioli', name_ru='айоли', calories=450, proteins=2, fats=48, carbs=3, category_id=categories['sauces'].id, default_portion=20),
            Food(name='satsebeli', name_ru='сацебели', calories=80, proteins=1.5, fats=3, carbs=12, category_id=categories['sauces'].id, default_portion=30),
            Food(name='tkemali', name_ru='ткемали', calories=60, proteins=1, fats=0.5, carbs=14, category_id=categories['sauces'].id, default_portion=30),
            Food(name='narhrab', name_ru='наршараб', calories=250, proteins=1, fats=0, carbs=62, category_id=categories['sauces'].id, default_portion=20),
            
            # Джемы и топпинги
            Food(name='strawberry jam', name_ru='клубничное варенье', calories=250, proteins=0.5, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='raspberry jam', name_ru='малиновое варенье', calories=250, proteins=0.5, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='apricot jam', name_ru='абрикосовое варенье', calories=250, proteins=0.5, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='cherry jam', name_ru='вишневое варенье', calories=250, proteins=0.5, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='currant jam', name_ru='смородиновое варенье', calories=250, proteins=0.5, fats=0.1, carbs=62, category_id=categories['sweets'].id, default_portion=20),
            Food(name='nutella', name_ru='нутелла', calories=530, proteins=6, fats=30, carbs=57, category_id=categories['sweets'].id, default_portion=20),
            Food(name='chocolate spread', name_ru='шоколадная паста', calories=540, proteins=5, fats=32, carbs=58, category_id=categories['sweets'].id, default_portion=20),
            Food(name='maple syrup', name_ru='кленовый сироп', calories=260, proteins=0, fats=0, carbs=67, category_id=categories['sweets'].id, is_liquid=True, default_portion=30),
            Food(name='chocolate syrup', name_ru='шоколадный сироп', calories=270, proteins=2, fats=1, carbs=63, category_id=categories['sweets'].id, is_liquid=True, default_portion=30),
            Food(name='caramel syrup', name_ru='карамельный сироп', calories=300, proteins=0, fats=0, carbs=75, category_id=categories['sweets'].id, is_liquid=True, default_portion=30),
            Food(name='agave syrup', name_ru='сироп агавы', calories=310, proteins=0, fats=0, carbs=76, category_id=categories['sweets'].id, is_liquid=True, default_portion=30),
            
            # Спортивное питание
            Food(name='whey protein', name_ru='протеин сывороточный', calories=380, proteins=80, fats=5, carbs=5, category_id=categories['other'].id, default_portion=30),
            Food(name='casein protein', name_ru='протеин казеин', calories=370, proteins=75, fats=4, carbs=8, category_id=categories['other'].id, default_portion=30),
            Food(name='soy protein', name_ru='протеин соевый', calories=350, proteins=70, fats=3, carbs=12, category_id=categories['other'].id, default_portion=30),
            Food(name='gainer', name_ru='гейнер', calories=400, proteins=40, fats=5, carbs=50, category_id=categories['other'].id, default_portion=100),
            Food(name='creatine', name_ru='креатин', calories=0, proteins=0, fats=0, carbs=0, category_id=categories['other'].id, default_portion=5),
            Food(name='bcaa', name_ru='bcaa', calories=20, proteins=5, fats=0, carbs=0, category_id=categories['other'].id, default_portion=10),
            Food(name='protein bar', name_ru='протеиновый батончик', calories=200, proteins=15, fats=7, carbs=20, category_id=categories['other'].id, default_portion=50),
            Food(name='energy bar', name_ru='энергетический батончик', calories=250, proteins=5, fats=8, carbs=40, category_id=categories['other'].id, default_portion=50),
            
            # Детское питание
            Food(name='baby formula', name_ru='детская смесь', calories=500, proteins=10, fats=25, carbs=60, category_id=categories['other'].id, default_portion=100),
            Food(name='baby puree fruit', name_ru='пюре фруктовое детское', calories=80, proteins=0.5, fats=0.1, carbs=19, category_id=categories['other'].id, default_portion=100),
            Food(name='baby puree vegetable', name_ru='пюре овощное детское', calories=50, proteins=1.5, fats=0.5, carbs=10, category_id=categories['other'].id, default_portion=100),
            Food(name='baby puree meat', name_ru='пюре мясное детское', calories=90, proteins=8, fats=5, carbs=3, category_id=categories['other'].id, default_portion=100),
            Food(name='baby cottage cheese', name_ru='творожок детский', calories=110, proteins=8, fats=5, carbs=10, category_id=categories['other'].id, default_portion=100),
            Food(name='baby yogurt', name_ru='йогурт детский', calories=80, proteins=3, fats=2.5, carbs=12, category_id=categories['other'].id, default_portion=100),
            Food(name='baby juice', name_ru='сок детский', calories=45, proteins=0.3, fats=0, carbs=11, category_id=categories['other'].id, is_liquid=True, default_portion=200),
            Food(name='baby porridge', name_ru='каша детская', calories=400, proteins=10, fats=5, carbs=75, category_id=categories['other'].id, default_portion=50),
            
            # Алкоголь (продолжение)
            Food(name='liquor', name_ru='ликер', calories=300, proteins=0, fats=0, carbs=35, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='baileys', name_ru='бейлис', calories=327, proteins=3, fats=13, carbs=25, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='martini', name_ru='мартини', calories=145, proteins=0, fats=0, carbs=15, category_id=categories['drinks'].id, is_liquid=True, default_portion=100),
            Food(name='vermouth', name_ru='вермут', calories=150, proteins=0, fats=0, carbs=16, category_id=categories['drinks'].id, is_liquid=True, default_portion=100),
            Food(name='sake', name_ru='саке', calories=134, proteins=0.5, fats=0, carbs=5, category_id=categories['drinks'].id, is_liquid=True, default_portion=100),
            Food(name='tequila', name_ru='текила', calories=231, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='rum', name_ru='ром', calories=231, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='gin', name_ru='джин', calories=231, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='brandy', name_ru='бренди', calories=225, proteins=0, fats=0, carbs=0.5, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='calvados', name_ru='кальвадос', calories=220, proteins=0, fats=0, carbs=1, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='grappa', name_ru='граппа', calories=230, proteins=0, fats=0, carbs=0, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='chacha', name_ru='чача', calories=235, proteins=0, fats=0, carbs=0.1, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='moonshine', name_ru='самогон', calories=235, proteins=0, fats=0, carbs=0.1, category_id=categories['drinks'].id, is_liquid=True, default_portion=50),
            Food(name='beer non-alcoholic', name_ru='пиво безалкогольное', calories=25, proteins=0.3, fats=0, carbs=5, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='beer light', name_ru='пиво светлое', calories=42, proteins=0.4, fats=0, carbs=3.5, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='beer dark', name_ru='пиво темное', calories=48, proteins=0.5, fats=0, carbs=4, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='beer live', name_ru='пиво живое', calories=45, proteins=0.5, fats=0, carbs=3.8, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='cider', name_ru='сидр', calories=50, proteins=0, fats=0, carbs=6, category_id=categories['drinks'].id, is_liquid=True, default_portion=500),
            Food(name='mead', name_ru='медовуха', calories=100, proteins=0, fats=0, carbs=15, category_id=categories['drinks'].id, is_liquid=True, default_portion=250),
        ]
        
        for food in foods:
            session.add(food)
        
        session.commit()
        
        # Подсчитываем количество продуктов
        food_count = session.query(Food).count()
        category_count = session.query(FoodCategory).count()
        
        session.close()
        print(f"✅ База данных успешно инициализирована!")
        print(f"📊 Категорий: {category_count}")
        print(f"🍎 Продуктов: {food_count}")
    
    def find_food(self, name):
        """Улучшенный поиск продукта по названию"""
        session = self.Session()
        name = name.lower().strip()
        
        # Прямой поиск по русскому названию
        food = session.query(Food).filter(Food.name_ru == name).first()
        if food:
            session.close()
            return food
        
        # Поиск по вхождению в русское название
        food = session.query(Food).filter(Food.name_ru.ilike(f'%{name}%')).first()
        if food:
            session.close()
            return food
        
        # Поиск по английскому названию
        food = session.query(Food).filter(Food.name.ilike(f'%{name}%')).first()
        if food:
            session.close()
            return food
        
        # Если ничего не найдено, ищем по частям (для составных блюд)
        words = name.split()
        for word in words:
            if len(word) > 3:  # Игнорируем короткие слова
                food = session.query(Food).filter(
                    (Food.name_ru.ilike(f'%{word}%')) | 
                    (Food.name.ilike(f'%{word}%'))
                ).first()
                if food:
                    session.close()
                    return food
        
        session.close()
        return None
    
    def get_all_foods(self):
        """Получить все продукты (для отладки)"""
        session = self.Session()
        foods = session.query(Food).all()
        session.close()
        return foods
    
    def get_foods_by_category(self, category_name):
        """Получить продукты по категории"""
        session = self.Session()
        foods = session.query(Food).join(FoodCategory).filter(FoodCategory.name == category_name).all()
        session.close()
        return foods
    
    def add_meal(self, telegram_id, food_name, weight, meal_type='breakfast'):
        """Добавление записи о приеме пищи"""
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
        
        # Получаем КБЖУ для этого приема
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
        """Создание нового пользователя"""
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
            
            # Пересчитываем дневную норму
            daily_norm = user.calculate_daily_norm()
            if daily_norm:
                user.daily_calories = daily_norm
            
            session.commit()
        session.close()
        
    def get_daily_summary(self, telegram_id, date=None):
        """Получение сводки за день"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        session = self.Session()
        meals = session.query(MealEntry).filter_by(
            user_id=telegram_id,
            date=date
        ).all()
        
        total = {
            'calories': 0,
            'proteins': 0,
            'fats': 0,
            'carbs': 0
        }
        
        meals_by_type = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }
        
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
        
        return {
            'date': date,
            'meals': meals_by_type,
            'total': total
        }