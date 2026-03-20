import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Получаем ID админов из .env
admin_ids_str = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]

# Для отладки (опционально)
print(f"🔐 Загружено админов: {len(ADMIN_IDS)}")