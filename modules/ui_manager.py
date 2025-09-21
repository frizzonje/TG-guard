from typing import List, Tuple
from .config_manager import save_config_to_file
from .ui_enhanced import (
    Colors, print_header, print_section, print_box, print_menu_option,
    print_list_items, print_status, get_input_with_prompt, print_separator,
    clear_screen
)


def show_list_management_menu() -> Tuple[List[str], List[str], List[str]]:
    """Показывает меню управления списками и возвращает обновленные списки."""
    print_header("⚙️ TG-Guard - Настройка списков", "Управление TRACKED, BLACKLIST и EXCLUSION")
    
    # Копируем списки из конфигурации
    from config import TRACKED, BLACKLIST, EXCLUSION_LIST
    current_tracked = list(TRACKED)
    current_blacklist = list(BLACKLIST)
    current_exclusion = list(EXCLUSION_LIST)
    
    while True:
        # Показываем текущие списки
        print_section("Текущие списки")
        
        print_list_items(current_tracked, "TRACKED (отслеживаемые)", "👀", Colors.BRIGHT_GREEN)
        print_list_items(current_blacklist, "BLACKLIST (чёрный список)", "🚫", Colors.BRIGHT_RED)
        print_list_items(current_exclusion, "EXCLUSION (исключения для самоочистки)", "🔒", Colors.BRIGHT_BLUE)
        
        print_separator()
        print_menu_option(1, "✏️", "Редактировать TRACKED", "список отслеживаемых")
        print_menu_option(2, "✏️", "Редактировать BLACKLIST", "чёрный список")
        print_menu_option(3, "🔒", "Редактировать EXCLUSION", "исключения для самоочистки", Colors.BRIGHT_CYAN)
        print_menu_option(4, "🔄", "Сбросить к config.py", "восстановить настройки", Colors.BRIGHT_YELLOW)
        print_menu_option(5, "✅", "Продолжить", "с текущими настройками", Colors.BRIGHT_GREEN)
        print_menu_option(6, "💾", "Сохранить в config.py", "записать изменения", Colors.BRIGHT_MAGENTA)
        
        try:
            choice = get_input_with_prompt("Выберите действие (1-6):", "choice")
            
            if choice == "1":
                current_tracked = edit_tracked_list(current_tracked)
            elif choice == "2":
                current_blacklist = edit_blacklist_list(current_blacklist)
            elif choice == "3":
                current_exclusion = edit_exclusion_list(current_exclusion)
            elif choice == "4":
                from config import TRACKED, BLACKLIST, EXCLUSION_LIST
                current_tracked = list(TRACKED)
                current_blacklist = list(BLACKLIST)
                current_exclusion = list(EXCLUSION_LIST)
                print_status("Списки сброшены к настройкам из config.py", "success")
            elif choice == "5":
                return current_tracked, current_blacklist, current_exclusion
            elif choice == "6":
                save_config_to_file(current_tracked, current_blacklist, current_exclusion)
                return current_tracked, current_blacklist, current_exclusion
            else:
                print_status("Неверный выбор. Пожалуйста, введите число от 1 до 6", "error")
                
        except KeyboardInterrupt:
            print_status("Программа завершена пользователем", "info")
            raise SystemExit(0)
        except Exception as e:
            print_status(f"Ошибка: {e}", "error")


def edit_tracked_list(current_list: List[str]) -> List[str]:
    """Редактирует список TRACKED."""
    print_header("👀 Редактирование TRACKED", "Список отслеживаемых пользователей")
    
    info_box = [
        "Пользователи из этого списка будут отслеживаться:",
        "• При вступлении в группы",
        "• При появлении онлайн в личных чатах",
        "Уведомления отправляются в Избранное"
    ]
    print_box(info_box, "👀 О списке TRACKED", "info")
    
    while True:
        print_list_items(current_list, "TRACKED", "👀", Colors.BRIGHT_GREEN)
        
        print_separator()
        print_menu_option(1, "➕", "Добавить", "нового пользователя", Colors.BRIGHT_GREEN)
        print_menu_option(2, "➖", "Удалить", "по номеру", Colors.BRIGHT_RED)
        print_menu_option(3, "🔄", "Очистить", "весь список", Colors.BRIGHT_YELLOW)
        print_menu_option(4, "✅", "Вернуться", "к основному меню", Colors.BRIGHT_BLUE)
        
        try:
            choice = get_input_with_prompt("Выберите действие (1-4):", "choice")
            
            if choice == "1":
                username = get_input_with_prompt("Введите юзернейм (с @ или без):", "username")
                if username:
                    if not username.startswith("@"):
                        username = "@" + username
                    if username not in current_list:
                        current_list.append(username)
                        print_status(f"Добавлен: {username}", "success")
                    else:
                        print_status(f"{username} уже в списке", "warning")
                else:
                    print_status("Юзернейм не может быть пустым", "error")
                    
            elif choice == "2":
                if not current_list:
                    print_status("Список пуст", "warning")
                    continue
                    
                try:
                    index_str = get_input_with_prompt(f"Введите номер (1-{len(current_list)}):", "choice")
                    index = int(index_str) - 1
                    if 0 <= index < len(current_list):
                        removed = current_list.pop(index)
                        print_status(f"Удален: {removed}", "success")
                    else:
                        print_status("Неверный номер", "error")
                except ValueError:
                    print_status("Необходимо ввести число", "error")
                    
            elif choice == "3":
                if current_list:
                    confirm = get_input_with_prompt("Очистить весь список? (да/нет):", "danger")
                    if confirm.lower() in ["да", "yes", "y", "я"]:
                        current_list.clear()
                        print_status("Список очищен", "success")
                    else:
                        print_status("Отменено", "info")
                else:
                    print_status("Список уже пуст", "warning")
                    
            elif choice == "4":
                return current_list
            else:
                print_status("Неверный выбор. Введите число от 1 до 4", "error")
                
        except KeyboardInterrupt:
            print_status("Программа завершена пользователем", "info")
            raise SystemExit(0)
        except Exception as e:
            print_status(f"Ошибка: {e}", "error")


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
    print("4. 🔄 Комбинированный режим (все функции выше)")
    print("5. 🗑️ Удаление всех собственных сообщений (кроме исключений)")
    print("="*60)
    
    while True:
        try:
            choice = input("Выберите режим (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                if choice == '5':
                    print("\n🚨 ВНИМАНИЕ! Вы выбрали режим самоочистки!")
                    print("🗑️ Это удалит все ваши сообщения во всех чатах, кроме тех, что в списке исключений")
                    confirm = input("Продолжить? (да/нет): ").strip().lower()
                    if confirm not in ["да", "yes", "y", "я"]:
                        print("❌ Отменено")
                        continue
                return int(choice)
            else:
                print("❌ Пожалуйста, введите число от 1 до 5")
        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена пользователем")
            raise SystemExit(0)
        except Exception:
            print("❌ Неверный ввод. Попробуйте снова")


def edit_exclusion_list(current_list: List[str]) -> List[str]:
    """Редактирует список EXCLUSION."""
    print(f"\n🔒 Редактирование списка EXCLUSION (исключения)")
    print("="*50)
    print("⚠️ Это пользователи, с которыми ваши сообщения НЕ будут удаляться при самоочистке")
    
    while True:
        print(f"\n📋 Текущий список EXCLUSION ({len(current_list)}):")
        if current_list:
            for i, user in enumerate(current_list, 1):
                print(f"  {i}. {user}")
        else:
            print("  (пусто)")
        
        print("\nДействия:")
        print("1. ➕ Добавить пользователя (сообщения с ним сохранятся)")
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
                        print(f"✅ Добавлен в исключения: {username}")
                        print("🔒 Сообщения с этим пользователем НЕ будут удаляться")
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
                        print(f"✅ Удален из исключений: {removed}")
                        print("⚠️ Теперь сообщения с этим пользователем будут удаляться")
                    else:
                        print("❌ Неверный номер")
                except ValueError:
                    print("❌ Введите число")
                    
            elif choice == "3":
                if current_list:
                    confirm = input("⚠️ Очистить весь список исключений? (да/нет): ").strip().lower()
                    if confirm in ["да", "yes", "y", "я"]:
                        current_list.clear()
                        print("✅ Список очищен")
                        print("🚨 ВНИМАНИЕ: Теперь при самоочистке будут удалены ВСЕ ваши сообщения!")
                    else:
                        print("❌ Отменено")
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
