#!/usr/bin/env python3
"""
Запуск бота для подсчета КБЖУ
"""
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие токена
if not os.getenv('BOT_TOKEN'):
    print("❌ Ошибка: Не найден BOT_TOKEN в файле .env")
    print("📝 Создайте файл .env и добавьте строку: BOT_TOKEN=ваш_токен")
    sys.exit(1)

# Запускаем бота
print("=" * 50)
print("🍎 Бот для подсчета КБЖУ")
print("=" * 50)

try:
    from bot import main
    main()
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📦 Установите зависимости: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()