
import asyncio
import os
from typing import Iterable, List, Set, Dict, Union

from dotenv import load_dotenv
from telethon import TelegramClient, events, errors, functions
from telethon.tl.types import Channel, Chat, User, Dialog, Message
from telethon.utils import get_display_name

# --- Конфигурация ---
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


# --- Интерактивная настройка списков ---
def show_list_management_menu() -> tuple:
    """Показывает меню управления списками и возвращает обновленные списки."""
    print("\n" + "="*60)
    print("⚙️ Настройка списков TRACKED и BLACKLIST")
    print("="*60)
    
    # Копируем списки из конфигурации
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


def save_config_to_file(tracked_list: List[str], blacklist_list: List[str]):
    """Сохраняет обновленные списки в файл config.py."""
    try:
        # Читаем текущий config.py
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обновляем списки в контенте
        import re
        
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


# --- Интерактивное меню выбора режима ---
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


# --- Режим 1: Сканирование присутствия TRACKED ---
async def mode_tracked_scanning(client: TelegramClient, tracked_map: Dict[int, str]):
    """Режим 1: Только сканирование присутствия TRACKED пользователей."""
    print("\n🔍 Режим: Сканирование присутствия TRACKED пользователей")
    print("="*50)
    
    if not tracked_map:
        print("⚠️ Список TRACKED пуст. Нечего отслеживать.")
        return
    
    # Регистрируем обработчик для новых вступлений в группы
    tracked_ids = set(tracked_map.keys())
    
    @client.on(events.ChatAction)
    async def on_chat_action(event: events.ChatAction.Event):
        # Нас интересуют только join/add события и только группы
        if not (event.user_joined or event.user_added):
            return
        chat = await event.get_chat()
        if not is_group(chat):
            return
        users = await event.get_users()
        for user in users:
            if user.id in tracked_ids:
                await send_to_saved(
                    client,
                    f"{ALERT_PREFIX}**Обнаружен пользователь!**\n\n"
                    f"**Кто:** `{get_display_name(user)}`\n"
                    f"**Где:** «*{get_display_name(chat)}*»",
                    keep=True
                )
    
    # Выполняем начальное сканирование
    await initial_presence_scan(client, tracked_map)
    print("✅ Режим сканирования активирован. Ожидаю новых вступлений...")


# --- Режим 2: Удаление ВСЕХ сообщений BLACKLIST ---
async def mode_blacklist_purge_all(client: TelegramClient, blacklist_map: Dict[int, str]):
    """Режим 2: Удаление ВСЕХ сообщений BLACKLIST пользователей."""
    print("\n🧹 Режим: Удаление ВСЕХ сообщений BLACKLIST пользователей")
    print("="*50)
    
    if not blacklist_map:
        print("⚠️ Список BLACKLIST пуст. Нечего удалять.")
        return
    
    # Регистрируем обработчики для новых сообщений
    blacklist_ids = set(blacklist_map.keys())
    
    @client.on(events.NewMessage(from_users=list(blacklist_ids), incoming=True))
    async def on_blacklisted_incoming(event: events.NewMessage.Event):
        try:
            chat = await event.get_chat()
            # Игнорируем каналы
            if is_broadcast_channel(chat):
                return
            await event.delete(revoke=False)
            print(f"🚫 Удалено новое сообщение от {get_display_name(await event.get_sender())}")
        except Exception as e:
            print(f"❌ Ошибка при удалении сообщения: {e}")

    @client.on(events.MessageEdited(from_users=list(blacklist_ids)))
    async def on_blacklisted_edited(event: events.MessageEdited.Event):
        try:
            chat = await event.get_chat()
            if is_broadcast_channel(chat):
                return
            await event.delete(revoke=False)
            print(f"🚫 Удалено отредактированное сообщение от {get_display_name(await event.get_sender())}")
        except Exception as e:
            print(f"❌ Ошибка при удалении отредактированного сообщения: {e}")
    
    # Выполняем начальную зачистку всех существующих сообщений
    print("🧹 Начинаю зачистку всех существующих сообщений...")
    for user_id, user_name in blacklist_map.items():
        await purge_user_everywhere(client, user_id, user_name)
    
    print("✅ Режим полной зачистки активирован. Удаляю новые сообщения...")


# --- Режим 3: Удаление только НОВЫХ сообщений BLACKLIST ---
async def mode_blacklist_new_only(client: TelegramClient, blacklist_map: Dict[int, str]):
    """Режим 3: Удаление только НОВЫХ сообщений BLACKLIST пользователей."""
    print("\n🚫 Режим: Удаление только НОВЫХ сообщений BLACKLIST пользователей")
    print("="*50)
    
    if not blacklist_map:
        print("⚠️ Список BLACKLIST пуст. Нечего удалять.")
        return
    
    # Регистрируем обработчики только для новых сообщений
    blacklist_ids = set(blacklist_map.keys())
    
    @client.on(events.NewMessage(from_users=list(blacklist_ids), incoming=True))
    async def on_blacklisted_incoming(event: events.NewMessage.Event):
        try:
            chat = await event.get_chat()
            # Игнорируем каналы
            if is_broadcast_channel(chat):
                return
            await event.delete(revoke=False)
            sender = await event.get_sender()
            chat_name = get_display_name(chat)
            print(f"🚫 Удалено новое сообщение от {get_display_name(sender)} в {chat_name}")
        except Exception as e:
            print(f"❌ Ошибка при удалении сообщения: {e}")

    @client.on(events.MessageEdited(from_users=list(blacklist_ids)))
    async def on_blacklisted_edited(event: events.MessageEdited.Event):
        try:
            chat = await event.get_chat()
            if is_broadcast_channel(chat):
                return
            await event.delete(revoke=False)
            sender = await event.get_sender()
            chat_name = get_display_name(chat)
            print(f"🚫 Удалено отредактированное сообщение от {get_display_name(sender)} в {chat_name}")
        except Exception as e:
            print(f"❌ Ошибка при удалении отредактированного сообщения: {e}")
    
    print("✅ Режим удаления новых сообщений активирован. Исторические сообщения не затрагиваются.")


# --- Режим 4: Комбинированный режим ---
async def mode_combined(client: TelegramClient, tracked_map: Dict[int, str], blacklist_map: Dict[int, str]):
    """Режим 4: Комбинированный режим - все функции."""
    print("\n🔄 Режим: Комбинированный (все функции)")
    print("="*50)
    
    # Запускаем все режимы одновременно
    if tracked_map:
        await mode_tracked_scanning(client, tracked_map)
    
    if blacklist_map:
        # В комбинированном режиме используем полную зачистку
        await mode_blacklist_purge_all(client, blacklist_map)
    
    print("✅ Комбинированный режим активирован. Все функции работают одновременно.")


# --- Вспомогательные функции типов чатов ---
def is_broadcast_channel(entity) -> bool:
    """Канал (broadcast), НЕ супергруппа."""
    return isinstance(entity, Channel) and not getattr(entity, 'megagroup', False)


def is_supergroup(entity) -> bool:
    """Супергруппа."""
    return isinstance(entity, Channel) and getattr(entity, 'megagroup', False)


def is_basic_group(entity) -> bool:
    """Обычная (старая) группа."""
    return isinstance(entity, Chat)


def is_group(entity) -> bool:
    """Любая группа: обычная или супергруппа (но не канал)."""
    return is_basic_group(entity) or is_supergroup(entity)


def is_personal(entity) -> bool:
    """Личный диалог."""
    return isinstance(entity, User)


def normalize_username(x: str) -> str:
    """Убирает @ из начала юзернейма, если он есть."""
    return x[1:] if isinstance(x, str) and x.startswith("@") else x


# --- Утилиты работы с пользователями ---
async def resolve_users(client: TelegramClient, ids_or_usernames: Iterable) -> Dict[int, str]:
    """Превращает список юзернеймов/ID в словарь {user_id: display_name}."""
    resolved: Dict[int, str] = {}
    for item in ids_or_usernames:
        try:
            entity = await client.get_entity(normalize_username(item))
            if isinstance(entity, User):
                resolved[entity.id] = get_display_name(entity) or (entity.username or str(entity.id))
        except Exception as e:
            print(f"[WARN] Не удалось определить пользователя '{item}': {e}")
    return resolved


# --- Отправка и автоудаление в 'Избранном' ---
async def schedule_delete_message(client: TelegramClient, entity, ids: List[int], delay: int):
    """Задержка и удаление сообщений (только для меня), с обработкой ошибок."""
    try:
        await asyncio.sleep(delay)
        if not ids:
            return
        await client.delete_messages(entity, ids, revoke=False)
        print(f"[AUTO-DELETE] ✅ Удалены {len(ids)} сообщ. в '{get_display_name(entity) if entity != 'me' else 'Избранном'}'")
    except errors.FloodWaitError as e:
        print(f"[AUTO-DELETE] [FLOOD] Жду {e.seconds} сек...")
        await asyncio.sleep(e.seconds + 1)
    except Exception as e:
        print(f"[AUTO-DELETE] [WARN] Ошибка при удалении: {e}")


async def send_to_saved(client: TelegramClient, text: str, keep: bool = False, parse_mode: str = MD) -> Message:
    """
    Отправляет сообщение себе ('Избранное'). Если keep=False и включен режим,
    планирует автоудаление через DELETE_SAVED_DELAY_SECONDS.
    """
    msg = await client.send_message("me", text, parse_mode=parse_mode)
    if DELETE_SAVED_MESSAGES and not keep:
        asyncio.create_task(schedule_delete_message(client, "me", [msg.id], DELETE_SAVED_DELAY_SECONDS))
    return msg


def is_alert_message_text(text: str) -> bool:
    """Вернуть True, если это оповещение, которое нельзя удалять из 'Избранного'."""
    if not isinstance(text, str):
        return False
    return text.startswith(ALERT_PREFIX)


# --- Массовое удаление сообщений ---
async def delete_ids_for_me(client: TelegramClient, entity, ids: List[int]) -> int:
    """Удаляет пачку сообщений 'только для меня' с обработкой FloodWait."""
    if not ids:
        return 0

    total_deleted = 0
    for i in range(0, len(ids), DELETE_CHUNK):
        chunk = ids[i:i + DELETE_CHUNK]
        while True:
            try:
                await client.delete_messages(entity, chunk, revoke=False)
                total_deleted += len(chunk)
                await asyncio.sleep(DELETE_PAUSE)
                break
            except errors.FloodWaitError as e:
                print(f"[FLOOD] Слишком много запросов. Жду {e.seconds} секунд...")
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении сообщений: {e}")
                break
    return total_deleted


# --- Пуржинг по всем разрешенным диалогам (без обычных каналов) ---
async def purge_user_everywhere(client: TelegramClient, user_id: int, user_name: str):
    """Удаляет все сообщения пользователя во всех ЛС и группах (каналы игнорируются)."""
    print(f"[PURGE] ⏳ Начинаю зачистку сообщений от '{user_name}'...")
    total_deleted_count = 0
    dialog_count = 0

    try:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            # Сканим только ЛС и группы (ни одного канала)
            if not (is_personal(entity) or is_group(entity)):
                continue

            dialog_count += 1
            print(f"\r[PURGE] Проверяю диалог {dialog_count}: {dialog.name}", end="")
            ids_to_delete: List[int] = []
            try:
                async for msg in client.iter_messages(entity, from_user=user_id):
                    ids_to_delete.append(msg.id)

                if ids_to_delete:
                    deleted_in_chat = await delete_ids_for_me(client, entity, ids_to_delete)
                    total_deleted_count += deleted_in_chat

            except Exception:
                # Некоторые чаты могут быть недоступны, это не критично
                pass
    finally:
        print()  # Перевод строки после завершения цикла

    print(f"[PURGE] ✅ Зачистка для '{user_name}' завершена. Удалено сообщений: {total_deleted_count}")
    await send_to_saved(
        client,
        f"✅ Зачистка завершена: удалено **{total_deleted_count}** сообщений от *{user_name}*.",
        keep=False
    )


# --- Начальное сканирование присутствия только в ЛС и группах (без каналов) ---
async def initial_presence_scan(client: TelegramClient, tracked_map: Dict[int, str]):
    """
    При запуске проверяет, где уже состоят отслеживаемые пользователи:
    - Личные диалоги (DM)
    - Группы и супергруппы
    Каналы (broadcast) игнорируются.
    """
    if not tracked_map:
        return

    print("[SCAN] 🕵️ Проверяю текущее присутствие отслеживаемых пользователей (ЛС и группы)...")
    found_count = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        # 1) ЛС
        if is_personal(entity):
            user_id = entity.id
            if user_id in tracked_map:
                user_name = tracked_map[user_id]
                message = f"ℹ️ **Уже в личном диалоге:** `{user_name}`"
                await send_to_saved(client, message, keep=False)
                found_count += 1
            continue

        # 2) Группы и супергруппы
        if is_group(entity):
            # Супергруппа — быстрый запрос участника
            if is_supergroup(entity):
                for user_id, user_name in tracked_map.items():
                    try:
                        await client(functions.channels.GetParticipantRequest(
                            channel=entity,
                            participant=user_id
                        ))
                        msg = f"ℹ️ **Уже в группе:** `{user_name}` состоит в чате «*{dialog.name}*»"
                        await send_to_saved(client, msg, keep=False)
                        found_count += 1
                    except errors.UserNotParticipantError:
                        pass
                    except Exception:
                        pass
                continue

            # Обычная группа — проверяем список участников (для небольших чатов)
            if is_basic_group(entity):
                try:
                    participants = await client.get_participants(entity)
                    ids = {p.id for p in participants if isinstance(p, User)}
                    for user_id in list(tracked_map.keys()):
                        if user_id in ids:
                            user_name = tracked_map[user_id]
                            msg = f"ℹ️ **Уже в группе:** `{user_name}` состоит в чате «*{dialog.name}*»"
                            await send_to_saved(client, msg, keep=False)
                            found_count += 1
                except Exception:
                    # нет прав или группа недоступна
                    pass

        # 3) Каналы игнорируем полностью
        # if is_broadcast_channel(entity): continue

    print(f"[SCAN] ✅ Проверка завершена. Найдено совпадений: {found_count}.")


# --- Экспорт участников из группы/супергруппы (опционально) ---
async def get_users_from_group(client: TelegramClient, group_identifier: Union[str, int]):
    """Возвращает юзернеймы участников, если это группа/супергруппа (канал игнорируется)."""
    if not group_identifier:
        return set()

    print(f"[EXPORT] ⏳ Загружаю участников из '{group_identifier}'...")
    try:
        group_entity = await client.get_entity(group_identifier)

        if is_broadcast_channel(group_entity):
            print(f"[EXPORT] ℹ️ '{group_identifier}' является каналом. Экспорт участников пропущен.")
            return set()

        participants = await client.get_participants(group_entity)
        usernames = {f"@{user.username}" for user in participants if isinstance(user, User) and user.username}
        print(f"[EXPORT] ✅ Найдено {len(usernames)} уникальных пользователей с юзернеймами.")
        return usernames
    except Exception as e:
        print(f"[ERROR] Не удалось получить участников из '{group_identifier}': {e}")
        return set()


# --- Основная логика ---
async def main():
    print("🚀 Запускаю Telegram-клиент...")
    
    # Показываем меню настройки списков
    print("\n" + "="*60)
    print("🤖 TG-Guard - Настройка и запуск")
    print("="*60)
    
    # Настройка списков
    tracked_list, blacklist_list = show_list_management_menu()
    
    # Показываем меню выбора режима
    selected_mode = show_mode_selection()
    
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        me = await client.get_me()
        me_id = me.id
        print(f"✅ Вход выполнен как: {get_display_name(me)}")

        # 1) Формируем итоговый набор отслеживаемых (TRACKED + EXPORT_GROUP)
        tracked_users_set = set(tracked_list)  # Используем настроенный список
        exported_users = await get_users_from_group(client, EXPORT_GROUP)
        tracked_users_set.update(exported_users)

        # 2) Резолвим юзернеймы в ID
        tracked_map = await resolve_users(client, tracked_users_set)
        blacklist_map = await resolve_users(client, blacklist_list)  # Используем настроенный список

        print("\n--- Итоговые списки ---")
        print(f"👀 Отслеживаем ({len(tracked_map)}): {list(tracked_map.values())}")
        print(f"🚫 Чёрный список ({len(blacklist_map)}): {list(blacklist_map.values())}\n")

        # 3) Регистрация обработчиков автоудаления в 'Избранном' (если включено)
        if DELETE_SAVED_MESSAGES:
            @client.on(events.NewMessage(incoming=True, outgoing=True))
            async def on_saved_new_message(event: events.NewMessage.Event):
                try:
                    if event.chat_id != me_id:
                        return
                    # Пиннутые не трогаем
                    if event.message and event.message.pinned:
                        return
                    text = event.raw_text or ""
                    if is_alert_message_text(text):
                        # Оповещения — оставляем
                        return
                    # Удаляем через задержку
                    asyncio.create_task(
                        schedule_delete_message(
                            client, "me", [event.id], DELETE_SAVED_DELAY_SECONDS
                        )
                    )
                except Exception:
                    pass

        # 4) Запускаем выбранный режим
        if selected_mode == 1:
            await mode_tracked_scanning(client, tracked_map)
        elif selected_mode == 2:
            await mode_blacklist_purge_all(client, blacklist_map)
        elif selected_mode == 3:
            await mode_blacklist_new_only(client, blacklist_map)
        elif selected_mode == 4:
            await mode_combined(client, tracked_map, blacklist_map)

        print("\n✅ Скрипт запущен и слушает события...")
        print("💡 Для остановки нажмите Ctrl+C")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
