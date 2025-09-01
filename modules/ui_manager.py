from typing import List, Tuple
from .config_manager import save_config_to_file


def show_list_management_menu() -> Tuple[List[str], List[str]]:
    """Показывает меню управления списками и возвращает обновленные списки."""
    print("\n" + "="*60)
    print("⚙️ Настройка списков TRACKED и BLACKLIST")
    print("="*60)
    
    # Копируем списки из конфигурации
    from config import TRACKED, BLACKLIST
    current_tracked = list(TRACKED)
    current_blacklist = list(BLACKLIST)
    
    while True:
        print(f"\n📋 Текущие списки:")
        print(f"👀 TRACKED ({len(current_tracked)}): {current_tracked}")
        print(f"🚫 BLACKLIST ({len(current_blacklist)}): {current_blacklist}")
        print("\n" + "-"*40)
        print("1. ✏️ Редактировать список TRACKED")
        print("2. ✏️ Редактировать список BLACKLIST")
        print("3. 🔄 Сбросить к настройкам из config.py")
        print("4. ✅ Продолжить с текущими настройками")
        print("5. 💾 Сохранить настройки в config.py")
        print("-"*40)
        
        try:
            choice = input("Выберите действие (1-5): ").strip()
            
            if choice == "1":
                current_tracked = edit_tracked_list(current_tracked)
            elif choice == "2":
                current_blacklist = edit_blacklist_list(current_blacklist)
            elif choice == "3":
                from config import TRACKED, BLACKLIST
                current_tracked = list(TRACKED)
                current_blacklist = list(BLACKLIST)
                print("✅ Списки сброшены к настройкам из config.py")
            elif choice == "4":
                return current_tracked, current_blacklist
            elif choice == "5":
                save_config_to_file(current_tracked, current_blacklist)
                return current_tracked, current_blacklist
            else:
                print("❌ Пожалуйста, введите число от 1 до 5")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена пользователем")
            raise SystemExit(0)
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def edit_tracked_list(current_list: List[str]) -> List[str]:
    """Редактирует список TRACKED."""
    print(f"\n✏️ Редактирование списка TRACKED")
    print("="*40)
    
    while True:
        print(f"\n📋 Текущий список TRACKED ({len(current_list)}):")
        for i, user in enumerate(current_list, 1):
            print(f"  {i}. {user}")
        
        print("\nДействия:")
        print("1. ➕ Добавить пользователя")
        print("2. ➖ Удалить пользователя")
        print("3. 🔄 Очистить список")
        print("4. ✅ Вернуться назад")
        
        try:
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                username = input("Введите юзернейм (с @ или без): ").strip()
                if username:
                    if not username.startswith("@"):
                        username = "@" + username
                    if username not in current_list:
                        current_list.append(username)
                        print(f"✅ Добавлен: {username}")
                    else:
                        print(f"⚠️ {username} уже в списке")
                else:
                    print("❌ Юзернейм не может быть пустым")
                    
            elif choice == "2":
                if not current_list:
                    print("⚠️ Список пуст")
                    continue
                    
                try:
                    index = int(input(f"Введите номер пользователя (1-{len(current_list)}): ")) - 1
                    if 0 <= index < len(current_list):
                        removed = current_list.pop(index)
                        print(f"✅ Удален: {removed}")
                    else:
                        print("❌ Неверный номер")
                except ValueError:
                    print("❌ Введите число")
                    
            elif choice == "3":
                if current_list:
                    current_list.clear()
                    print("✅ Список очищен")
                else:
                    print("⚠️ Список уже пуст")
                    
            elif choice == "4":
                return current_list
            else:
                print("❌ Пожалуйста, введите число от 1 до 4")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена пользователем")
            raise SystemExit(0)
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def edit_blacklist_list(current_list: List[str]) -> List[str]:
    """Редактирует список BLACKLIST."""
    print(f"\n✏️ Редактирование списка BLACKLIST")
    print("="*40)
    
    while True:
        print(f"\n📋 Текущий список BLACKLIST ({len(current_list)}):")
        for i, user in enumerate(current_list, 1):
            print(f"  {i}. {user}")
        
        print("\nДействия:")
        print("1. ➕ Добавить пользователя")
        print("2. ➖ Удалить пользователя")
        print("3. 🔄 Очистить список")
        print("4. ✅ Вернуться назад")
        
        try:
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                username = input("Введите юзернейм (с @ или без): ").strip()
                if username:
                    if not username.startswith("@"):
                        username = "@" + username
                    if username not in current_list:
                        current_list.append(username)
                        print(f"✅ Добавлен: {username}")
                    else:
                        print(f"⚠️ {username} уже в списке")
                else:
                    print("❌ Юзернейм не может быть пустым")
                    
            elif choice == "2":
                if not current_list:
                    print("⚠️ Список пуст")
                    continue
                    
                try:
                    index = int(input(f"Введите номер пользователя (1-{len(current_list)}): ")) - 1
                    if 0 <= index < len(current_list):
                        removed = current_list.pop(index)
                        print(f"✅ Удален: {removed}")
                    else:
                        print("❌ Неверный номер")
                except ValueError:
                    print("❌ Введите число")
                    
            elif choice == "3":
                if current_list:
                    current_list.clear()
                    print("✅ Список очищен")
                else:
                    print("⚠️ Список уже пуст")
                    
            elif choice == "4":
                return current_list
            else:
                print("❌ Пожалуйста, введите число от 1 до 4")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена пользователем")
            raise SystemExit(0)
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def show_mode_selection() -> int:
    """Показывает меню выбора режима работы и возвращает выбранный режим."""
    print("\n" + "="*60)
    print("🤖 TG-Guard - Выбор режима работы")
    print("="*60)
    print("1. 🔍 Сканирование присутствия TRACKED пользователей")
    print("2. 🧹 Удаление ВСЕХ сообщений BLACKLIST пользователей")
    print("3. 🚫 Удаление только НОВЫХ сообщений BLACKLIST пользователей")
    print("4. 🔄 Комбинированный режим (все функции)")
    print("="*60)
    
    while True:
        try:
            choice = input("Выберите режим (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            else:
                print("❌ Пожалуйста, введите число от 1 до 4")
        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена пользователем")
            raise SystemExit(0)
        except Exception:
            print("❌ Неверный ввод. Попробуйте снова")
