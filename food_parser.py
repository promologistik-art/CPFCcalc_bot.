import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
    
    def parse_message(self, text):
        """
        Разбор сообщения на отдельные блюда/продукты
        Возвращает список словарей с name и weight
        """
        text = text.lower().strip()
        
        # Заменяем переносы и маркеры на запятые
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        # Разделяем по запятым
        parts = [p.strip() for p in text.split(',') if p.strip()]
        
        # Дополнительное разделение по "и"
        final_parts = []
        for part in parts:
            if ' и ' in part:
                subparts = [p.strip() for p in part.split(' и ')]
                final_parts.extend(subparts)
            else:
                final_parts.append(part)
        
        results = []
        for part in final_parts:
            items = self._parse_part(part)
            results.extend(items)
        
        return results
    
    def _parse_part(self, text):
        """
        Парсит одну часть (до запятой)
        Возвращает список продуктов с весами
        """
        if not text:
            return []
        
        print(f"\n📝 Парсим: '{text}'")
        
        # Специальная обработка для яичницы (нужно считать количество яиц)
        if 'яичница' in text:
            return self._parse_eggs(text)
        
        # Специальная обработка для бутерброда
        if 'бутерброд' in text:
            return self._parse_sandwich(text)
        
        # Для всего остального - разбиваем на слова и ищем каждое
        return self._parse_words(text)
    
    def _parse_eggs(self, text):
        """Разбирает яичницу"""
        print("   🍳 Яичница")
        
        # Ищем количество яиц
        match = re.search(r'(\d+)\s*яйц', text)
        if match:
            egg_count = int(match.group(1))
        else:
            egg_count = 2
        
        weight = egg_count * 50
        print(f"   Яиц: {egg_count}, вес: {weight}г")
        
        # Ищем в базе
        food = self.db.find_food_by_word("яичница")
        if not food:
            food = self.db.find_food_by_word("яйца")
        
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        
        return []
    
    def _parse_sandwich(self, text):
        """Разбирает бутерброд на ингредиенты"""
        print("   🥪 Бутерброд")
        
        results = []
        
        # Добавляем хлеб (50г)
        bread = self.db.find_food_by_word("хлеб")
        if bread:
            results.append({'name': bread.name_ru, 'weight': 50})
            print(f"   ✅ Хлеб: {bread.name_ru} (50г)")
        
        # Ищем начинку (семга, авокадо, сыр, колбаса и т.д.)
        fillings = ['семга', 'лосось', 'форель', 'авокадо', 'сыр', 'колбаса', 'ветчина', 'курица']
        
        for filling in fillings:
            if filling in text:
                food = self.db.find_food_by_word(filling)
                if food:
                    # Вес начинки для бутерброда - 50-80г
                    weight = 70 if filling == 'авокадо' else 50
                    results.append({'name': food.name_ru, 'weight': weight})
                    print(f"   ✅ Начинка: {food.name_ru} ({weight}г)")
        
        return results
    
    def _parse_words(self, text):
        """
        Разбивает текст на слова и ищет каждое
        """
        # Убираем вес из текста
        weight_match = re.search(r'(\d+)\s*г', text)
        explicit_weight = int(weight_match.group(1)) if weight_match else None
        
        # Очищаем текст от веса
        clean_text = re.sub(r'\d+\s*г', '', text)
        
        # Разбиваем на слова
        words = clean_text.split()
        
        # Убираем предлоги
        stop_words = ['с', 'со', 'из', 'на', 'в', 'и', 'или', 'а', 'но', 'для', 'без', 'по']
        words = [w for w in words if w not in stop_words]
        
        print(f"   Слова для поиска: {words}")
        
        results = []
        
        for word in words:
            # Пропускаем короткие слова
            if len(word) < 2:
                continue
            
            # Нормализуем слово
            word = self._normalize(word)
            
            # Ищем в базе
            food = self.db.find_food_by_word(word)
            
            if food:
                # Определяем вес
                if explicit_weight:
                    weight = explicit_weight
                else:
                    weight = self._get_default_weight(word)
                
                results.append({'name': food.name_ru, 'weight': weight})
                print(f"   ✅ Найден: {food.name_ru} ({weight}г)")
            else:
                print(f"   ❌ Не найден: {word}")
        
        return results
    
    def _normalize(self, word):
        """Нормализует слово для поиска"""
        synonyms = {
            'овсянка': 'овсяная',
            'гречка': 'гречневая',
            'манка': 'манная',
            'пшенка': 'пшенная',
            'перловка': 'перловая',
            'картошка': 'картофель',
            'помидор': 'томат',
            'семга': 'семга',
            'авокадо': 'авокадо',
        }
        
        if word in synonyms:
            return synonyms[word]
        
        # Убираем окончания
        if word.endswith('ая') and len(word) > 2:
            return word[:-2]  # овсяная -> овсян
        
        if word.endswith('ой') and len(word) > 2:
            return word[:-2]  # семгой -> семг
        
        return word
    
    def _get_default_weight(self, word):
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