import re
from database import Database


class FoodParser:
    def __init__(self):
        self.db = Database()

    def parse_message(self, text):
        """Разбор сообщения на отдельные продукты"""
        text = text.lower().strip()
        text = text.replace('\n', ',')
        text = text.replace('•', ',')
        text = re.sub(r'\s+', ' ', text)

        parts = [p.strip() for p in text.split(',') if p.strip()]

        if len(parts) == 1 and ' и ' in parts[0]:
            parts = [p.strip() for p in parts[0].split(' и ') if p.strip()]

        results = []
        for part in parts:
            products = self._parse_part(part)
            results.extend(products)

        return results

    def normalize_product_name(self, name):
        """
        Нормализует название продукта
        "каша овсяная" -> "овсяная каша"
        "овсянка" -> "овсяная каша"
        """
        name_lower = name.lower().strip()

        # Словарь соответствий
        synonyms = {
            # Каши
            'овсянка': 'овсяная каша',
            'овсяная': 'овсяная каша',
            'овсяная каша': 'овсяная каша',
            'геркулес': 'овсяная каша',

            'манка': 'манная каша',
            'манная': 'манная каша',
            'манная каша': 'манная каша',

            'гречка': 'гречневая каша',
            'греча': 'гречневая каша',
            'гречневая': 'гречневая каша',
            'гречневая каша': 'гречневая каша',

            'рис': 'рисовая каша',
            'рисовая': 'рисовая каша',
            'рисовая каша': 'рисовая каша',

            'пшенка': 'пшенная каша',
            'пшено': 'пшенная каша',
            'пшенная': 'пшенная каша',
            'пшенная каша': 'пшенная каша',

            'перловка': 'перловая каша',
            'перловая': 'перловая каша',
            'перловая каша': 'перловая каша',

            # Другие
            'картошка': 'картофель',
            'помидор': 'томат',
            'курица': 'куриное филе',
            'мясо': 'мясо',
            'хлеб': 'хлеб',
            'молоко': 'молоко',
            'кефир': 'кефир',
            'творог': 'творог',
            'кофе': 'кофе',
            'чай': 'чай',
            'сахар': 'сахар',
            'масло': 'масло сливочное',
        }

        # Точное совпадение
        if name_lower in synonyms:
            return synonyms[name_lower]

        # Поиск по ключу внутри строки
        for key, value in synonyms.items():
            if key in name_lower:
                return value

        # Если есть "каша" и слово типа "овсян" - собираем
        if 'каша' in name_lower:
            for prefix in ['овсян', 'гречн', 'манн', 'рис', 'пшен', 'перлов']:
                if prefix in name_lower:
                    return f"{prefix}ая каша"

        return name

    def _parse_part(self, text):
        """Парсит одну часть текста"""
        if not text:
            return []

        print(f"\n📝 Парсим: '{text}'")

        weight = self._extract_weight(text)
        print(f"   Вес: {weight}г")

        name = self._clean_name(text)
        print(f"   После очистки: '{name}'")

        # Нормализация ДО поиска
        name = self.normalize_product_name(name)
        print(f"   После нормализации: '{name}'")

        if weight == 0:
            weight = self._get_default_weight(name)
            print(f"   Стандартный вес: {weight}г")

        if not name:
            name = text

        print(f"   🔍 Ищем: '{name}'")
        food = self.db.find_food(name)

        if food:
            print(f"   ✅ Найдено: {food.name_ru}")
            return [{'name': food.name_ru, 'weight': weight}]
        else:
            print(f"   ❌ Не найдено")
            return []

    def _extract_weight(self, text):
        """Извлекает вес из текста"""
        patterns = [
            (r'(\d+)\s*г(?:рамм)?', 1),
            (r'(\d+)\s*гр', 1),
            (r'(\d+)\s*мл', 1),
            (r'(\d+)\s*л(?:итр(?:а|ов)?)?', 1000),
            (r'(\d+)\s*шт', 1),
            (r'(\d+)\s*ложк[иа]?', 1),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                weight = value * multiplier

                if 'ложк' in pattern:
                    if 'сахар' in text:
                        weight = value * 7
                    elif 'кофе' in text:
                        weight = value * 2
                    else:
                        weight = value * 15

                return weight
        return 0

    def _clean_name(self, text):
        """Очищает название от веса и служебных слов"""
        text = re.sub(r'\d+\s*г(?:рамм)?', '', text)
        text = re.sub(r'\d+\s*гр', '', text)
        text = re.sub(r'\d+\s*мл', '', text)
        text = re.sub(r'\d+\s*л(?:итр(?:а|ов)?)?', '', text)
        text = re.sub(r'\d+\s*шт', '', text)
        text = re.sub(r'\d+\s*ложк[иа]?', '', text)

        stop_words = ['с', 'со', 'из', 'на', 'в', 'для', 'и', 'или', 'без', 'по']
        words = text.split()
        cleaned = [w for w in words if w not in stop_words]

        return ' '.join(cleaned).strip()

    def _get_default_weight(self, name):
        """Возвращает стандартный вес"""
        name_lower = name.lower()

        portions = {
            'кофе': 200, 'чай': 200, 'сок': 200,
            'молоко': 200, 'кефир': 200, 'йогурт': 150,
            'творог': 150, 'сметана': 20,
            'хлеб': 30, 'бутерброд': 80,
            'яблоко': 150, 'банан': 150,
            'картофель': 200,
            'гречневая каша': 200, 'овсяная каша': 200,
            'манная каша': 200, 'рисовая каша': 200,
            'суп': 300, 'борщ': 300,
            'салат': 200, 'пельмени': 200, 'шашлык': 200,
        }

        for key, portion in portions.items():
            if key in name_lower:
                return portion
        return 100