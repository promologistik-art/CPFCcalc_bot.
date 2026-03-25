import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
    
    def parse_message(self, text):
        """Разбор сообщения"""
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
        """Парсит одну часть"""
        if not text:
            return []
        
        print(f"\n📝 Парсим: '{text}'")
        
        # 1. Проверяем на яичницу
        if 'яичница' in text:
            return self._parse_eggs(text)
        
        # 2. Проверяем на бутерброд
        if 'бутерброд' in text:
            return self._parse_sandwich(text)
        
        # 3. Проверяем на кашу
        if 'каша' in text:
            return self._parse_porridge(text)
        
        # 4. Обычный продукт
        quantity, clean_text = self._extract_quantity(text)
        weight = self._extract_weight(clean_text)
        name = self._clean_name(clean_text)
        
        if weight == 0:
            weight = self._get_default_weight(name)
        
        if quantity > 1:
            weight = weight * quantity
            print(f"   Количество: {quantity} → вес: {weight}г")
        
        name = self._normalize_name(name)
        food = self.db.find_food(name)
        
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        return []
    
    def _parse_eggs(self, text):
        """Разбирает яичницу"""
        print("   🍳 Обнаружена яичница")
        
        # Извлекаем количество яиц
        match = re.search(r'(\d+)\s*яйц', text)
        if match:
            egg_count = int(match.group(1))
        else:
            egg_count = 2  # стандартная порция
        
        # Вес: 1 яйцо ≈ 50г
        weight = egg_count * 50
        print(f"   Яиц: {egg_count}, вес: {weight}г")
        
        # Ищем в базе "Яичница глазунья"
        food = self.db.find_food("яичница глазунья")
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        
        # Если нет, ищем просто "яйца"
        food = self.db.find_food("яйца")
        if food:
            return [{'name': food.name_ru, 'weight': weight}]
        
        return []
    
    def _parse_sandwich(self, text):
        """Разбирает бутерброд на ингредиенты"""
        print("   🥪 Обнаружен бутерброд")
        
        # Извлекаем количество
        quantity, clean_text = self._extract_quantity(text)
        
        # Вес одного бутерброда
        weight = self._extract_weight(clean_text)
        if weight == 0:
            weight = 200  # стандартный вес
        
        total_weight = weight * quantity
        print(f"   Вес 1 бутерброда: {weight}г, всего: {total_weight}г")
        
        ingredients = []
        
        # Пропорции
        bread_ratio = 0.4      # 40% хлеб
        spread_ratio = 0.1     # 10% намазка
        filling_ratio = 0.5    # 50% начинка
        
        # 1. Хлеб
        bread_type = 'хлеб'
        bread_variants = ['бородинский', 'белый', 'черный', 'ржаной', 'зерновой']
        for bv in bread_variants:
            if bv in clean_text:
                bread_type = f'хлеб {bv}'
                break
        
        ingredients.append({
            'name': bread_type,
            'weight': round(total_weight * bread_ratio, 1)
        })
        
        # 2. Намазка (если есть)
        spreads = {
            'масло': 'масло сливочное',
            'сливочный сыр': 'сыр сливочный',
            'творожный сыр': 'сыр творожный',
            'авокадо': 'авокадо',
        }
        
        for key, value in spreads.items():
            if key in clean_text:
                ingredients.append({
                    'name': value,
                    'weight': round(total_weight * spread_ratio, 1)
                })
                break
        
        # 3. Начинка
        fillings = {
            'семга': 'семга',
            'лосось': 'лосось',
            'форель': 'форель',
            'ветчина': 'ветчина',
            'колбаса': 'колбаса',
            'сыр': 'сыр',
            'курица': 'курица',
        }
        
        has_avocado = any(ing['name'] == 'авокадо' for ing in ingredients)
        
        for key, value in fillings.items():
            if key in clean_text:
                if key == 'авокадо' and has_avocado:
                    continue
                ingredients.append({
                    'name': value,
                    'weight': round(total_weight * filling_ratio, 1)
                })
                break
        
        # Если начинки нет, берем половину веса как начинку
        if len(ingredients) == 1:
            ingredients.append({
                'name': 'начинка',
                'weight': round(total_weight * filling_ratio, 1)
            })
        
        # Ищем каждый ингредиент в базе
        result = []
        for ing in ingredients:
            food = self.db.find_food(ing['name'])
            if food:
                result.append({'name': food.name_ru, 'weight': ing['weight']})
            else:
                print(f"   ⚠️ Ингредиент не найден: {ing['name']}")
        
        return result
    
    def _parse_porridge(self, text):
        """Разбирает кашу"""
        print("   🥣 Обнаружена каша")
        
        # Извлекаем количество порций
        quantity, clean_text = self._extract_quantity(text)
        
        # Определяем тип каши
        porridge_type = None
        if 'овсян' in clean_text or 'геркулес' in clean_text:
            porridge_type = 'овсяная каша'
        elif 'гречн' in clean_text or 'гречка' in clean_text:
            porridge_type = 'гречневая каша'
        elif 'манн' in clean_text or 'манка' in clean_text:
            porridge_type = 'манная каша'
        elif 'рис' in clean_text:
            porridge_type = 'рисовая каша'
        elif 'пшен' in clean_text or 'пшено' in clean_text:
            porridge_type = 'пшенная каша'
        elif 'перлов' in clean_text or 'перловка' in clean_text:
            porridge_type = 'перловая каша'
        
        if not porridge_type:
            porridge_type = 'каша'
        
        # Определяем на чем приготовлена
        if 'молоке' in clean_text:
            porridge_type = f'{porridge_type} на молоке'
        elif 'воде' in clean_text:
            porridge_type = f'{porridge_type} на воде'
        
        # Вес порции
        weight = self._extract_weight(clean_text)
        if weight == 0:
            weight = 250  # стандартная порция каши
        
        total_weight = weight * quantity
        print(f"   Тип: {porridge_type}, порция: {weight}г, всего: {total_weight}г")
        
        food = self.db.find_food(porridge_type)
        if food:
            return [{'name': food.name_ru, 'weight': total_weight}]
        
        return []
    
    def _extract_quantity(self, text):
        """Извлекает количество (2 бутерброда, 4 яйца)"""
        # Паттерны: "4 яйца", "2 бутерброда", "яйца 4 шт"
        patterns = [
            (r'^(\d+)\s+(.+)', 1),           # "4 яйца"
            (r'(.+)\s+(\d+)\s*шт', 2),       # "яйца 4 шт"
            (r'(\d+)\s*шт\s+(.+)', 1),       # "4 шт яйца"
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
        """Очищает название от веса"""
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*гр', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        
        stop_words = ['с', 'со', 'из', 'на', 'в', 'для', 'и', 'или']
        words = text.split()
        cleaned = [w for w in words if w not in stop_words]
        
        return ' '.join(cleaned).strip()
    
    def _normalize_name(self, name):
        """Нормализует название"""
        synonyms = {
            'овсянка': 'овсяная каша',
            'гречка': 'гречневая каша',
            'манка': 'манная каша',
            'пшенка': 'пшенная каша',
            'перловка': 'перловая каша',
            'картошка': 'картофель',
            'помидор': 'томат',
        }
        
        name_lower = name.lower()
        for key, value in synonyms.items():
            if key in name_lower:
                return value
        return name
    
    def _get_default_weight(self, name):
        """Стандартный вес"""
        name_lower = name.lower()
        
        portions = {
            'кофе': 200, 'чай': 200, 'сок': 200,
            'молоко': 200, 'кефир': 200, 'йогурт': 150,
            'творог': 150, 'сметана': 20,
            'хлеб': 40, 'бутерброд': 200,
            'яйцо': 50, 'яичница': 200,
            'яблоко': 150, 'банан': 150,
            'картофель': 200,
            'каша': 250, 'суп': 300, 'борщ': 300,
            'салат': 200, 'пельмени': 200, 'шашлык': 200,
        }
        
        for key, portion in portions.items():
            if key in name_lower:
                return portion
        return 100