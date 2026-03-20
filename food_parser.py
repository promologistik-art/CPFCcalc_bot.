import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """
        Универсальный парсер для любых продуктов
        Понимает форматы:
        - 100г творог
        - творог 100г
        - 3 литра пива
        - пиво 3 литра
        - 2 бутерброда с колбасой
        - кофе 2 ложки сахара
        - тарелка борща
        - 200 грамм арахиса
        - пачка чипсов
        - и т.д.
        """
        # Приводим к нижнему регистру
        text = text.lower().strip()
        
        # Разделяем по запятым или переносам строк
        parts = re.split(r'[,\n]', text)
        results = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Извлекаем все продукты из этой части
            items = self._extract_products(part)
            results.extend(items)
        
        return results
    
    def _extract_products(self, text):
        """
        Извлекает все продукты из текста
        Обрабатывает даже сложные случаи типа "пиво 3 литра и 100 гр арахиса"
        """
        # Сначала пробуем разделить по "и" если это разные продукты
        if ' и ' in text and not self._is_single_product(text):
            subparts = text.split(' и ')
            products = []
            for subpart in subparts:
                products.extend(self._extract_single_product(subpart))
            return products
        
        # Если это одно блюдо или продукт
        return self._extract_single_product(text)
    
    def _is_single_product(self, text):
        """Проверяет, является ли текст одним продуктом"""
        # Если есть слова-связки, значит это несколько продуктов
        connectors = [' и ', ' с ', ' со ', 'без']
        for conn in connectors:
            if conn in text:
                # Но это может быть "бутерброд с колбасой" - это одно блюдо
                if 'бутерброд' in text or 'сэндвич' in text:
                    return True
                return False
        return True
    
    def _extract_single_product(self, text):
        """
        Извлекает один продукт из текста
        Универсальный метод, работающий для всего
        """
        # Сначала ищем числовые значения с единицами измерения
        weight_info = self._find_weight(text)
        
        if weight_info:
            value, unit, remaining_text = weight_info
            # Конвертируем в граммы/миллилитры
            weight = self._convert_to_grams(value, unit, text)
            
            # Определяем, является ли это сложным блюдом
            if self._is_complex_dish(remaining_text):
                return self._parse_complex_dish_with_weight(remaining_text, weight)
            else:
                return [{'name': remaining_text.strip(), 'weight': weight}]
        
        # Если вес не найден, ищем известные форматы
        if 'бутерброд' in text:
            return self._parse_sandwich(text)
        elif 'борщ' in text or 'щи' in text or 'суп' in text:
            return self._parse_soup(text)
        elif 'салат' in text:
            return self._parse_salad(text)
        elif 'кофе' in text or 'чай' in text:
            return self._parse_hot_drink(text)
        elif 'пиво' in text:
            return self._parse_beer(text)
        elif 'шашлык' in text:
            return self._parse_shashlik(text)
        elif 'пельмени' in text or 'вареники' in text:
            return self._parse_dumplings(text)
        elif 'блины' in text:
            return self._parse_pancakes(text)
        elif 'котлет' in text:
            return self._parse_cutlets(text)
        elif 'яичниц' in text or 'яйц' in text:
            return self._parse_eggs(text)
        else:
            # Обычный продукт со стандартной порцией
            weight = self._guess_portion(text)
            return [{'name': text.strip(), 'weight': weight}]
    
    def _find_weight(self, text):
        """
        Ищет в тексте паттерны с весом
        Возвращает (значение, единица, оставшийся_текст)
        """
        patterns = [
            # Формат: "100г творог" или "100 г творог"
            (r'^(\d+)\s*г(?:рамм)?\s+(.+)$', 'г'),
            (r'^(\d+)\s*мл\s+(.+)$', 'мл'),
            (r'^(\d+(?:\.\d+)?)\s*л(?:итр)?\s+(.+)$', 'л'),
            
            # Формат: "творог 100г" или "творог 100 г"
            (r'^(.+?)\s+(\d+)\s*г(?:рамм)?$', 'г'),
            (r'^(.+?)\s+(\d+)\s*мл$', 'мл'),
            (r'^(.+?)\s+(\d+(?:\.\d+)?)\s*л(?:итр)?$', 'л'),
            
            # Формат: "100 грамм арахиса" (с родительным падежом)
            (r'^(\d+)\s*г(?:рамм)?\s+([а-я]+[а-я]?[а-я]?[а-я]?)$', 'г'),
            
            # Формат: "3 литра пива"
            (r'^(\d+)\s*л(?:итр)?\s+([а-я]+[а-я]?[а-я]?)$', 'л'),
            
            # Формат: "пачка чипсов 150г"
            (r'^(.+?)\s+(\d+)\s*г$', 'г'),
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # Определяем, где число, а где текст
                    if groups[0].replace('.', '').isdigit():
                        value = float(groups[0])
                        remaining = groups[1]
                    elif groups[1].replace('.', '').isdigit():
                        value = float(groups[1])
                        remaining = groups[0]
                    else:
                        continue
                    
                    return value, unit, remaining
        
        return None
    
    def _convert_to_grams(self, value, unit, original_text):
        """Конвертирует в граммы или миллилитры"""
        if unit == 'л':
            # Проверяем, жидкий ли продукт
            liquid_keywords = ['пиво', 'вода', 'сок', 'молоко', 'кефир', 'кофе', 'чай', 'квас', 'лимонад']
            if any(keyword in original_text for keyword in liquid_keywords):
                return value * 1000  # литры в мл
            else:
                # Для сыпучих продуктов литры могут быть примерно равны кг
                return value * 1000
        elif unit in ['г', 'мл']:
            return int(value)
        else:
            return int(value)
    
    def _is_complex_dish(self, text):
        """Проверяет, является ли текст сложным блюдом"""
        complex_dishes = [
            'борщ', 'щи', 'солянка', 'окрошка', 'уха', 'рассольник',
            'салат', 'винегрет', 'оливье', 'цезарь', 'греческий',
            'шашлык', 'кебаб', 'люля',
            'пельмени', 'вареники', 'манты', 'хинкали', 'чебурек',
            'блины', 'оладьи', 'сырники', 'котлеты', 'тефтели',
            'бутерброд', 'сэндвич', 'бургер', 'хот-дог', 'шаурма',
            'пицца', 'лазанья', 'ризотто', 'паэлья',
            'пюре', 'каша', 'рагу', 'жаркое',
        ]
        return any(dish in text for dish in complex_dishes)
    
    def _parse_complex_dish_with_weight(self, dish_name, weight):
        """Парсит сложное блюдо с указанным весом"""
        # Для большинства сложных блюд вес относится ко всему блюду
        if 'борщ' in dish_name:
            products = [{'name': 'борщ', 'weight': weight}]
            if 'со сметаной' in dish_name:
                products.append({'name': 'сметана 20%', 'weight': 20})
            return products
        elif 'щи' in dish_name:
            return [{'name': 'щи', 'weight': weight}]
        elif 'солянка' in dish_name:
            return [{'name': 'солянка', 'weight': weight}]
        elif 'окрошка' in dish_name:
            return [{'name': 'окрошка', 'weight': weight}]
        elif 'суп' in dish_name:
            return [{'name': 'суп', 'weight': weight}]
        elif 'салат' in dish_name:
            return [{'name': dish_name, 'weight': weight}]
        elif 'пельмени' in dish_name:
            return [{'name': 'пельмени', 'weight': weight}]
        elif 'вареники' in dish_name:
            return [{'name': 'вареники', 'weight': weight}]
        elif 'блины' in dish_name:
            return [{'name': 'блины', 'weight': weight}]
        elif 'котлеты' in dish_name:
            return [{'name': 'котлеты', 'weight': weight}]
        elif 'шашлык' in dish_name:
            if 'свинина' in dish_name:
                return [{'name': 'шашлык из свинины', 'weight': weight}]
            elif 'курица' in dish_name:
                return [{'name': 'шашлык из курицы', 'weight': weight}]
            else:
                return [{'name': 'шашлык из свинины', 'weight': weight}]
        else:
            return [{'name': dish_name, 'weight': weight}]
    
    def _parse_sandwich(self, text):
        """Парсинг бутерброда"""
        # Ищем количество
        count = 1
        match = re.search(r'(\d+)\s*бутерброд', text)
        if match:
            count = int(match.group(1))
        
        products = []
        
        # Хлеб (30г на бутерброд)
        if 'черный' in text or 'ржаной' in text:
            products.append({'name': 'хлеб ржаной', 'weight': 30 * count})
        else:
            products.append({'name': 'хлеб белый', 'weight': 30 * count})
        
        # Начинка
        if 'с колбасой' in text:
            if 'копченой' in text:
                products.append({'name': 'колбаса копченая', 'weight': 40 * count})
            else:
                products.append({'name': 'колбаса вареная', 'weight': 40 * count})
        elif 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 30 * count})
        elif 'с маслом' in text:
            products.append({'name': 'масло сливочное', 'weight': 10 * count})
        
        return products
    
    def _parse_soup(self, text):
        """Парсинг супа"""
        weight = 300  # стандартная тарелка
        
        # Ищем указанный вес
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        if 'борщ' in text:
            products = [{'name': 'борщ', 'weight': weight}]
            if 'со сметаной' in text:
                products.append({'name': 'сметана 20%', 'weight': 20})
            return products
        elif 'щи' in text:
            return [{'name': 'щи', 'weight': weight}]
        elif 'солянка' in text:
            return [{'name': 'солянка', 'weight': weight}]
        elif 'окрошка' in text:
            return [{'name': 'окрошка', 'weight': weight}]
        elif 'уха' in text:
            return [{'name': 'уха', 'weight': weight}]
        else:
            return [{'name': 'суп', 'weight': weight}]
    
    def _parse_salad(self, text):
        """Парсинг салата"""
        weight = 200  # стандартная порция
        
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        if 'оливье' in text:
            return [{'name': 'салат оливье', 'weight': weight}]
        elif 'цезарь' in text:
            return [{'name': 'салат цезарь', 'weight': weight}]
        elif 'греческий' in text:
            return [{'name': 'салат греческий', 'weight': weight}]
        elif 'винегрет' in text:
            return [{'name': 'винегрет', 'weight': weight}]
        else:
            return [{'name': 'салат', 'weight': weight}]
    
    def _parse_hot_drink(self, text):
        """Парсинг горячих напитков"""
        products = []
        
        # Определяем напиток
        if 'кофе' in text:
            drink = 'кофе'
        elif 'чай' in text:
            if 'зеленый' in text:
                drink = 'чай зеленый'
            else:
                drink = 'чай черный'
        else:
            drink = 'кофе'
        
        # Объем
        weight = 200  # стандартная чашка
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        products.append({'name': drink, 'weight': weight})
        
        # Сахар
        sugar_match = re.search(r'(\d+)\s*ложк[иа]?\s*сахар', text)
        if sugar_match:
            spoons = int(sugar_match.group(1))
            products.append({'name': 'сахар', 'weight': spoons * 7})
        elif 'сахар' in text and 'без сахара' not in text:
            products.append({'name': 'сахар', 'weight': 7})
        
        return products
    
    def _parse_beer(self, text):
        """Парсинг пива"""
        # Ищем объем
        weight = 500  # стандартная бутылка
        
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        # Определяем тип
        if 'светлое' in text:
            return [{'name': 'пиво светлое', 'weight': weight}]
        elif 'темное' in text:
            return [{'name': 'пиво темное', 'weight': weight}]
        elif 'живое' in text:
            return [{'name': 'пиво живое', 'weight': weight}]
        elif 'безалкогольное' in text:
            return [{'name': 'пиво безалкогольное', 'weight': weight}]
        else:
            return [{'name': 'пиво светлое', 'weight': weight}]
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        weight = 200  # стандартная порция
        
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        if 'свинина' in text:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
        elif 'курица' in text:
            return [{'name': 'шашлык из курицы', 'weight': weight}]
        elif 'говядина' in text:
            return [{'name': 'шашлык из говядины', 'weight': weight}]
        elif 'баранина' in text:
            return [{'name': 'шашлык из баранины', 'weight': weight}]
        else:
            return [{'name': 'шашлык из свинины', 'weight': weight}]
    
    def _parse_dumplings(self, text):
        """Парсинг пельменей/вареников"""
        weight = 200  # стандартная порция
        
        weight_info = self._find_weight(text)
        if weight_info:
            value, unit, _ = weight_info
            weight = self._convert_to_grams(value, unit, text)
        
        if 'пельмени' in text:
            return [{'name': 'пельмени', 'weight': weight}]
        elif 'вареники' in text:
            if 'с творогом' in text:
                return [{'name': 'вареники с творогом', 'weight': weight}]
            elif 'с картошкой' in text:
                return [{'name': 'вареники с картошкой', 'weight': weight}]
            elif 'с вишней' in text:
                return [{'name': 'вареники с вишней', 'weight': weight}]
            else:
                return [{'name': 'вареники', 'weight': weight}]
        else:
            return [{'name': 'пельмени', 'weight': weight}]
    
    def _parse_pancakes(self, text):
        """Парсинг блинов"""
        count = 3  # стандартная порция
        
        match = re.search(r'(\d+)\s*блин', text)
        if match:
            count = int(match.group(1))
        
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
        count = 2  # стандартная порция
        
        match = re.search(r'(\d+)\s*котлет', text)
        if match:
            count = int(match.group(1))
        
        weight = count * 75  # 1 котлета ~75г
        
        if 'куриные' in text:
            return [{'name': 'котлеты куриные', 'weight': weight}]
        elif 'рыбные' in text:
            return [{'name': 'котлеты рыбные', 'weight': weight}]
        else:
            return [{'name': 'котлеты', 'weight': weight}]
    
    def _parse_eggs(self, text):
        """Парсинг яиц"""
        count = 2  # стандартная порция
        
        match = re.search(r'(\d+)\s*яйц', text)
        if match:
            count = int(match.group(1))
        
        weight = count * 50  # 1 яйцо ~50г
        
        products = [{'name': 'яйца', 'weight': weight}]
        
        if 'яичница' in text or 'глазунья' in text:
            products.append({'name': 'масло подсолнечное', 'weight': 10})
        
        return products
    
    def _guess_portion(self, text):
        """Универсальный определитель стандартной порции"""
        portions = {
            # Напитки
            'кофе': 200, 'чай': 200, 'сок': 200, 'компот': 200,
            'квас': 250, 'лимонад': 250, 'кола': 250, 'пепси': 250,
            'пиво': 500, 'вино': 150, 'водка': 50, 'коньяк': 50,
            'виски': 50, 'ром': 50, 'джин': 50,
            
            # Молочка
            'молоко': 200, 'кефир': 200, 'ряженка': 200, 'йогурт': 150,
            'творог': 150, 'сметана': 20, 'сливки': 20,
            
            # Хлеб
            'хлеб': 30, 'батон': 30, 'булка': 50, 'лаваш': 50,
            'бутерброд': 80, 'тост': 25,
            
            # Фрукты
            'яблоко': 150, 'банан': 150, 'апельсин': 150, 'мандарин': 100,
            'груша': 150, 'персик': 150, 'абрикос': 100, 'слива': 100,
            'виноград': 150, 'клубника': 150, 'малина': 150, 'черника': 150,
            'арбуз': 300, 'дыня': 300, 'ананас': 200, 'манго': 200,
            'авокадо': 100, 'киви': 100, 'гранат': 200,
            
            # Овощи
            'картофель': 200, 'картошка': 200, 'морковь': 100, 'лук': 50,
            'огурец': 100, 'помидор': 100, 'перец': 100, 'капуста': 150,
            'брокколи': 150, 'цветная капуста': 150, 'кабачок': 200,
            'баклажан': 200, 'тыква': 200, 'свекла': 150, 'редис': 50,
            
            # Мясо
            'мясо': 150, 'говядина': 150, 'свинина': 150, 'баранина': 150,
            'курица': 150, 'куриная грудка': 150, 'индейка': 150, 'утка': 150,
            'печень': 100, 'сердце': 100, 'язык': 100,
            
            # Рыба
            'рыба': 150, 'лосось': 150, 'семга': 150, 'форель': 150,
            'скумбрия': 150, 'сельдь': 100, 'треска': 150, 'минтай': 150,
            'креветки': 100, 'кальмар': 100, 'мидии': 100, 'икра': 30,
            
            # Колбаса
            'колбаса': 50, 'сосиски': 50, 'сардельки': 50, 'ветчина': 50,
            'бекон': 30, 'сало': 30,
            
            # Сыр
            'сыр': 30, 'моцарелла': 30, 'пармезан': 20, 'фета': 40,
            
            # Крупы
            'гречка': 200, 'рис': 200, 'овсянка': 200, 'каша': 200,
            'пшено': 200, 'перловка': 200, 'кускус': 200, 'булгур': 200,
            'макароны': 200, 'паста': 200, 'спагетти': 200, 'лапша': 200,
            
            # Готовые блюда
            'суп': 300, 'борщ': 300, 'щи': 300, 'солянка': 300,
            'окрошка': 300, 'уха': 300, 'рассольник': 300,
            'салат': 200, 'оливье': 200, 'цезарь': 200, 'винегрет': 200,
            'пельмени': 200, 'вареники': 200, 'манты': 200, 'хинкали': 200,
            'блины': 150, 'оладьи': 150, 'сырники': 150,
            'котлеты': 150, 'тефтели': 150, 'фрикадельки': 150,
            'шашлык': 200, 'кебаб': 200, 'люля': 200,
            'пюре': 200, 'рагу': 200, 'жаркое': 250,
            'пицца': 200, 'бургер': 200, 'шаурма': 300, 'хот-дог': 150,
            'картошка фри': 150, 'наггетсы': 100, 'крылышки': 150,
            
            # Орехи и снеки
            'арахис': 30, 'орехи': 30, 'грецкие': 30, 'миндаль': 30,
            'фундук': 30, 'кешью': 30, 'фисташки': 30, 'кедровые': 20,
            'семечки': 30, 'тыквенные семечки': 30, 'чипсы': 50,
            
            # Сладости
            'шоколад': 20, 'конфеты': 15, 'печенье': 30, 'вафли': 30,
            'халва': 30, 'зефир': 30, 'мармелад': 30, 'пастила': 30,
            'торт': 150, 'пирожное': 100, 'кекс': 80, 'пирог': 150,
            'варенье': 20, 'джем': 20, 'мед': 20, 'сгущенка': 30,
            
            # Соусы
            'кетчуп': 20, 'майонез': 20, 'горчица': 10, 'соус': 30,
        }
        
        # Ищем по ключевым словам
        for key, portion in portions.items():
            if key in text:
                return portion
        
        # Если ничего не нашли, пробуем определить по контексту
        if any(word in text for word in ['стакан', 'чашка', 'кружка']):
            return 200
        elif any(word in text for word in ['тарелка', 'миска', 'порция']):
            return 300
        elif any(word in text for word in ['ложка', 'чайная']):
            return 10
        elif any(word in text for word in ['столовая', 'поварешка']):
            return 25
        elif any(word in text for word in ['кусок', 'ломтик']):
            return 50
        elif any(word in text for word in ['горсть', 'пригоршня']):
            return 30
        elif any(word in text for word in ['пачка', 'упаковка']):
            return 200
        
        return 100  # абсолютный дефолт