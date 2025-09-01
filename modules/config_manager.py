import os
import re
from typing import List, Dict
from dotenv import load_dotenv

from config import (
    TRACKED, BLACKLIST, EXPORT_GROUP, DELETE_CHUNK, DELETE_PAUSE, ON_START_PURGE,
    DELETE_SAVED_MESSAGES, DELETE_SAVED_DELAY_SECONDS
)

# --- ENV ---
load_dotenv()
API_ID_STR = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION')

# Проверка и преобразование API_ID в число
try:
    API_ID = int(API_ID_STR)
except (ValueError, TypeError):
    print("❌ Ошибка: API_ID в файле .env должен быть числом.")
    raise SystemExit(1)

if not all([API_ID, API_HASH, SESSION]):
    print("❌ Ошибка: Не все переменные (API_ID, API_HASH, SESSION) заданы в файле .env.")
    raise SystemExit(1)

# --- Константы/настройки поведения ---
ALERT_PREFIX = "🚨🚨🚨 "  # все оповещения сохраняем, остальное в 'Избранном' удаляем
MD = 'md'


def save_config_to_file(tracked_list: List[str], blacklist_list: List[str]):
    """Сохраняет обновленные списки в файл config.py."""
    try:
        # Читаем текущий config.py
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обновляем списки в контенте
        # Обновляем TRACKED
        tracked_pattern = r'TRACKED = \[.*?\]'
        tracked_replacement = f'TRACKED = {tracked_list}'
        content = re.sub(tracked_pattern, tracked_replacement, content, flags=re.DOTALL)
        
        # Обновляем BLACKLIST
        blacklist_pattern = r'BLACKLIST = \[.*?\]'
        blacklist_replacement = f'BLACKLIST = {blacklist_list}'
        content = re.sub(blacklist_pattern, blacklist_replacement, content, flags=re.DOTALL)
        
        # Сохраняем обновленный файл
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Настройки сохранены в config.py")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")


def get_config():
    """Возвращает текущую конфигурацию."""
    return {
        'API_ID': API_ID,
        'API_HASH': API_HASH,
        'SESSION': SESSION,
        'TRACKED': TRACKED,
        'BLACKLIST': BLACKLIST,
        'EXPORT_GROUP': EXPORT_GROUP,
        'DELETE_CHUNK': DELETE_CHUNK,
        'DELETE_PAUSE': DELETE_PAUSE,
        'ON_START_PURGE': ON_START_PURGE,
        'DELETE_SAVED_MESSAGES': DELETE_SAVED_MESSAGES,
        'DELETE_SAVED_DELAY_SECONDS': DELETE_SAVED_DELAY_SECONDS,
        'ALERT_PREFIX': ALERT_PREFIX,
        'MD': MD
    }
