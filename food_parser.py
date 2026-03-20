import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """
        ЕДИНЫЙ парсер для ЛЮБЫХ продуктов
        Правила:
        1. Разделяем запрос на отдельные продукты по запятым
        2. Для каждого продукта определяем название и вес
        3. Если вес не указан - берем стандартную порцию
        4. Если продукт не найден в БД - всё равно считаем по стандартной порции
        """
        # Подготовка текста
        text = text.lower().strip()
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        # Разделяем на отдельные продукты
        parts = [p.strip() for p in text.split(',') if p.strip()]
        results = []
        
        for part in parts:
            # Обрабатываем каждый продукт
            products = self._parse_single_product(part)
            results.extend(products)
        
        return results
    
    def _parse_single_product(self, text):
        """
        УНИВЕРСАЛЬНЫЙ метод для парсинга ОДНОГО продукта
        Работает для ЛЮБЫХ форматов:
        - "авокадо 100 гр"
        - "100 гр авокадо"
        - "авокадо"
        - "2 ложки сахара"
        - "кофе 200 мл"
        - "3 литра пива"
        """
        # ШАГ 1: Проверяем особые случаи (сложные блюда)
        special_cases = [
            ('салат оливье', 'салат оливье', 200),
            ('салат цезарь', 'салат цезарь', 200),
            ('салат греческий', 'салат греческий', 200),
            ('борщ', self._parse_borscht, None),
            ('щи', 'щи', 300),
            ('солянка', 'солянка', 300),
            ('окрошка', 'окрошка', 300),
            ('шашлык', self._parse_shashlik, None),
            ('пельмени', 'пельмени', 200),
            ('вареники', 'вареники', 200),
            ('блины', self._parse_pancakes, None),
            ('котлеты', self._parse_cutlets, None),
            ('яичница', self._parse_eggs, None),
            ('яйца', self._parse_eggs, None),
            ('бутерброд', self._parse_sandwich, None),
        ]
        
        for keyword, handler, default_weight in special_cases:
            if keyword in text:
                if callable(handler):
                    return handler(text)
                else:
                    return self._create_product(handler, text, default_weight)
        
        # ШАГ 2: Извлекаем вес из текста (ЕДИНЫЙ метод для всего)
        weight_info = self._extract_weight_universal(text)
        
        if weight_info:
            # Вес найден
            weight, clean_text = weight_info
            product_name = clean_text.strip()
            
            # Проверяем, не осталось ли чего-то в названии
            if not product_name:
                return []
            
            # Создаем продукт с найденным весом
            return [{'name': product_name, 'weight': weight}]
        else:
            # Вес не найден - берем стандартную порцию
            product_name = text.strip()
            weight = self._get_standard_portion(product_name)
            return [{'name': product_name, 'weight': weight}]
    
    def _extract_weight_universal(self, text):
        """
        УНИВЕРСАЛЬНОЕ извлечение веса из текста
        Понимает ЛЮБЫЕ форматы:
        - "100г", "100 гр", "100 грамм"
        - "200 мл", "200мл"
        - "3л", "3 литра", "3 литра"
        - "2 ложки"
        - "50 гр" в начале, середине или конце
        """
        # Паттерны для разных единиц измерения
        patterns = [
            # Граммы: 100г, 100 г, 100 грамм, 100гр
            (r'(\d+)\s*г(?:рамм|р)?', 1, 'г'),
            # Миллилитры: 200мл, 200 мл
            (r'(\d+)\s*мл', 1, 'мл'),
            # Литры: 3л, 3 л, 3 литра
            (r'(\d+(?:\.\d+)?)\s*л(?:итр(?:а|ов)?)?', 1000, 'л'),
            # Ложки: 2 ложки, 3 ложек
            (r'(\d+)\s*ложк[иае]', 1, 'ложка'),
        ]
        
        for pattern, multiplier, unit in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                weight = int(value * multiplier)
                
                # Специальная обработка для ложек сахара
                if unit == 'ложка' and 'сахар' in text:
                    # Ложка сахара = 7г
                    weight = int(value * 7)
                    # Удаляем информацию о ложках из текста
                    clean_text = re.sub(r'\d+\s*ложк[иае].*?сахар', '', text)
                    clean_text = re.sub(r'\d+\s*ложк[иае]', '', clean_text)
                    return weight, clean_text
                
                # Для остальных случаев - удаляем информацию о весе
                clean_text = re.sub(pattern, '', text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                # Если после очистки ничего не осталось, ищем название рядом
                if not clean_text:
                    # Пробуем найти слово до или после числа
                    words = text.split()
                    for i, word in enumerate(words):
                        if re.search(r'\d+', word):
                            if i > 0:
                                clean_text = words[i-1]
                            elif i < len(words)-1:
                                clean_text = words[i+1]
                            break
                
                return weight, clean_text
        
        return None
    
    def _get_standard_portion(self, product_name):
        """
        Стандартные порции для популярных продуктов
        Если продукт неизвестен - возвращает 100г
        """
        portions = {
            # Фрукты
            'авокадо': 100,
            'яблоко': 150,
            'банан': 150,
            'апельсин': 150,
            'мандарин': 100,
            'груша': 150,
            'киви': 100,
            'лимон': 50,
            
            # Овощи
            'помидор': 100,
            'огурец': 100,
            'картофель': 200,
            'морковь': 100,
            'лук': 50,
            'чеснок': 10,
            'капуста': 150,
            'брокколи': 150,
            'перец': 100,
            'кабачок': 200,
            'баклажан': 200,
            'тыква': 200,
            'свекла': 150,
            
            # Молочные
            'творог': 150,
            'молоко': 200,
            'кефир': 200,
            'йогурт': 150,
            'сметана': 20,
            'сливки': 20,
            'сыр': 30,
            'масло сливочное': 10,
            
            # Мясо
            'курица': 150,
            'говядина': 150,
            'свинина': 150,
            'баранина': 150,
            'индейка': 150,
            'печень': 100,
            
            # Рыба
            'рыба': 150,
            'лосось': 150,
            'семга': 150,
            'форель': 150,
            'скумбрия': 150,
            'сельдь': 100,
            'треска': 150,
            
            # Колбасные
            'колбаса': 50,
            'сосиски': 50,
            'ветчина': 50,
            'бекон': 30,
            'сало': 30,
            
            # Крупы
            'гречка': 200,
            'рис': 200,
            'овсянка': 200,
            'каша': 200,
            'макароны': 200,
            'паста': 200,
            'спагетти': 200,
            
            # Напитки
            'кофе': 200,
            'чай': 200,
            'пиво': 500,
            'вино': 150,
            'сок': 200,
            
            # Орехи
            'арахис': 30,
            'орехи': 30,
            'миндаль': 30,
            'фундук': 30,
            'кешью': 30,
            'фисташки': 30,
            
            # Хлеб
            'хлеб': 30,
            'батон': 30,
            'лаваш': 50,
            
            # Яйца
            'яйцо': 50,
            'яйца': 100,
            
            # Готовые блюда
            'суп': 300,
            'борщ': 300,
            'салат': 200,
            'шашлык': 200,
            'пельмени': 200,
            'блины': 150,
            'котлеты': 150,
            
            # Сладости
            'шоколад': 20,
            'конфеты': 15,
            'печенье': 30,
            'сахар': 7,
            'мед': 20,
        }
        
        # Ищем по ключевым словам
        for key, portion in portions.items():
            if key in product_name:
                return portion
        
        # Если ничего не нашли - 100г по умолчанию
        return 100
    
    def _create_product(self, name, text, default_weight):
        """Создает продукт с извлеченным или стандартным весом"""
        weight_info = self._extract_weight_universal(text)
        if weight_info:
            weight, _ = weight_info
        else:
            weight = default_weight
        return [{'name': name, 'weight': weight}]
    
    def _parse_borscht(self, text):
        """Парсинг борща"""
        weight_info = self._extract_weight_universal(text)
        weight = weight_info[0] if weight_info else 300
        
        products = [{'name': 'борщ', 'weight': weight}]
        if 'со сметаной' in text:
            products.append({'name': 'сметана 20%', 'weight': 20})
        return products
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        weight_info = self._extract_weight_universal(text)
        weight = weight_info[0] if weight_info else 200
        
        if 'свинина' in text:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
        elif 'курица' in text:
            return [{'name': 'шашлык из курицы', 'weight': weight}]
        else:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
    
    def _parse_pancakes(self, text):
        """Парсинг блинов"""
        # Ищем количество
        count_match = re.search(r'(\d+)\s*блин', text)
        count = int(count_match.group(1)) if count_match else 3
        
        weight = count * 50
        
        if 'с мясом' in text:
            return [{'name': 'блины с мясом', 'weight': weight}]
        elif 'с творогом' in text:
            return [{'name': 'блины с творогом', 'weight': weight}]
        else:
            return [{'name': 'блины', 'weight': weight}]
    
    def _parse_cutlets(self, text):
        """Парсинг котлет"""
        count_match = re.search(r'(\d+)\s*котлет', text)
        count = int(count_match.group(1)) if count_match else 2
        
        weight = count * 75
        
        if 'куриные' in text:
            return [{'name': 'котлеты куриные', 'weight': weight}]
        else:
            return [{'name': 'котлеты', 'weight': weight}]
    
    def _parse_eggs(self, text):
        """Парсинг яиц"""
        count_match = re.search(r'(\d+)\s*яйц', text)
        count = int(count_match.group(1)) if count_match else 2
        
        weight = count * 50
        
        products = [{'name': 'яйца', 'weight': weight}]
        if 'яичница' in text:
            products.append({'name': 'масло подсолнечное', 'weight': 10})
        return products
    
    def _parse_sandwich(self, text):
        """Парсинг бутерброда"""
        count_match = re.search(r'(\d+)\s*бутерброд', text)
        count = int(count_match.group(1)) if count_match else 1
        
        products = []
        
        # Хлеб
        if 'черный' in text:
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
        
        # Сыр
        if 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 25 * count})
        
        return products