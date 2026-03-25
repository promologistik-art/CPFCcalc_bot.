import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
    
    def parse_message(self, text):
        """Разбор сообщения на части по запятым"""
        text = text.lower().strip()
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        parts = [p.strip() for p in text.split(',') if p.strip()]
        
        results = []
        for part in parts:
            items = self._parse_part(part)
            results.extend(items)
        
        return results
    
    def _parse_part(self, text):
        """Парсит одну часть (все что до запятой)"""
        if not text:
            return []
        
        print(f"\n📝 Парсим: '{text}'")
        
        # Специальные случаи
        if 'яичница' in text:
            return self._parse_eggs(text)
        
        # Разбиваем на компоненты
        components = self._split_into_components(text)
        print(f"   Компоненты: {components}")
        
        results = []
        for comp in components:
            # Пропускаем предлоги и слово бутерброд
            if comp in ['с', 'со', 'из', 'на', 'в', 'и', 'или', 'а', 'но', 
                       'бутерброд', 'бутерброда', 'бутерброде', 'бутербродом']:
                continue
            
            # Пропускаем короткие слова
            if len(comp) < 2:
                continue
            
            # Определяем количество и вес
            quantity, clean_comp = self._extract_quantity(comp)
            weight = self._extract_weight(clean_comp)
            name = self._clean_name(clean_comp)
            
            if not name:
                continue
            
            if weight == 0:
                weight = self._get_default_weight(name)
            
            if quantity > 1:
                weight = weight * quantity
            
            # Нормализуем название
            name = self._normalize_name(name)
            
            # Ищем в базе
            food = self.db.find_food(name)
            if food:
                results.append({'name': food.name_ru, 'weight': weight})
                print(f"   ✅ Найден: {food.name_ru} ({weight}г)")
            else:
                print(f"   ❌ Не найден: {name}")
        
        return results
    
    def _split_into_components(self, text):
        """Разбивает текст на компоненты"""
        # Убираем слово "бутерброд" и его формы
        text = re.sub(r'\bбутерброд\w*\b', '', text)
        
        # Заменяем союзы и предлоги на разделители
        separators = [' с ', ' со ', ' и ', ' из ', ' на ', ' в ', ',', 'а также', 'плюс']
        for sep in separators:
            text = text.replace(sep, ' | ')
        
        # Убираем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Разбиваем по разделителю
        components = [c.strip() for c in text.split('|') if c.strip()]
        
        # Если ничего не разбилось, очищаем от предлогов в начале
        if not components and text:
            clean_text = re.sub(r'^(с|со|из|на|в)\s+', '', text)
            if clean_text:
                return [clean_text]
            return [text]
        
        return components
    
    def _parse_eggs(self, text):
        """Разбирает яичницу"""
        print("   🍳 Обнаружена яичница")
        
        match = re.search(r'(\d+)\s*яйц', text)
        if match:
            egg_count = int(match.group(1))
        else:
            egg_count = 2
        
        weight = egg_count * 50
        print(f"   Яиц: {egg_count}, вес: {weight}г")
        
        # Сначала ищем яичницу
        food = self.db.find_food("яичница глазунья")
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        
        # Если нет, ищем яйца
        food = self.db.find_food("яйца")
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        
        return []
    
    def _extract_quantity(self, text):
        """Извлекает количество"""
        patterns = [
            (r'^(\d+)\s+(.+)', 1),
            (r'(.+)\s+(\d+)\s*шт', 2),
        ]
        
        for pattern, group in patterns:
            match = re.match(pattern, text)
            if match:
                if group == 1:
                    return int(match.group(1)), match.group(2)
                else:
                    return int(match.group(2)), match.group(1)
        
        return 1, text
    
    def _extract_weight(self, text):
        """Извлекает вес"""
        patterns = [
            (r'(\d+)\s*г(?:рамм)?', 1),
            (r'(\d+)\s*гр', 1),
            (r'(\d+)\s*мл', 1),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1)) * multiplier
        return 0
    
    def _clean_name(self, text):
        """Очищает название от веса и предлогов"""
        # Удаляем вес
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*гр', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        
        # Убираем предлоги в начале
        text = re.sub(r'^(с|со|из|на|в|для|без)\s+', '', text)
        
        return text.strip()
    
    def _normalize_name(self, name):
        """Нормализует название для поиска в базе"""
        name_lower = name.lower()
        
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
            'бородинский хлеб': 'хлеб бородинский',
            'бородинский': 'хлеб бородинский',
            'белый хлеб': 'хлеб белый',
            'черный хлеб': 'хлеб черный',
            'ржаной хлеб': 'хлеб ржаной',
        }
        
        for key, value in synonyms.items():
            if key == name_lower or key in name_lower:
                return value
        
        return name
    
    def _get_default_weight(self, name):
        """Стандартный вес для продукта"""
        name_lower = name.lower()
        
        portions = {
            'кофе': 200, 'чай': 200, 'сок': 200,
            'молоко': 200, 'кефир': 200, 'йогурт': 150,
            'творог': 150, 'сметана': 20,
            'хлеб': 50,
            'яйцо': 50, 'яичница': 200,
            'яблоко': 150, 'банан': 150,
            'картофель': 200,
            'овсяная каша': 250, 'гречневая каша': 250,
            'манная каша': 250, 'рисовая каша': 250,
            'каша': 250,
            'суп': 300, 'борщ': 300,
            'салат': 200, 'пельмени': 200, 'шашлык': 200,
            'семга': 100, 'авокадо': 100, 'сыр': 30, 'масло сливочное': 10,
        }
        
        for key, portion in portions.items():
            if key in name_lower:
                return portion
        
        return 100