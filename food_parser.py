import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """
        Парсинг сообщения с продуктами
        """
        # Приводим к нижнему регистру
        text = text.lower().strip()
        
        # Заменяем разные разделители
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        # Разделяем по запятым
        parts = [p.strip() for p in text.split(',') if p.strip()]
        results = []
        
        for part in parts:
            # Проверяем, есть ли в части "и" (но не в составе названий)
            if ' и ' in part and not self._has_complex_dish(part):
                subparts = part.split(' и ')
                for subpart in subparts:
                    results.extend(self._parse_single_item(subpart.strip()))
            else:
                results.extend(self._parse_single_item(part))
        
        return results
    
    def _has_complex_dish(self, text):
        """Проверяет, содержит ли текст сложное блюдо"""
        complex_dishes = ['бутерброд с', 'кофе с', 'чай с', 'салат с']
        return any(dish in text for dish in complex_dishes)
    
    def _parse_single_item(self, text):
        """Парсинг одного продукта или блюда"""
        if not text:
            return []
        
        # Проверяем конкретные названия (важно: порядок имеет значение!)
        if 'салат оливье' in text:
            return self._create_product('салат оливье', text, 200)
        if 'салат цезарь' in text:
            return self._create_product('салат цезарь', text, 200)
        if 'салат греческий' in text:
            return self._create_product('салат греческий', text, 200)
        
        if 'борщ' in text:
            return self._parse_borscht(text)
        if 'щи' in text:
            return self._create_product('щи', text, 300)
        if 'солянка' in text:
            return self._create_product('солянка', text, 300)
        if 'окрошка' in text:
            return self._create_product('окрошка', text, 300)
        
        if 'шашлык' in text:
            return self._parse_shashlik(text)
        if 'пельмени' in text:
            return self._create_product('пельмени', text, 200)
        if 'вареники' in text:
            return self._create_product('вареники', text, 200)
        if 'блины' in text:
            return self._parse_pancakes(text)
        if 'котлеты' in text:
            return self._parse_cutlets(text)
        
        if 'яичница' in text or 'яйца' in text:
            return self._parse_eggs(text)
        
        if 'бутерброд' in text:
            return self._parse_sandwich(text)
        
        if 'пиво' in text:
            return self._parse_beer(text)
        if 'кофе' in text:
            return self._parse_coffee(text)
        if 'чай' in text:
            return self._parse_tea(text)
        
        # Обычный продукт
        return self._parse_simple_food(text)
    
    def _create_product(self, name, text, default_weight):
        """Создает продукт с весом"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = default_weight
        return [{'name': name, 'weight': weight}]
    
    def _parse_borscht(self, text):
        """Парсинг борща"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 300
        
        products = [{'name': 'борщ', 'weight': weight}]
        if 'со сметаной' in text:
            products.append({'name': 'сметана 20%', 'weight': 20})
        return products
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200
        
        if 'свинина' in text or 'свиной' in text:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
        elif 'курица' in text or 'куриный' in text:
            return [{'name': 'шашлык из курицы', 'weight': weight}]
        else:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
    
    def _parse_pancakes(self, text):
        """Парсинг блинов"""
        count = 3
        match = re.search(r'(\d+)\s*блин', text)
        if match:
            count = int(match.group(1))
        
        weight = count * 50
        
        if 'с мясом' in text:
            return [{'name': 'блины с мясом', 'weight': weight}]
        elif 'с творогом' in text:
            return [{'name': 'блины с творогом', 'weight': weight}]
        else:
            return [{'name': 'блины', 'weight': weight}]
    
    def _parse_cutlets(self, text):
        """Парсинг котлет"""
        count = 2
        match = re.search(r'(\d+)\s*котлет', text)
        if match:
            count = int(match.group(1))
        
        weight = count * 75
        
        if 'куриные' in text:
            return [{'name': 'котлеты куриные', 'weight': weight}]
        else:
            return [{'name': 'котлеты', 'weight': weight}]
    
    def _parse_eggs(self, text):
        """Парсинг яиц"""
        count = 2
        match = re.search(r'(\d+)\s*яйц', text)
        if match:
            count = int(match.group(1))
        
        weight = count * 50
        
        products = [{'name': 'яйца', 'weight': weight}]
        if 'яичница' in text:
            products.append({'name': 'масло подсолнечное', 'weight': 10})
        return products
    
    def _parse_sandwich(self, text):
        """Парсинг бутерброда"""
        count = 1
        match = re.search(r'(\d+)\s*бутерброд', text)
        if match:
            count = int(match.group(1))
        
        products = []
        
        # Хлеб
        if 'черный' in text or 'ржаной' in text:
            products.append({'name': 'хлеб ржаной', 'weight': 30 * count})
        else:
            products.append({'name': 'хлеб белый', 'weight': 30 * count})
        
        # Колбаса
        if 'с колбасой' in text:
            if 'копченой' in text:
                products.append({'name': 'колбаса копченая', 'weight': 40 * count})
            else:
                products.append({'name': 'колбаса вареная', 'weight': 40 * count})
        
        # Масло
        if 'с маслом' in text:
            products.append({'name': 'масло сливочное', 'weight': 10 * count})
        
        return products
    
    def _parse_beer(self, text):
        """Парсинг пива"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 500
        
        if 'светлое' in text:
            return [{'name': 'пиво светлое', 'weight': weight}]
        elif 'темное' in text:
            return [{'name': 'пиво темное', 'weight': weight}]
        else:
            return [{'name': 'пиво светлое', 'weight': weight}]
    
    def _parse_coffee(self, text):
        """Парсинг кофе"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200
        
        products = [{'name': 'кофе', 'weight': weight}]
        
        # Сахар
        sugar_match = re.search(r'(\d+)\s*ложк[иа]?\s*сахар', text)
        if sugar_match:
            spoons = int(sugar_match.group(1))
            products.append({'name': 'сахар', 'weight': spoons * 7})
        elif 'сахар' in text and 'без сахара' not in text:
            products.append({'name': 'сахар', 'weight': 7})
        
        return products
    
    def _parse_tea(self, text):
        """Парсинг чая"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200
        
        products = [{'name': 'чай черный', 'weight': weight}]
        
        # Сахар
        sugar_match = re.search(r'(\d+)\s*ложк[иа]?\s*сахар', text)
        if sugar_match:
            spoons = int(sugar_match.group(1))
            products.append({'name': 'сахар', 'weight': spoons * 7})
        
        return products
    
    def _parse_simple_food(self, text):
        """Парсинг простого продукта"""
        weight = self._extract_weight(text)
        name = self._clean_name(text)
        
        if weight == 0:
            weight = self._guess_portion(name)
        
        return [{'name': name, 'weight': weight}]
    
    def _extract_weight(self, text):
        """Извлечение веса из текста"""
        # Форматы: 100г, 100 г, 100грамм, 200мл, 3л, 3 литра
        patterns = [
            (r'(\d+)\s*г(?:рамм)?', 1),      # 100г
            (r'(\d+)\s*мл', 1),               # 200мл
            (r'(\d+)\s*л(?:итр(?:а|ов)?)?', 1000),  # 3л -> *1000
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1)) * multiplier
        
        return 0
    
    def _clean_name(self, text):
        """Очистка названия от веса"""
        # Удаляем вес и единицы измерения
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*л(?:итр(?:а|ов)?)?', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        text = re.sub(r'\d+\s*ложк[иа]?', '', text)
        
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _guess_portion(self, name):
        """Стандартные порции"""
        portions = {
            'творог': 150,
            'молоко': 200,
            'кефир': 200,
            'йогурт': 150,
            'сметана': 20,
            'масло': 10,
            'хлеб': 30,
            'сыр': 30,
            'колбаса': 50,
            'яйца': 100,
            'яблоко': 150,
            'банан': 150,
            'апельсин': 150,
            'авокадо': 100,
            'картофель': 200,
            'гречка': 200,
            'рис': 200,
            'макароны': 200,
            'курица': 150,
            'говядина': 150,
            'свинина': 150,
            'рыба': 150,
            'лосось': 150,
            'арахис': 30,
            'орехи': 30,
            'кофе': 200,
            'чай': 200,
            'сахар': 7,
            'пиво': 500,
            'борщ': 300,
            'суп': 300,
            'салат': 200,
            'шашлык': 200,
            'пельмени': 200,
            'блины': 150,
            'котлеты': 150,
        }
        
        for key, portion in portions.items():
            if key in name:
                return portion
        
        return 100