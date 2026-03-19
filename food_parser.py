import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """Улучшенный парсинг сообщения с продуктами"""
        # Разделяем сообщение на отдельные продукты по запятым или союзам
        # Теперь учитываем, что в одном сообщении может быть несколько блюд
        
        # Сначала пробуем разделить по запятым
        if ',' in text:
            lines = text.split(',')
        else:
            # Если запятых нет, пробуем разделить по союзам "и", "а также"
            lines = re.split(r'\s+и\s+|\s+а также\s+|\s+плюс\s+', text.lower())
        
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Проверяем, содержит ли строка несколько блюд (например, "4 яйца, 2 бутерброда")
            if self._contains_multiple_items(line):
                items = self._split_multiple_items(line)
                for item in items:
                    results.extend(self._parse_single_item(item))
            else:
                results.extend(self._parse_single_item(line))
        
        return results
    
    def _contains_multiple_items(self, text):
        """Проверка, содержит ли строка несколько блюд"""
        # Ищем числа перед словами (яйца, бутерброда, порции и т.д.)
        patterns = [
            r'\d+\s*(?:шт|яйц[ао]|бутерброд|порци|куск|ломтик)',
            r'\d+\s+разных',
            r'\d+\s+вида',
        ]
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text)
            count += len(matches)
        return count > 1
    
    def _split_multiple_items(self, text):
        """Разделение строки с несколькими блюдами"""
        # Ищем числа с последующими словами
        items = []
        current_pos = 0
        
        # Паттерн для поиска: число + пробел + слово (яйца, бутерброда и т.д.)
        pattern = r'(\d+)\s*(?:шт\s*)?([а-я]+(?:[а-я]*))'
        
        matches = list(re.finditer(pattern, text))
        
        for i, match in enumerate(matches):
            start = match.start()
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(text)
            
            item_text = text[start:end].strip()
            items.append(item_text)
        
        return items if items else [text]
    
    def _parse_single_item(self, text):
        """Парсинг одного продукта или блюда"""
        text = text.lower().strip()
        
        # Проверяем специальные случаи
        if 'яичница' in text or 'яйца' in text or 'яйцо' in text:
            return self._parse_eggs_dish(text)
        elif 'бутерброд' in text or 'сэндвич' in text:
            return self._parse_sandwich(text)
        elif 'кофе' in text:
            return self._parse_coffee(text)
        elif 'пиво' in text:
            return self._parse_beer(text)
        elif 'салат' in text:
            return self._parse_salad(text)
        elif 'суп' in text or 'борщ' in text or 'щи' in text:
            return self._parse_soup(text)
        elif 'шашлык' in text:
            return self._parse_shashlik(text)
        elif 'пельмени' in text:
            return self._parse_pelmeni(text)
        elif 'блины' in text:
            return self._parse_blini(text)
        elif 'котлеты' in text:
            return self._parse_cutlets(text)
        else:
            # Обычный продукт
            return self._parse_simple_food(text)
    
    def _parse_eggs_dish(self, text):
        """Парсинг яичницы и яиц"""
        products = []
        
        # Ищем количество яиц
        eggs_count = 2  # по умолчанию 2 яйца
        count_match = re.search(r'(\d+)\s*(?:шт|яйц|яиц|яйца)', text)
        if count_match:
            eggs_count = int(count_match.group(1))
        
        # Вес одного яйца примерно 50г
        eggs_weight = eggs_count * 50
        products.append({'name': 'яйца', 'weight': eggs_weight})
        
        # Если это яичница, добавляем масло
        if 'яичница' in text or 'глазунья' in text or 'омлет' in text:
            products.append({'name': 'масло подсолнечное', 'weight': 10})
        
        # Если есть дополнительные ингредиенты
        if 'с помидорами' in text:
            products.append({'name': 'помидор', 'weight': 50})
        if 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 30})
        if 'с беконом' in text:
            products.append({'name': 'бекон', 'weight': 30})
        if 'с колбасой' in text:
            if 'копченой' in text:
                products.append({'name': 'колбаса копченая', 'weight': 40})
            else:
                products.append({'name': 'колбаса вареная', 'weight': 40})
        
        return products
    
    def _parse_sandwich(self, text):
        """Парсинг бутерброда"""
        products = []
        
        # Определяем количество бутербродов
        sandwich_count = 1
        count_match = re.search(r'(\d+)\s*(?:шт|бутерброд)', text)
        if count_match:
            sandwich_count = int(count_match.group(1))
        
        # Основа - хлеб (30г на бутерброд)
        if 'черный' in text or 'ржаной' in text:
            bread_name = 'хлеб ржаной'
        elif 'зерновой' in text or 'цельнозерновой' in text:
            bread_name = 'хлеб цельнозерновой'
        else:
            bread_name = 'хлеб белый'
        
        products.append({'name': bread_name, 'weight': 30 * sandwich_count})
        
        # Масло (10г на бутерброд)
        if 'с маслом' in text or 'с маслицем' in text:
            products.append({'name': 'масло сливочное', 'weight': 10 * sandwich_count})
        
        # Колбаса (40г на бутерброд)
        if 'с колбасой' in text:
            if 'копченой' in text:
                products.append({'name': 'колбаса копченая', 'weight': 40 * sandwich_count})
            elif 'вареной' in text or 'докторской' in text:
                products.append({'name': 'колбаса вареная', 'weight': 40 * sandwich_count})
            else:
                # Если не указано, по умолчанию копченая (чаще так и говорят)
                products.append({'name': 'колбаса копченая', 'weight': 40 * sandwich_count})
        
        # Сыр (25г на бутерброд)
        if 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 25 * sandwich_count})
        
        # Ветчина (30г на бутерброд)
        if 'с ветчиной' in text:
            products.append({'name': 'ветчина', 'weight': 30 * sandwich_count})
        
        # Рыба (30г на бутерброд)
        if 'с рыбой' in text or 'с лососем' in text or 'с семгой' in text:
            products.append({'name': 'лосось', 'weight': 30 * sandwich_count})
        
        # Икра (15г на бутерброд)
        if 'с икрой' in text:
            products.append({'name': 'икра красная', 'weight': 15 * sandwich_count})
        
        # Авокадо (30г на бутерброд)
        if 'с авокадо' in text:
            products.append({'name': 'авокадо', 'weight': 30 * sandwich_count})
        
        return products
    
    def _parse_coffee(self, text):
        """Парсинг кофе"""
        products = []
        
        # Основа - кофе (200мл)
        coffee_type = 'кофе'
        if 'растворимый' in text:
            coffee_type = 'кофе растворимый'
        elif 'эспрессо' in text:
            coffee_type = 'кофе эспрессо'
            products.append({'name': coffee_type, 'weight': 50})
        elif 'капучино' in text:
            coffee_type = 'кофе капучино'
            products.append({'name': coffee_type, 'weight': 200})
        elif 'латте' in text:
            coffee_type = 'кофе латте'
            products.append({'name': coffee_type, 'weight': 250})
        elif 'американо' in text:
            coffee_type = 'кофе американо'
            products.append({'name': coffee_type, 'weight': 200})
        else:
            products.append({'name': coffee_type, 'weight': 200})
        
        # Сахар
        sugar_match = re.search(r'(\d+)\s*(?:ложк|ч.л|чайных|ст.л)', text)
        if sugar_match:
            sugar_spoons = int(sugar_match.group(1))
            products.append({'name': 'сахар', 'weight': sugar_spoons * 7})
        elif 'сахар' in text and not re.search(r'без сахара', text):
            # Если просто сказано "с сахаром", добавляем 1 ложку
            products.append({'name': 'сахар', 'weight': 7})
        
        # Молоко или сливки
        if 'с молоком' in text:
            products.append({'name': 'молоко 2.5%', 'weight': 50})
        elif 'со сливками' in text:
            products.append({'name': 'сливки 20%', 'weight': 30})
        
        return products
    
    def _parse_beer(self, text):
        """Парсинг пива"""
        # Ищем объем
        volume = 500  # по умолчанию 500мл
        
        volume_match = re.search(r'(\d+)\s*(?:мл|л|литр)', text)
        if volume_match:
            vol_value = int(volume_match.group(1))
            if 'л' in text and 'мл' not in text:
                volume = vol_value * 1000
            else:
                volume = vol_value
        
        # Ищем количество бутылок/банок
        bottles_match = re.search(r'(\d+)\s*(?:бут|банк|шт)', text)
        if bottles_match:
            bottles = int(bottles_match.group(1))
            volume = volume * bottles
        
        # Определяем тип пива
        if 'светлое' in text:
            beer_name = 'пиво светлое'
        elif 'темное' in text:
            beer_name = 'пиво темное'
        elif 'живое' in text:
            beer_name = 'пиво живое'
        elif 'безалкогольное' in text:
            beer_name = 'пиво безалкогольное'
        else:
            beer_name = 'пиво светлое'
        
        return [{'name': beer_name, 'weight': volume}]
    
    def _parse_simple_food(self, text):
        """Парсинг простого продукта"""
        # Ищем вес
        weight = self._extract_weight(text)
        
        # Очищаем название от веса
        food_name = self._clean_name(text)
        
        # Если вес не указан, используем стандартную порцию
        if weight == 0:
            food = self.db.find_food(food_name)
            weight = self._guess_portion(food_name, food)
        
        return [{'name': food_name, 'weight': weight}]
    
    def _parse_salad(self, text):
        """Парсинг салата"""
        if 'оливье' in text:
            return [
                {'name': 'колбаса вареная', 'weight': 50},
                {'name': 'картофель', 'weight': 50},
                {'name': 'яйца', 'weight': 40},
                {'name': 'огурцы соленые', 'weight': 30},
                {'name': 'морковь вареная', 'weight': 30},
                {'name': 'горошек консервированный', 'weight': 30},
                {'name': 'майонез', 'weight': 30}
            ]
        elif 'цезарь' in text:
            result = [
                {'name': 'куриная грудка', 'weight': 50},
                {'name': 'салат', 'weight': 50},
                {'name': 'сыр пармезан', 'weight': 15},
                {'name': 'сухарики', 'weight': 20}
            ]
            if 'с соусом' in text:
                result.append({'name': 'соус цезарь', 'weight': 30})
            return result
        elif 'греческий' in text:
            return [
                {'name': 'помидор', 'weight': 50},
                {'name': 'огурец', 'weight': 50},
                {'name': 'перец болгарский', 'weight': 30},
                {'name': 'лук красный', 'weight': 15},
                {'name': 'сыр фета', 'weight': 40},
                {'name': 'маслины', 'weight': 20},
                {'name': 'масло оливковое', 'weight': 10}
            ]
        else:
            return [{'name': 'салат', 'weight': 150}]
    
    def _parse_soup(self, text):
        """Парсинг супа"""
        if 'борщ' in text:
            products = [
                {'name': 'борщ', 'weight': 300}
            ]
            if 'со сметаной' in text:
                products.append({'name': 'сметана 20%', 'weight': 20})
            return products
        elif 'щи' in text:
            return [{'name': 'щи', 'weight': 300}]
        elif 'солянка' in text:
            return [{'name': 'солянка', 'weight': 300}]
        elif 'окрошка' in text:
            return [{'name': 'окрошка', 'weight': 300}]
        elif 'уха' in text:
            return [{'name': 'уха', 'weight': 300}]
        else:
            return [{'name': 'суп', 'weight': 300}]
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        weight = self._extract_weight(text) or 200
        
        if 'свинина' in text or 'свиной' in text:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
        elif 'говядина' in text or 'говяжий' in text:
            return [{'name': 'шашлык из говядины', 'weight': weight}]
        elif 'курица' in text or 'куриный' in text:
            return [{'name': 'шашлык из курицы', 'weight': weight}]
        elif 'баранина' in text or 'бараний' in text:
            return [{'name': 'шашлык из баранины', 'weight': weight}]
        else:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
    
    def _parse_pelmeni(self, text):
        """Парсинг пельменей"""
        weight = self._extract_weight(text) or 200
        return [{'name': 'пельмени', 'weight': weight}]
    
    def _parse_blini(self, text):
        """Парсинг блинов"""
        count = 3  # по умолчанию 3 блина
        count_match = re.search(r'(\d+)\s*(?:блин|шт)', text)
        if count_match:
            count = int(count_match.group(1))
        
        weight = count * 50  # 1 блин ~50г
        
        if 'с мясом' in text:
            return [{'name': 'блины с мясом', 'weight': weight}]
        elif 'с творогом' in text:
            return [{'name': 'блины с творогом', 'weight': weight}]
        elif 'с икрой' in text:
            return [{'name': 'блины с икрой', 'weight': weight}]
        else:
            return [{'name': 'блины', 'weight': weight}]
    
    def _parse_cutlets(self, text):
        """Парсинг котлет"""
        count = 2  # по умолчанию 2 котлеты
        count_match = re.search(r'(\d+)\s*(?:котлет|шт)', text)
        if count_match:
            count = int(count_match.group(1))
        
        weight = count * 75  # 1 котлета ~75г
        
        if 'куриные' in text:
            return [{'name': 'котлеты куриные', 'weight': weight}]
        elif 'рыбные' in text:
            return [{'name': 'котлеты рыбные', 'weight': weight}]
        else:
            return [{'name': 'котлеты', 'weight': weight}]
    
    def _extract_weight(self, text):
        """Извлечение веса из текста"""
        patterns = [
            r'(\d+)\s*г(?:рамм)?',  # 100г, 100 г, 100грамм
            r'(\d+)\s*мл',           # 200мл, 200 мл
            r'(\d+)\s*л(?:итров?)?', # 1л, 2 литра
            r'(\d+)\s*шт',           # 2шт, 2 шт
            r'(\d+)\s*куск',         # 2 куска
            r'(\d+)\s*порц',         # 2 порции
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                # Для литров конвертируем в мл
                if 'л' in pattern and 'мл' not in pattern:
                    return value * 1000
                return value
        
        return 0
    
    def _clean_name(self, text):
        """Очистка названия от веса и других числовых значений"""
        # Удаляем вес и единицы измерения
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*л(?:итров?)?', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        text = re.sub(r'\d+\s*куск', '', text)
        text = re.sub(r'\d+\s*порц', '', text)
        text = re.sub(r'\d+\s*ложк[иа]?', '', text)
        text = re.sub(r'\d+%', '', text)
        
        # Удаляем предлоги и лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(с |со |из |на |в |для |и |или )', ' ', text)
        
        return text.strip()
    
    def _guess_portion(self, food_name, food=None):
        """Угадывание стандартной порции"""
        # Сначала проверяем, есть ли стандартная порция в базе
        if food and food.default_portion:
            return food.default_portion
        
        # Если нет, используем эвристику
        portions = {
            'кофе': 200,
            'чай': 200,
            'сок': 200,
            'компот': 200,
            'кисель': 200,
            'квас': 250,
            'лимонад': 250,
            'кола': 250,
            'пиво': 500,
            'вино': 150,
            'водка': 50,
            'коньяк': 50,
            'виски': 50,
            'йогурт': 150,
            'творог': 150,
            'кефир': 200,
            'молоко': 200,
            'ряженка': 200,
            'сметана': 20,
            'сливки': 20,
            'масло сливочное': 10,
            'масло растительное': 10,
            'хлеб': 30,
            'батон': 30,
            'лаваш': 50,
            'яйца': 50,
            'яблоко': 150,
            'банан': 150,
            'апельсин': 150,
            'мандарин': 100,
            'груша': 150,
            'виноград': 150,
            'клубника': 150,
            'картофель': 200,
            'пюре': 200,
            'мясо': 150,
            'рыба': 150,
            'каша': 200,
            'гречка': 200,
            'рис': 200,
            'макароны': 200,
            'паста': 200,
            'суп': 300,
            'борщ': 300,
            'щи': 300,
            'солянка': 300,
            'окрошка': 300,
            'пельмени': 200,
            'вареники': 200,
            'блины': 150,
            'оладьи': 150,
            'сырники': 150,
            'котлеты': 150,
            'шашлык': 200,
            'бургер': 200,
            'пицца': 200,
            'шаурма': 300,
            'хот-дог': 150,
            'картошка фри': 150,
            'наггетсы': 100,
            'суши': 200,
            'роллы': 200,
            'сыр': 30,
            'колбаса': 50,
            'сосиски': 50,
            'ветчина': 50,
            'салат': 200,
            'оливье': 200,
            'цезарь': 200,
            'винегрет': 200,
            'греческий': 200,
            'печенье': 30,
            'шоколад': 20,
            'конфеты': 15,
            'вафли': 30,
            'халва': 30,
            'зефир': 30,
            'мармелад': 30,
            'варенье': 20,
            'мед': 20,
            'сахар': 7,
            'орехи': 30,
            'семечки': 30,
        }
        
        for key, portion in portions.items():
            if key in food_name:
                return portion
        
        return 100  # По умолчанию 100г