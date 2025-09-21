#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Без цвета
BOLD='\033[1m'

# Вывод цветного сообщения
print_message() {
    COLOR=$1
    MSG=$2
    echo -e "${COLOR}${MSG}${NC}"
}

# Проверка наличия команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Заголовок
print_message "${GREEN}" "
🤖 TG-Guard - Установка
================================="

# Проверка версии Python
print_message "${YELLOW}" "\n📋 Проверка версии Python..."
if ! command_exists python3; then
    print_message "${RED}" "❌ Python 3 не установлен
    
Для установки Python 3:
• Ubuntu/Debian: sudo apt install python3
• Fedora: sudo dnf install python3
• Arch Linux: sudo pacman -S python3
• macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}")' 2>/dev/null)
if [ $? -ne 0 ]; then
    print_message "${RED}" "❌ Не удалось определить версию Python"
    exit 1
fi

PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    print_message "${RED}" "❌ Ваша версия Python устарела
    
• Установлена версия: $PYTHON_VERSION
• Требуется версия: 3.7 или выше
    
Пожалуйста, обновите Python"
    exit 1
fi
print_message "${GREEN}" "✅ Найден Python версии $PYTHON_VERSION"

# Проверка виртуального окружения
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    print_message "${YELLOW}" "\n🔄 Виртуальное окружение уже существует. Пересоздать? [д/Н]"
    read -r response
    if [[ "$response" =~ ^([дД]|[дД][аА]|[yY])+$ ]]; then
        print_message "${YELLOW}" "🗑️ Удаление существующего виртуального окружения..."
        rm -rf "$VENV_DIR"
    else
        print_message "${GREEN}" "✅ Используем существующее виртуальное окружение"
    fi
fi

# Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    print_message "${YELLOW}" "\n📦 Создание виртуального окружения..."
    if ! python3 -m venv "$VENV_DIR" > /dev/null 2>&1; then
        print_message "${RED}" "❌ Не удалось создать виртуальное окружение. Возможные причины:
• Нет прав на создание директории
• Не установлен пакет python3-venv
• Недостаточно места на диске"
        exit 1
    fi
    print_message "${GREEN}" "✅ Виртуальное окружение создано"
fi

# Активация виртуального окружения
print_message "${YELLOW}" "\n🔄 Активация виртуального окружения..."
if ! source "$VENV_DIR/bin/activate" 2>/dev/null; then
    print_message "${RED}" "❌ Не удалось активировать виртуальное окружение"
    exit 1
fi

# Обновление pip
print_message "${YELLOW}" "\n🔄 Обновление pip..."
if ! pip install --upgrade pip > /dev/null 2>&1; then
    print_message "${RED}" "❌ Не удалось обновить pip. Проверьте подключение к интернету"
    exit 1
fi

# Установка зависимостей
print_message "${YELLOW}" "\n📦 Установка зависимостей..."
if ! pip install -r requirements.txt > /dev/null 2>&1; then
    print_message "${RED}" "❌ Не удалось установить зависимости. Возможные причины:
• Отсутствует подключение к интернету
• Ошибка в файле requirements.txt
• Недостаточно прав для установки пакетов"
    exit 1
fi

# Проверка наличия .env
if [ ! -f ".env" ]; then
    print_message "${YELLOW}" "\n📝 Создание файла .env..."
    print_message "${BOLD}" "\nКак получить API ключи Telegram:
1. Перейдите на https://my.telegram.org/auth
2. Войдите в свой аккаунт
3. Нажмите 'API development tools'
4. Заполните форму (можно указать 'TG-Guard')
5. Скопируйте API_ID (числа) и API_HASH (буквы и числа)\n"
    
    # Создание .env файла
    cat > .env << 'ENV_EOF'
API_ID=  # Получите на https://my.telegram.org/auth (только цифры)
API_HASH=  # Получите на https://my.telegram.org/auth (вставьте без кавычек)
SESSION=my_user_session  # Можно оставить как есть
ENV_EOF
    
    print_message "${GREEN}" "✅ Файл .env создан"
else
    print_message "${GREEN}" "✅ Файл .env уже существует"
fi

# Сообщение об успешной установке
print_message "${GREEN}" "\n✅ Установка успешно завершена!"
print_message "${YELLOW}" "\nДля запуска TG-Guard:
1. Заполните API ключи в файле .env
2. При необходимости настройте списки в config.py
3. Запустите бота командой:
   ./start.sh

❗ Примечание: Убедитесь, что вы заполнили API ключи в файле .env перед запуском!"
