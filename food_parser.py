import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """Улучшенный парсинг сообщения с продуктами"""
        # Нормализуем текст
        text = text.lower().strip()
        
        # Заменяем разные варианты написания
        text = text.replace(' гр ', ' г ').replace(' грамм ', ' г ')
        text = text.replace(' литр ', ' л ').replace(' литра ', ' л ').replace(' литров ', ' л ')
        
        # Разделяем по запятым, но сохраняем числа
        results = []
        
        # Сначала пробуем разделить по запятым
        if ',' in text:
            parts = text.split(',')
        else:
            # Если запятых нет, пробуем разделить по союзам
            parts = re.split(r'\s+и\s+|\s+а также\s+|\s+плюс\s+', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Обрабатываем каждую часть
            items = self._parse_part(part)
            results.extend(items)
        
        return results
    
    def _parse_part(self, text):
        """Парсинг одной части сообщения"""
        # Проверяем, содержит ли часть несколько продуктов (например, "пиво 3 литра и арахис")
        if ' и ' in text and not self._is_complex_dish(text):
            # Разделяем по "и"
            subparts = text.split(' и ')
            items = []
            for subpart in subparts:
                items.extend(self._parse_single_item(subpart))
            return items
        
        # Если это одно блюдо или продукт
        return self._parse_single_item(text)
    
    def _parse_single_item(self, text):
        """Парсинг одного продукта или блюда"""
        text = text.strip()
        if not text:
            return []
        
        # Сначала ищем вес
        weight_info = self._extract_weight_and_product(text)
        if weight_info:
            product_name, weight = weight_info
            # Проверяем, является ли продукт сложным блюдом
            if self._is_complex_dish(product_name):
                return self._parse_complex_dish_with_weight(product_name, weight)
            else:
                return [{'name': product_name, 'weight': weight}]
        
        # Если вес не найден, проверяем сложные блюда
        if self._is_complex_dish(text):
            return self._parse_complex_dish(text)
        
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
        elif 'арахис' in text or 'орехи' in text:
            return self._parse_nuts(text)
        else:
            # Обычный продукт
            return self._parse_simple_food(text)
    
    def _extract_weight_and_product(self, text):
        """Извлечение веса и названия продукта из текста"""
        # Паттерны для разных форматов: "3 литра пива", "пиво 3 литра", "100 гр арахиса"
        patterns = [
            # Формат: "100 гр арахиса" (вес перед продуктом)
            r'(\d+)\s*(?:г|гр|грамм|мл|л|литр(?:а|ов)?)\s+([а-я]+(?:[а-я\s]*[а-я])?)',
            # Формат: "арахис 100 гр" (продукт перед весом)
            r'([а-я]+(?:[а-я\s]*[а-я])?)\s+(\d+)\s*(?:г|гр|грамм|мл|л|литр(?:а|ов)?)',
            # Формат: "3 литра пива" (вес с единицей перед продуктом)
            r'(\d+)\s*(?:л|литр(?:а|ов)?)\s+([а-я]+(?:[а-я\s]*[а-я])?)',
            # Формат: "пива 3 литра" (продукт в родительном падеже перед весом)
            r'([а-я]+[а-я]?[а-я]?)\s+(\d+)\s*(?:л|литр(?:а|ов)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # Определяем, где число, а где название
                    if groups[0].isdigit():
                        weight = float(groups[0])
                        product = groups[1].strip()
                    elif groups[1].isdigit():
                        weight = float(groups[1])
                        product = groups[0].strip()
                    else:
                        continue
                    
                    # Конвертируем литры в мл для жидкостей
                    if 'л' in text and 'мл' not in text:
                        weight = weight * 1000
                    
                    return product, weight
        
        return None
    
    def _parse_nuts(self, text):
        """Парсинг орехов"""
        # Проверяем наличие веса
        weight_info = self._extract_weight_and_product(text)
        if weight_info:
            product_name, weight = weight_info
            # Уточняем название
            if 'арахис' in product_name:
                if 'соленый' in text:
                    return [{'name': 'арахис соленый', 'weight': weight}]
                return [{'name': 'арахис', 'weight': weight}]
            elif 'грецкие' in text:
                return [{'name': 'грецкие орехи', 'weight': weight}]
            elif 'миндаль' in text:
                return [{'name': 'миндаль', 'weight': weight}]
            elif 'фундук' in text:
                return [{'name': 'фундук', 'weight': weight}]
            elif 'кешью' in text:
                return [{'name': 'кешью', 'weight': weight}]
            elif 'фисташки' in text:
                return [{'name': 'фисташки', 'weight': weight}]
            elif 'кедровые' in text:
                return [{'name': 'кедровые орехи', 'weight': weight}]
        
        # Если вес не указан, ищем его в тексте
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 30  # стандартная порция орехов
        
        # Определяем тип орехов
        if 'арахис' in text:
            if 'соленый' in text:
                return [{'name': 'арахис соленый', 'weight': weight}]
            return [{'name': 'арахис', 'weight': weight}]
        elif 'грецкие' in text:
            return [{'name': 'грецкие орехи', 'weight': weight}]
        elif 'миндаль' in text:
            return [{'name': 'миндаль', 'weight': weight}]
        elif 'фундук' in text:
            return [{'name': 'фундук', 'weight': weight}]
        elif 'кешью' in text:
            return [{'name': 'кешью', 'weight': weight}]
        elif 'фисташки' in text:
            return [{'name': 'фисташки', 'weight': weight}]
        elif 'кедровые' in text:
            return [{'name': 'кедровые орехи', 'weight': weight}]
        else:
            return [{'name': 'арахис', 'weight': weight}]
    
    def _parse_beer(self, text):
        """Парсинг пива"""
        # Проверяем наличие объема через weight_info
        weight_info = self._extract_weight_and_product(text)
        if weight_info:
            product_name, volume = weight_info
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
        
        # Если не нашли через weight_info, ищем объем обычным способом
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
    
    def _parse_complex_dish_with_weight(self, dish_name, weight):
        """Парсинг сложного блюда с указанным весом"""
        # Для сложных блюд вес обычно относится ко всему блюду целиком
        if 'борщ' in dish_name:
            return [{'name': 'борщ', 'weight': weight}]
        elif 'щи' in dish_name:
            return [{'name': 'щи', 'weight': weight}]
        elif 'солянка' in dish_name:
            return [{'name': 'солянка', 'weight': weight}]
        elif 'окрошка' in dish_name:
            return [{'name': 'окрошка', 'weight': weight}]
        elif 'салат' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'суп' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'пельмени' in dish_name:
            return [{'name': 'пельмени', 'weight': weight}]
        elif 'вареники' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'блины' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'котлеты' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'шашлык' in dish_name:
            return self._parse_shashlik(dish_name + f" {weight}г")
        
        return [{'name': dish_name, 'weight': weight}]
    
    def _is_complex_dish(self, text):
        """Проверка, является ли блюдо сложным"""
        complex_dishes = [
            'борщ', 'щи', 'солянка', 'окрошка', 'рассольник', 'уха',
            'бутерброд', 'сэндвич', 'салат', 'суп', 'шашлык',
            'пюре', 'каша', 'макароны', 'пельмени', 'вареники',
            'блины', 'оладьи', 'сырники', 'котлеты', 'тефтели',
            'пицца', 'бургер', 'шаурма', 'хот-дог'
        ]
        return any(dish in text for dish in complex_dishes)
    
    def _parse_complex_dish(self, text):
        """Парсинг сложного блюда без указания веса"""
        if 'борщ' in text:
            products = [{'name': 'борщ', 'weight': 300}]
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
        elif 'салат' in text:
            return self._parse_salad(text)
        elif 'суп' in text:
            return [{'name': 'суп', 'weight': 300}]
        elif 'шашлык' in text:
            return self._parse_shashlik(text)
        elif 'пельмени' in text:
            return self._parse_pelmeni(text)
        elif 'блины' in text:
            return self._parse_blini(text)
        elif 'котлеты' in text:
            return self._parse_cutlets(text)
        else:
            return [{'name': text, 'weight': 200}]
    
    def _parse_eggs_dish(self, text):
        """Парсинг яичницы и яиц"""
        products = []
        
        # Ищем количество яиц
        eggs_count = 2  # по умолчанию 2 яйца
        
        # Проверяем разные форматы: "4 яйца", "яйца 4шт", "4шт яиц"
        count_match = re.search(r'(\d+)\s*(?:шт|яйц|яиц|яйца)', text)
        if count_match:
            eggs_count = int(count_match.group(1))
        else:
            # Пробуем найти просто число перед словом "яйца"
            count_match = re.search(r'(\d+)\s+яйц', text)
            if count_match:
                eggs_count = int(count_match.group(1))
        
        # Вес одного яйца примерно 50г
        eggs_weight = eggs_count * 50
        products.append({'name': 'яйца', 'weight': eggs_weight})
        
        # Если это яичница, добавляем масло
        if 'яичница' in text or 'глазунья' in text or 'омлет' in text:
            products.append({'name': 'масло подсолнечное', 'weight': 10})
        
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
                # Если не указано, по умолчанию вареная
                products.append({'name': 'колбаса вареная', 'weight': 40 * sandwich_count})
        
        # Сыр (25г на бутерброд)
        if 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 25 * sandwich_count})
        
        return products
    
    def _parse_coffee(self, text):
        """Парсинг кофе"""
        products = []
        
        # Проверяем наличие объема
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200  # стандартная чашка
        
        coffee_type = 'кофе'
        if 'растворимый' in text:
            coffee_type = 'кофе растворимый'
        elif 'эспрессо' in text:
            coffee_type = 'кофе эспрессо'
        elif 'капучино' in text:
            coffee_type = 'кофе капучино'
        elif 'латте' in text:
            coffee_type = 'кофе латте'
        elif 'американо' in text:
            coffee_type = 'кофе американо'
        
        products.append({'name': coffee_type, 'weight': weight})
        
        # Сахар
        sugar_match = re.search(r'(\d+)\s*(?:ложк|ч.л|чайных)', text)
        if sugar_match:
            sugar_spoons = int(sugar_match.group(1))
            products.append({'name': 'сахар', 'weight': sugar_spoons * 7})
        elif 'сахар' in text and 'без сахара' not in text:
            # Если просто сказано "с сахаром", добавляем 1 ложку
            products.append({'name': 'сахар', 'weight': 7})
        
        return products
    
    def _parse_salad(self, text):
        """Парсинг салата"""
        if 'оливье' in text:
            return [{'name': 'салат оливье', 'weight': 200}]
        elif 'цезарь' in text:
            return [{'name': 'салат цезарь', 'weight': 200}]
        elif 'греческий' in text:
            return [{'name': 'салат греческий', 'weight': 200}]
        elif 'винегрет' in text:
            return [{'name': 'винегрет', 'weight': 200}]
        else:
            return [{'name': 'салат', 'weight': 150}]
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200
        
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
        weight = self._extract_weight(text)
        if weight == 0:
            weight = 200
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
    
    def _parse_simple_food(self, text):
        """Парсинг простого продукта"""
        # Сначала пробуем найти продукт в базе
        food = self.db.find_food(text)
        
        # Ищем вес
        weight = self._extract_weight(text)
        
        # Если вес не указан, используем стандартную порцию
        if weight == 0:
            weight = self._guess_portion(text, food)
        
        # Если продукт не найден в базе, пробуем найти по ключевым словам
        if not food:
            food = self._find_by_keywords(text)
            if food:
                return [{'name': food.name_ru, 'weight': weight}]
        
        # Возвращаем исходное название
        return [{'name': text, 'weight': weight}]
    
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
    
    def _guess_portion(self, food_name, food=None):
        """Угадывание стандартной порции"""
        if food and food.default_portion:
            return food.default_portion
        
        portions = {
            'арахис': 30,
            'арахис соленый': 30,
            'орехи': 30,
            'грецкие орехи': 30,
            'миндаль': 30,
            'фундук': 30,
            'кешью': 30,
            'фисташки': 30,
            'кедровые орехи': 20,
            'пиво': 500,
            'пиво светлое': 500,
            'пиво темное': 500,
            'пиво живое': 500,
            'пиво безалкогольное': 500,
            'кофе': 200,
            'чай': 200,
            'сок': 200,
            'компот': 200,
            'кисель': 200,
            'квас': 250,
            'лимонад': 250,
            'кола': 250,
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
            'яйца': 100,
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
        }
        
        # Ищем по ключевым словам
        for key, portion in portions.items():
            if key in food_name:
                return portion
        
        return 100
    
    def _find_by_keywords(self, text):
        """Поиск продукта по ключевым словам"""
        keywords = {
            'арахис': 'арахис',
            'арахис соленый': 'арахис соленый',
            'орехи': 'арахис',
            'пиво': 'пиво светлое',
            'творог': 'творог 5%',
            'кефир': 'кефир 2.5%',
            'молоко': 'молоко 2.5%',
            'ряженка': 'ряженка',
            'сметана': 'сметана 20%',
            'сливки': 'сливки 20%',
            'масло сливочное': 'масло сливочное',
            'масло подсолнечное': 'масло подсолнечное',
            'масло оливковое': 'масло оливковое',
            'сыр': 'сыр российский',
            'колбаса': 'колбаса вареная',
            'колбаса копченая': 'колбаса копченая',
            'ветчина': 'ветчина',
            'сосиски': 'сосиски',
            'курица': 'куриная грудка',
            'индейка': 'индейка грудка',
            'говядина': 'говядина',
            'свинина': 'свинина',
            'баранина': 'баранина',
            'рыба': 'лосось',
            'лосось': 'лосось',
            'семга': 'семга',
            'форель': 'форель',
            'сельдь': 'сельдь',
            'скумбрия': 'скумбрия',
            'треска': 'треска',
            'минтай': 'минтай',
            'креветки': 'креветки',
            'кальмар': 'кальмар',
            'мидии': 'мидии',
            'яйцо': 'яйца',
            'яйца': 'яйца',
        }
        
        for key, value in keywords.items():
            if key in text:
                return self.db.find_food(value)
        
        return None