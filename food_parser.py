import re
from database import Database

class FoodParser:
    def __init__(self):
        self.db = Database()
        
    def parse_message(self, text):
        """
        Универсальный парсер для ЛЮБЫХ запросов
        """
        text = text.lower().strip()
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)
        
        # Разделяем на отдельные продукты
        products = self._split_products(text)
        
        results = []
        for product_text in products:
            item = self._parse_one_product(product_text)
            if item:
                results.append(item)
        
        return results
    
    def _split_products(self, text):
        """
        Разделяет текст на отдельные продукты
        Понимает:
        - запятые
        - союз "и"
        - числа с весами
        """
        # Сначала разделяем по запятым
        if ',' in text:
            parts = [p.strip() for p in text.split(',') if p.strip()]
            return self._split_parts_by_and(parts)
        
        # Если нет запятых, пробуем разделить по "и"
        if ' и ' in text:
            parts = [p.strip() for p in text.split(' и ') if p.strip()]
            return self._split_parts_by_and(parts)
        
        # Если нет разделителей, ищем по числам с весами
        weight_matches = list(re.finditer(r'\d+\s*[гмл][лр]?', text))
        if len(weight_matches) > 1:
            return self._split_by_weights(text, weight_matches)
        
        return [text]
    
    def _split_parts_by_and(self, parts):
        """Рекурсивно разделяет части по союзу "и" внутри"""
        result = []
        for part in parts:
            if ' и ' in part and not self._is_complex_name(part):
                subparts = part.split(' и ')
                result.extend([p.strip() for p in subparts if p.strip()])
            else:
                result.append(part)
        return result
    
    def _split_by_weights(self, text, matches):
        """Разделяет текст по позициям чисел с весами"""
        parts = []
        last_pos = 0
        for match in matches:
            if match.start() > last_pos:
                # Берем текст от предыдущего числа до этого
                part = text[last_pos:match.start()].strip()
                if part:
                    parts.append(part + ' ' + match.group())
                else:
                    parts.append(match.group())
                last_pos = match.end()
            else:
                # Добавляем число к предыдущей части
                if parts:
                    parts[-1] = parts[-1] + ' ' + match.group()
                else:
                    parts.append(match.group())
                last_pos = match.end()
        
        # Последняя часть после последнего числа
        if last_pos < len(text):
            remaining = text[last_pos:].strip()
            if remaining:
                if parts:
                    parts[-1] = parts[-1] + ' ' + remaining
                else:
                    parts.append(remaining)
        
        return parts
    
    def _is_complex_name(self, text):
        """Проверяет, является ли текст сложным названием"""
        complex_patterns = [
            r'бутерброд с',
            r'кофе с',
            r'чай с',
            r'салат с',
            r'суп с',
            r'соус с',
        ]
        for pattern in complex_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _parse_one_product(self, text):
        """
        Парсит ОДИН продукт из текста
        Возвращает {'name': название, 'weight': вес}
        """
        if not text:
            return None
        
        # Извлекаем вес
        weight_info = self._extract_weight_info(text)
        
        if weight_info:
            weight, clean_text = weight_info
        else:
            weight = 0
            clean_text = text
        
        # Очищаем название
        name = self._clean_name(clean_text)
        
        # Если вес не найден, берем стандартную порцию
        if weight == 0:
            weight = self._get_default_weight(name)
        
        return {'name': name, 'weight': weight}
    
    def _extract_weight_info(self, text):
        """
        Извлекает вес из текста
        Возвращает (вес, текст_без_веса) или None
        Понимает:
        - 100г, 100 г, 100грамм
        - 200мл, 200 мл
        - 3л, 3 литра
        - 100 гр, 100гр
        - полкило, 0.5кг
        """
        # Паттерны для разных единиц
        patterns = [
            # Граммы
            (r'(\d+)\s*г(?:рамм)?', 1, 'г'),
            (r'(\d+)\s*гр', 1, 'г'),
            # Миллилитры
            (r'(\d+)\s*мл', 1, 'мл'),
            # Литры
            (r'(\d+(?:\.\d+)?)\s*л(?:итр(?:а|ов)?)?', 1000, 'л'),
            # Полкило
            (r'полкило', 500, 'г'),
            (r'0\.5\s*кг', 500, 'г'),
        ]
        
        for pattern, multiplier, unit in patterns:
            match = re.search(pattern, text)
            if match:
                if pattern == 'полкило':
                    value = 500
                else:
                    value = float(match.group(1))
                
                weight = int(value * multiplier)
                
                # Удаляем вес из текста
                clean_text = re.sub(pattern, '', text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                return weight, clean_text
        
        return None
    
    def _clean_name(self, text):
        """
        Очищает название от лишних слов и нормализует
        """
        # Удаляем предлоги и служебные слова
        stop_words = ['с', 'со', 'из', 'на', 'в', 'для', 'и', 'или', 'без', 'по']
        words = text.split()
        cleaned = [w for w in words if w not in stop_words]
        
        # Нормализуем падежи (простейший вариант)
        name = ' '.join(cleaned)
        name = self._normalize_case(name)
        
        return name
    
    def _normalize_case(self, name):
        """
        Приводит название к именительному падежу (упрощенно)
        """
        # Окончания родительного падежа
        endings = {
            'ого': 'ый',
            'его': 'ий',
            'ого': 'ой',
            'его': 'ей',
            'и': 'а',
            'у': 'а',
            'ой': 'а',
            'ей': 'я',
        }
        
        words = name.split()
        normalized = []
        for word in words:
            changed = False
            for ending, replacement in endings.items():
                if word.endswith(ending):
                    word = word[:-len(ending)] + replacement
                    changed = True
                    break
            normalized.append(word)
        
        return ' '.join(normalized)
    
    def _get_default_weight(self, name):
        """
        Возвращает стандартный вес для продукта
        """
        # Проверяем по ключевым словам
        keywords = {
            'хлеб': 30,
            'бутерброд': 80,
            'сыр': 30,
            'колбаса': 50,
            'сало': 30,
            'яйцо': 50,
            'яйца': 100,
            'молоко': 200,
            'кефир': 200,
            'йогурт': 150,
            'творог': 150,
            'сметана': 20,
            'масло': 10,
            'кофе': 200,
            'чай': 200,
            'сок': 200,
            'пиво': 500,
            'вино': 150,
            'водка': 50,
            'виски': 50,
            'коньяк': 50,
            'суп': 300,
            'борщ': 300,
            'салат': 200,
            'оливье': 200,
            'винегрет': 200,
            'шашлык': 200,
            'пельмени': 200,
            'котлеты': 150,
            'блины': 150,
            'пирожное': 100,
            'торт': 150,
            'шоколад': 20,
            'конфета': 15,
            'печенье': 30,
            'арахис': 30,
            'орехи': 30,
            'яблоко': 150,
            'банан': 150,
            'апельсин': 150,
            'авокадо': 100,
            'картофель': 200,
            'гречка': 200,
            'рис': 200,
            'макароны': 200,
        }
        
        name_lower = name.lower()
        for key, weight in keywords.items():
            if key in name_lower:
                return weight
        
        return 100