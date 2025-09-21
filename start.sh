#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Без цвета

# Проверка виртуального окружения
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Виртуальное окружение не найдено
    
Сначала выполните установку:
./install.sh${NC}"
    exit 1
fi

# Активация виртуального окружения
if ! source .venv/bin/activate 2>/dev/null; then
    echo -e "${RED}❌ Не удалось активировать виртуальное окружение
    
Попробуйте переустановить:
./install.sh${NC}"
    exit 1
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден
    
Создайте его с помощью:
./install.sh${NC}"
    exit 1
fi

# Проверка API ключей в .env
if ! grep -q "^API_ID=[0-9]" .env || ! grep -q "^API_HASH=[a-zA-Z0-9]" .env; then
    echo -e "${YELLOW}⚠️ API ключи в .env файле не настроены

Как получить API ключи:
1. Перейдите на https://my.telegram.org/auth
2. Войдите в свой аккаунт
3. Нажмите 'API development tools'
4. Заполните форму
5. Скопируйте API_ID и API_HASH в файл .env${NC}"
    exit 1
fi

# Запуск скрипта
echo -e "${GREEN}🚀 Запуск TG-Guard...${NC}"
if ! python main.py; then
    echo -e "${RED}❌ Произошла ошибка при запуске
    
Проверьте:
• Правильность API ключей в .env
• Подключение к интернету
• Логи выше для деталей ошибки${NC}"
    exit 1
fi