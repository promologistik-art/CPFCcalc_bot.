from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class FoodCategory(Base):
    __tablename__ = 'food_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    
    foods = relationship("Food", back_populates="category")

class Food(Base):
    __tablename__ = 'foods'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    name_ru = Column(String, index=True)  # Русское название
    calories = Column(Float)  # ккал на 100г
    proteins = Column(Float)  # белки на 100г
    fats = Column(Float)      # жиры на 100г
    carbs = Column(Float)     # углеводы на 100г
    category_id = Column(Integer, ForeignKey('food_categories.id'))
    is_liquid = Column(Boolean, default=False)  # для жидкостей (мл)
    default_portion = Column(Float, nullable=True)  # стандартная порция в г/мл
    
    category = relationship("FoodCategory", back_populates="foods")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    activity_level = Column(Float, default=1.2)  # коэффициент активности
    daily_calories = Column(Float, nullable=True)
    
    def calculate_daily_norm(self):
        """Расчет дневной нормы калорий (формула Миффлина-Сан Жеора)"""
        if not all([self.weight, self.height, self.age, self.gender]):
            return None
            
        if self.gender == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        
        return bmr * self.activity_level

class MealEntry(Base):
    __tablename__ = 'meal_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.telegram_id'))
    food_id = Column(Integer, ForeignKey('foods.id'))
    weight = Column(Float)  # вес в граммах
    date = Column(String)   # дата в формате YYYY-MM-DD
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    
    food = relationship("Food")