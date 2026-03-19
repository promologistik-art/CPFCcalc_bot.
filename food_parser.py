import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """Улучшенный парсинг сообщения с продуктами"""
        # Разделяем сообщение на отдельные продукты по запятым или переносам строк
        lines = re.split(r'[,\n]', text.lower())
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Проверяем, является ли строка сложным блюдом
            if self._is_complex_dish(line):
                results.extend(self._parse_complex_dish(line))
                continue
            
            # Проверяем на специальные случаи (сахар в ложках)
            if 'сахар' in line and 'ложек' in line:
                sugar_result = self._parse_sugar(line)
                if sugar_result:
                    results.append(sugar_result)
                    continue
            
            # Ищем вес в разных форматах
            weight = self._extract_weight(line)
            
            # Очищаем название от веса
            food_name = self._clean_name(line)
            
            # Проверяем, есть ли продукт в базе
            food = self.db.find_food(food_name)
            
            # Если продукт не найден, пробуем найти по ключевым словам
            if not food:
                food = self._find_by_keywords(food_name)
                if food:
                    food_name = food.name_ru
            
            # Если вес не указан, используем стандартную порцию
            if weight == 0:
                weight = self._guess_portion(food_name, food)
            
            if food_name:  # Добавляем только если есть название
                results.append({
                    'name': food_name,
                    'weight': weight
                })
        
        return results
    
    def _extract_weight(self, text):
        """Извлечение веса из текста"""
        # Форматы: 100г, 100 г, 100грамм, 100 грамм, 200мл, 2шт, 3ложки
        patterns = [
            r'(\d+)\s*г(?:рамм)?',  # 100г, 100 г, 100грамм, 100 грамм
            r'(\d+)\s*мл',           # 200мл, 200 мл
            r'(\d+)\s*шт',           # 2шт, 2 шт
            r'(\d+)\s*л(?:ожк[иа]?)' # 2 ложки, 3 ложки
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _clean_name(self, text):
        """Очистка названия от веса и других числовых значений"""
        # Удаляем вес и единицы измерения
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        text = re.sub(r'\d+\s*л(?:ожк[иа]?)?', '', text)
        text = re.sub(r'\d+%', '', text)  # убираем проценты
        
        # Удаляем предлоги и лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(с |со |из |на |в |для |и |или )', ' ', text)
        
        return text.strip()
    
    def _parse_sugar(self, text):
        """Парсинг сахара в ложках"""
        match = re.search(r'(\d+)\s*л(?:ожк[иа]?)?\s*сахар', text)
        if match:
            spoons = int(match.group(1))
            weight = spoons * 7  # 1 ложка сахара ≈ 7г
            return {'name': 'сахар', 'weight': weight}
        return None
    
    def _is_complex_dish(self, text):
        """Проверка, является ли блюдо сложным"""
        complex_dishes = [
            'бутерброд', 'сэндвич', 'салат', 'суп', 'борщ', 'щи', 
            'солянка', 'окрошка', 'рассольник', 'уха', 'шашлык',
            'пюре', 'каша', 'макароны', 'пельмени', 'вареники',
            'блины', 'оладьи', 'сырники', 'котлеты', 'тефтели'
        ]
        return any(dish in text for dish in complex_dishes)
    
    def _parse_complex_dish(self, text):
        """Парсинг сложных блюд"""
        products = []
        
        # Бутерброды
        if 'бутерброд' in text or 'сэндвич' in text:
            return self._parse_sandwich(text)
        
        # Супы
        elif 'борщ' in text:
            return self._parse_borscht(text)
        elif 'щи' in text:
            return self._parse_shchi(text)
        elif 'солянка' in text:
            return self._parse_solyanka(text)
        elif 'окрошка' in text:
            return self._parse_okroshka(text)
        elif 'уха' in text:
            return self._parse_uha(text)
        elif 'рассольник' in text:
            return self._parse_rassolnik(text)
        elif 'суп' in text:
            return self._parse_soup(text)
        
        # Салаты
        elif 'салат' in text:
            return self._parse_salad(text)
        
        # Горячие блюда
        elif 'шашлык' in text:
            return self._parse_shashlik(text)
        elif 'пюре' in text:
            return self._parse_mashed_potatoes(text)
        elif 'каша' in text:
            return self._parse_kasha(text)
        elif 'макароны' in text or 'паста' in text:
            return self._parse_pasta(text)
        elif 'пельмени' in text:
            return self._parse_pelmeni(text)
        elif 'вареники' in text:
            return self._parse_vareniki(text)
        elif 'блины' in text or 'блинчики' in text:
            return self._parse_blini(text)
        elif 'оладьи' in text:
            return self._parse_oladushki(text)
        elif 'сырники' in text:
            return self._parse_syrniki(text)
        elif 'котлеты' in text:
            return self._parse_cutlets(text)
        
        return products
    
    def _parse_sandwich(self, text):
        """Парсинг бутерброда"""
        products = []
        
        # Основа - хлеб
        if 'черный' in text or 'ржаной' in text:
            products.append({'name': 'хлеб ржаной', 'weight': 30})
        elif 'зерновой' in text or 'цельнозерновой' in text:
            products.append({'name': 'хлеб цельнозерновой', 'weight': 30})
        else:
            products.append({'name': 'хлеб белый', 'weight': 30})
        
        # Масло
        if 'с маслом' in text:
            products.append({'name': 'масло сливочное', 'weight': 10})
        
        # Колбаса
        if 'с колбасой' in text:
            if 'вареной' in text or 'докторской' in text:
                products.append({'name': 'колбаса вареная', 'weight': 40})
            elif 'копченой' in text or 'сервелат' in text:
                products.append({'name': 'колбаса копченая', 'weight': 35})
            else:
                products.append({'name': 'колбаса вареная', 'weight': 40})
        
        # Сыр
        if 'с сыром' in text:
            products.append({'name': 'сыр российский', 'weight': 25})
        
        return products
    
    def _parse_borscht(self, text):
        """Парсинг борща"""
        products = []
        
        # Основа борща
        products.append({'name': 'свекла', 'weight': 50})
        products.append({'name': 'капуста', 'weight': 50})
        products.append({'name': 'картофель', 'weight': 70})
        products.append({'name': 'морковь', 'weight': 30})
        products.append({'name': 'лук', 'weight': 20})
        
        # Мясо
        if 'с мясом' in text:
            products.append({'name': 'говядина', 'weight': 50})
        
        # Сметана
        if 'со сметаной' in text:
            products.append({'name': 'сметана 20%', 'weight': 20})
        
        return products
    
    def _parse_shchi(self, text):
        """Парсинг щей"""
        products = [
            {'name': 'капуста', 'weight': 100},
            {'name': 'картофель', 'weight': 50},
            {'name': 'морковь', 'weight': 20},
            {'name': 'лук', 'weight': 20}
        ]
        
        if 'с мясом' in text:
            products.append({'name': 'говядина', 'weight': 50})
        
        return products
    
    def _parse_solyanka(self, text):
        """Парсинг солянки"""
        products = [
            {'name': 'колбаса вареная', 'weight': 30},
            {'name': 'колбаса копченая', 'weight': 30},
            {'name': 'ветчина', 'weight': 30},
            {'name': 'огурцы соленые', 'weight': 40},
            {'name': 'лук', 'weight': 20},
            {'name': 'томатная паста', 'weight': 15}
        ]
        return products
    
    def _parse_okroshka(self, text):
        """Парсинг окрошки"""
        products = [
            {'name': 'картофель', 'weight': 60},
            {'name': 'яйца', 'weight': 50},
            {'name': 'колбаса вареная', 'weight': 50},
            {'name': 'огурец', 'weight': 50},
            {'name': 'редис', 'weight': 30},
            {'name': 'зелень', 'weight': 10}
        ]
        
        if 'на кефире' in text:
            products.append({'name': 'кефир 2.5%', 'weight': 200})
        elif 'на квасе' in text:
            products.append({'name': 'квас', 'weight': 200})
        
        return products
    
    def _parse_uha(self, text):
        """Парсинг ухи"""
        products = [
            {'name': 'рыба', 'weight': 100},
            {'name': 'картофель', 'weight': 50},
            {'name': 'морковь', 'weight': 20},
            {'name': 'лук', 'weight': 20}
        ]
        return products
    
    def _parse_rassolnik(self, text):
        """Парсинг рассольника"""
        products = [
            {'name': 'картофель', 'weight': 60},
            {'name': 'перловка', 'weight': 20},
            {'name': 'огурцы соленые', 'weight': 40},
            {'name': 'морковь', 'weight': 20},
            {'name': 'лук', 'weight': 20}
        ]
        return products
    
    def _parse_soup(self, text):
        """Парсинг обычного супа"""
        products = [
            {'name': 'картофель', 'weight': 70},
            {'name': 'морковь', 'weight': 20},
            {'name': 'лук', 'weight': 20}
        ]
        
        if 'куриный' in text:
            products.append({'name': 'куриная грудка', 'weight': 50})
        elif 'грибной' in text:
            products.append({'name': 'шампиньоны', 'weight': 50})
        elif 'гороховый' in text:
            products.append({'name': 'горох', 'weight': 30})
        elif 'рыбный' in text:
            products.append({'name': 'рыба', 'weight': 50})
        
        if 'с лапшой' in text:
            products.append({'name': 'лапша', 'weight': 20})
        elif 'с вермишелью' in text:
            products.append({'name': 'вермишель', 'weight': 20})
        elif 'с рисом' in text:
            products.append({'name': 'рис белый', 'weight': 20})
        elif 'с гречкой' in text:
            products.append({'name': 'гречка', 'weight': 20})
        
        return products
    
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
        elif 'винегрет' in text:
            return [
                {'name': 'свекла', 'weight': 50},
                {'name': 'картофель', 'weight': 50},
                {'name': 'морковь', 'weight': 30},
                {'name': 'огурцы соленые', 'weight': 30},
                {'name': 'горошек консервированный', 'weight': 20},
                {'name': 'лук', 'weight': 15},
                {'name': 'масло растительное', 'weight': 10}
            ]
        else:
            # Базовый овощной салат
            result = [
                {'name': 'помидор', 'weight': 50},
                {'name': 'огурец', 'weight': 50}
            ]
            if 'с маслом' in text:
                result.append({'name': 'масло растительное', 'weight': 10})
            elif 'со сметаной' in text:
                result.append({'name': 'сметана 15%', 'weight': 20})
            return result
    
    def _parse_shashlik(self, text):
        """Парсинг шашлыка"""
        if 'свинина' in text or 'свиной' in text:
            return [{'name': 'шашлык из свинины', 'weight': 200}]
        elif 'говядина' in text or 'говяжий' in text:
            return [{'name': 'шашлык из говядины', 'weight': 200}]
        elif 'курица' in text or 'куриный' in text:
            return [{'name': 'шашлык из курицы', 'weight': 200}]
        elif 'баранина' in text or 'бараний' in text:
            return [{'name': 'шашлык из баранины', 'weight': 200}]
        else:
            return [{'name': 'шашлык из свинины', 'weight': 200}]
    
    def _parse_mashed_potatoes(self, text):
        """Парсинг картофельного пюре"""
        result = [{'name': 'пюре картофельное', 'weight': 200}]
        if 'с маслом' in text:
            result.append({'name': 'масло сливочное', 'weight': 10})
        return result
    
    def _parse_kasha(self, text):
        """Парсинг каши"""
        if 'гречневая' in text or 'гречка' in text:
            result = [{'name': 'гречка вареная', 'weight': 200}]
        elif 'овсяная' in text or 'овсянка' in text or 'геркулес' in text:
            result = [{'name': 'овсянка вареная', 'weight': 200}]
        elif 'рисовая' in text or 'рис' in text:
            result = [{'name': 'рис белый вареный', 'weight': 200}]
        elif 'манная' in text or 'манка' in text:
            result = [{'name': 'манная каша', 'weight': 200}]
        elif 'пшенная' in text or 'пшено' in text:
            result = [{'name': 'пшенная каша', 'weight': 200}]
        elif 'перловая' in text or 'перловка' in text:
            result = [{'name': 'перловая каша', 'weight': 200}]
        else:
            result = [{'name': 'овсянка вареная', 'weight': 200}]
        
        if 'с маслом' in text:
            result.append({'name': 'масло сливочное', 'weight': 10})
        elif 'с молоком' in text:
            result.append({'name': 'молоко 2.5%', 'weight': 100})
        
        return result
    
    def _parse_pasta(self, text):
        """Парсинг макаронных изделий"""
        result = [{'name': 'макароны вареные', 'weight': 200}]
        
        if 'по-флотски' in text:
            result.append({'name': 'фарш мясной', 'weight': 80})
        elif 'с сыром' in text:
            result.append({'name': 'сыр российский', 'weight': 30})
        elif 'с маслом' in text:
            result.append({'name': 'масло сливочное', 'weight': 10})
        
        return result
    
    def _parse_pelmeni(self, text):
        """Парсинг пельменей"""
        if 'говяжьи' in text:
            return [{'name': 'пельмени говяжьи', 'weight': 200}]
        elif 'свиные' in text:
            return [{'name': 'пельмени свиные', 'weight': 200}]
        else:
            return [{'name': 'пельмени', 'weight': 200}]
    
    def _parse_vareniki(self, text):
        """Парсинг вареников"""
        if 'с творогом' in text:
            return [{'name': 'вареники с творогом', 'weight': 200}]
        elif 'с картошкой' in text or 'с картофелем' in text:
            return [{'name': 'вареники с картошкой', 'weight': 200}]
        elif 'с вишней' in text:
            return [{'name': 'вареники с вишней', 'weight': 200}]
        else:
            return [{'name': 'вареники с творогом', 'weight': 200}]
    
    def _parse_blini(self, text):
        """Парсинг блинов"""
        if 'с мясом' in text:
            return [{'name': 'блины с мясом', 'weight': 200}]
        elif 'с творогом' in text:
            return [{'name': 'блины с творогом', 'weight': 200}]
        elif 'с икрой' in text:
            return [{'name': 'блины с икрой', 'weight': 150}]
        else:
            return [{'name': 'блины', 'weight': 150}]
    
    def _parse_oladushki(self, text):
        """Парсинг оладий"""
        return [{'name': 'оладьи', 'weight': 150}]
    
    def _parse_syrniki(self, text):
        """Парсинг сырников"""
        return [{'name': 'сырники', 'weight': 150}]
    
    def _parse_cutlets(self, text):
        """Парсинг котлет"""
        if 'куриные' in text:
            return [{'name': 'котлеты куриные', 'weight': 150}]
        elif 'рыбные' in text:
            return [{'name': 'котлеты рыбные', 'weight': 150}]
        else:
            return [{'name': 'котлеты', 'weight': 150}]
    
    def _find_by_keywords(self, text):
        """Поиск продукта по ключевым словам"""
        keywords = {
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
            'картошка': 'картофель',
            'картофель': 'картофель',
            'пюре': 'пюре картофельное',
            'капуста': 'капуста',
            'морковь': 'морковь',
            'лук': 'лук',
            'чеснок': 'чеснок',
            'огурец': 'огурец',
            'помидор': 'помидор',
            'перец': 'перец болгарский',
            'кабачок': 'кабачок',
            'баклажан': 'баклажан',
            'тыква': 'тыква',
            'свекла': 'свекла',
            'зелень': 'зелень',
            'укроп': 'укроп',
            'петрушка': 'петрушка',
            'салат': 'салат',
            'руккола': 'руккола',
            'авокадо': 'авокадо',
            'гречка': 'гречка',
            'рис': 'рис белый',
            'овсянка': 'овсянка',
            'пшено': 'пшено',
            'перловка': 'перловка',
            'манка': 'манка',
            'макароны': 'макароны',
            'паста': 'паста',
            'спагетти': 'спагетти',
            'хлеб': 'хлеб белый',
            'батон': 'батон',
            'лаваш': 'лаваш',
            'банан': 'банан',
            'яблоко': 'яблоко',
            'апельсин': 'апельсин',
            'мандарин': 'мандарин',
            'груша': 'груша',
            'виноград': 'виноград',
            'клубника': 'клубника',
            'малина': 'малина',
            'кофе': 'кофе',
            'чай': 'чай черный',
            'сахар': 'сахар',
            'мед': 'мед',
            'шоколад': 'шоколад темный',
            'печенье': 'печенье',
            'конфеты': 'конфеты шоколадные',
            'вафли': 'вафли',
            'халва': 'халва',
            'зефир': 'зефир',
            'мармелад': 'мармелад',
            'сок': 'сок апельсиновый',
            'компот': 'компот',
            'кисель': 'кисель',
            'квас': 'квас',
            'лимонад': 'лимонад',
            'кола': 'кола',
            'минералка': 'минеральная вода',
            'пиво': 'пиво светлое',
            'вино': 'вино сухое',
            'водка': 'водка',
            'коньяк': 'коньяк',
            'виски': 'виски',
            'пельмени': 'пельмени',
            'вареники': 'вареники с творогом',
            'блины': 'блины',
            'оладьи': 'оладьи',
            'сырники': 'сырники',
            'котлеты': 'котлеты',
            'шашлык': 'шашлык из свинины',
            'бургер': 'бургер',
            'пицца': 'пицца',
            'шаурма': 'шаурма',
            'хот-дог': 'хот-дог',
            'картошка фри': 'картошка фри',
            'наггетсы': 'наггетсы',
            'суши': 'суши',
            'роллы': 'роллы',
        }
        
        for key, value in keywords.items():
            if key in text:
                return self.db.find_food(value)
        
        return None
    
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
            'минеральная вода': 250,
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
            'бутерброд': 80,
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
            'рассольник': 300,
            'уха': 300,
            'салат': 200,
            'оливье': 200,
            'цезарь': 200,
            'винегрет': 200,
            'греческий': 200,
            'сыр': 30,
            'колбаса': 50,
            'сосиски': 50,
            'ветчина': 50,
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
            'пиво': 500,
            'вино': 150,
            'водка': 50,
            'коньяк': 50,
            'виски': 50,
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