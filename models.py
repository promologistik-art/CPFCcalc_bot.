from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    name_ru = Column(String, index=True)
    calories = Column(Float)
    proteins = Column(Float)
    fats = Column(Float)
    carbs = Column(Float)
    category_id = Column(Integer, ForeignKey('food_categories.id'))
    is_liquid = Column(Boolean, default=False)
    default_portion = Column(Float, nullable=True)
    
    category = relationship("FoodCategory", back_populates="foods")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    activity_level = Column(Float, default=1.2)
    daily_calories = Column(Float, nullable=True)
    
    def calculate_daily_norm(self):
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
    weight = Column(Float)
    date = Column(String)
    meal_type = Column(String)
    
    food = relationship("Food")