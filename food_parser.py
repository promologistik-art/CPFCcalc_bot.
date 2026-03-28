import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
    
    def parse_message(self, text):
        text = text.lower().strip()
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        parts = [p.strip() for p in text.split(',') if p.strip()]
        
        print(f"📝 Части: {parts}")
        
        results = []
        for part in parts:
            items = self._parse_part(part)
            results.extend(items)
        
        return results
    
    def _parse_part(self, text):
        if not text:
            return []
        
        print(f"\n📝 Парсим: '{text}'")
        
        # Извлекаем вес
        weight_match = re.search(r'(\d+)\s*г', text)
        explicit_weight = int(weight_match.group(1)) if weight_match else None
        
        if explicit_weight:
            print(f"   Вес: {explicit_weight}г")
        
        # Очищаем текст
        clean_text = re.sub(r'\d+\s*г', '', text).strip()
        clean_text = re.sub(r'^(тарелка|порция|чашка|стакан|ложка|ложки|кусок)\s+', '', clean_text)
        
        print(f"   Очищенный: '{clean_text}'")
        
        # Нормализуем
        normalized = self._normalize(clean_text)
        print(f"   Нормализованный: '{normalized}'")
        
        # Ищем в базе
        food = self.db.find_food_by_word(normalized)
        
        if food:
            weight = explicit_weight if explicit_weight else self._get_weight(food.name_ru)
            print(f"   ✅ Найден: {food.name_ru} ({weight}г)")
            return [{'name': food.name_ru, 'weight': weight}]
        
        print(f"   ❌ Не найден")
        return []
    
    def _normalize(self, text):
        synonyms = {
            'овсянка': 'овсяная каша',
            'гречка': 'гречневая каша',
            'манка': 'манная каша',
            'пшенка': 'пшенная каша',
            'перловка': 'перловая каша',
            'картошка': 'картофель',
            'помидор': 'томат',
        }
        
        for key, value in synonyms.items():
            if key in text:
                return value
        return text
    
    def _get_weight(self, name):
        name_lower = name.lower()
        
        if any(x in name_lower for x in ['суп', 'борщ', 'щи', 'солянка']):
            return 350
        if any(x in name_lower for x in ['каша', 'гречневая', 'овсяная', 'манная']):
            return 250
        if 'кофе' in name_lower:
            return 200
        if 'творог' in name_lower:
            return 150
        if 'хлеб' in name_lower:
            return 50
        
        return 150