import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
    
    def parse_message(self, text):
        """
        Разбор сообщения на отдельные блюда/продукты
        """
        text = text.lower().strip()
        
        # Заменяем переносы и маркеры на запятые
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        # Разделяем по запятым
        parts = [p.strip() for p in text.split(',') if p.strip()]
        
        print(f"📝 Исходный текст: {text}")
        print(f"📝 Части: {parts}")
        
        results = []
        for part in parts:
            items = self._parse_part(part)
            results.extend(items)
        
        return results
    
    def _parse_part(self, text):
        """
        Парсит одну часть (до запятой)
        """
        if not text:
            return []
        
        print(f"\n📝 Парсим часть: '{text}'")
        
        # 1. Извлекаем вес
        weight_match = re.search(r'(\d+)\s*г', text)
        explicit_weight = int(weight_match.group(1)) if weight_match else None
        
        if explicit_weight:
            print(f"   Вес: {explicit_weight}г")
        
        # 2. Очищаем текст от веса и служебных слов
        clean_text = re.sub(r'\d+\s*г', '', text).strip()
        clean_text = re.sub(r'^(тарелка|порция|чашка|стакан|ложка|ложки|кусок|куска)\s+', '', clean_text)
        
        print(f"   Очищенный текст: '{clean_text}'")
        
        # 3. Нормализуем запрос (заменяем синонимы)
        normalized = self._normalize_query(clean_text)
        print(f"   Нормализованный: '{normalized}'")
        
        # 4. Ищем в базе
        food = self.db.find_best_match(normalized)
        
        if food:
            weight = explicit_weight if explicit_weight else self._get_default_weight(food.name_ru)
            print(f"   ✅ Найден: {food.name_ru} ({weight}г)")
            return [{'name': food.name_ru, 'weight': weight}]
        
        print(f"   ❌ Не найден")
        return []
    
    def _normalize_query(self, text):
        """
        Нормализует запрос пользователя
        Заменяет уменьшительные формы и синонимы
        """
        synonyms = {
            'овсянка': 'овсяная каша',
            'гречка': 'гречневая каша',
            'манка': 'манная каша',
            'пшенка': 'пшенная каша',
            'перловка': 'перловая каша',
            'картошка': 'картофель',
            'помидор': 'томат',
            'семга': 'семга',
            'авокадо': 'авокадо',
            'колбаска': 'колбаса',
            'сосиска': 'сосиски',
            'молочко': 'молоко',
            'кефирчик': 'кефир',
            'творожок': 'творог',
            'хлебушек': 'хлеб',
            'маслице': 'масло сливочное',
            'сырок': 'сыр',
            'кофеек': 'кофе',
            'чайку': 'чай',
            'сахарок': 'сахар',
        }
        
        text_lower = text.lower()
        for key, value in synonyms.items():
            if key in text_lower:
                text_lower = text_lower.replace(key, value)
        
        return text_lower
    
    def _get_default_weight(self, name):
        """
        Стандартный вес для продукта
        """
        name_lower = name.lower()
        
        # Супы
        if any(x in name_lower for x in ['суп', 'борщ', 'щи', 'солянка', 'окрошка', 'уха', 'рассольник']):
            return 350
        # Каши
        if any(x in name_lower for x in ['каша', 'гречневая', 'овсяная', 'манная', 'рисовая', 'пшенная', 'перловая']):
            return 250
        # Салаты
        if any(x in name_lower for x in ['салат', 'оливье', 'винегрет', 'цезарь']):
            return 200
        # Напитки
        if any(x in name_lower for x in ['кофе', 'чай', 'сок', 'компот', 'кисель']):
            return 200
        # Молочка
        if 'молоко' in name_lower or 'кефир' in name_lower:
            return 200
        if 'йогурт' in name_lower:
            return 150
        if 'творог' in name_lower:
            return 150
        if 'сметана' in name_lower:
            return 20
        # Хлеб
        if 'хлеб' in name_lower:
            return 50
        # Яйца
        if 'яйцо' in name_lower:
            return 50
        if 'яичница' in name_lower:
            return 200
        # Мясо
        if any(x in name_lower for x in ['шашлык', 'стейк', 'отбивная']):
            return 200
        if any(x in name_lower for x in ['колбаса', 'сосиски', 'ветчина']):
            return 50
        # Рыба
        if any(x in name_lower for x in ['семга', 'лосось', 'форель', 'сельдь']):
            return 80
        # Овощи
        if any(x in name_lower for x in ['картофель', 'картошка']):
            return 200
        if any(x in name_lower for x in ['огурец', 'помидор', 'томат']):
            return 100
        # Фрукты
        if any(x in name_lower for x in ['яблоко', 'банан', 'апельсин', 'груша']):
            return 150
        # Сладости
        if 'шоколад' in name_lower:
            return 20
        if 'печенье' in name_lower:
            return 30
        
        return 150  # вес по умолчанию