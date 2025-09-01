# main.py
import asyncio
import os
from typing import Iterable, List, Set, Dict, Union

from dotenv import load_dotenv
from telethon import TelegramClient, events, errors, functions
from telethon.tl.types import Channel, Chat, User, Dialog
from telethon.utils import get_display_name

# --- Загрузка конфигурации ---
from config import TRACKED, BLACKLIST, EXPORT_GROUP, DELETE_CHUNK, DELETE_PAUSE, ON_START_PURGE

load_dotenv()

API_ID_STR = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION')

# Проверка и преобразование API_ID в число
try:
    API_ID = int(API_ID_STR)
except (ValueError, TypeError):
    print("❌ Ошибка: API_ID в файле .env должен быть числом.")
    exit(1)

if not all([API_ID, API_HASH, SESSION]):
    print("❌ Ошибка: Не все переменные (API_ID, API_HASH, SESSION) заданы в файле .env.")
    exit(1)


# --- Вспомогательные функции ---

def is_group(entity) -> bool:
    """
    Проверяет, является ли сущность группой или супергруппой (но не каналом).
    """
    if isinstance(entity, Chat):
        return True  # Это старая, обычная группа
    if isinstance(entity, Channel) and getattr(entity, 'megagroup', False):
        return True  # Это супергруппа
    return False


def normalize_username(x: str) -> str:
    """Убирает @ из начала юзернейма, если он есть."""
    return x[1:] if isinstance(x, str) and x.startswith("@") else x


async def resolve_users(client: TelegramClient, ids_or_usernames: Iterable) -> Dict[int, str]:
    """Превращает список юзернеймов/ID в словарь {user_id: display_name}."""
    resolved = {}
    for item in ids_or_usernames:
        try:
            entity = await client.get_entity(normalize_username(item))
            if isinstance(entity, User):
                resolved[entity.id] = get_display_name(entity) or (entity.username or str(entity.id))
        except Exception as e:
            print(f"[WARN] Не удалось определить пользователя '{item}': {e}")
    return resolved


async def delete_ids_for_me(client: TelegramClient, entity, ids: List[int]) -> int:
    """Удаляет пачку сообщений 'только для меня' с обработкой FloodWait."""
    if not ids:
        return 0
    
    total_deleted = 0
    for i in range(0, len(ids), DELETE_CHUNK):
        chunk = ids[i:i + DELETE_CHUNK]
        while True:
            try:
                # revoke=False => "удалить только для меня"
                await client.delete_messages(entity, chunk, revoke=False)
                total_deleted += len(chunk)
                await asyncio.sleep(DELETE_PAUSE)
                break
            except errors.FloodWaitError as e:
                print(f"[FLOOD] Слишком много запросов. Жду {e.seconds} секунд...")
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении сообщений: {e}")
                break  # Пропускаем эту пачку при неизвестной ошибке
    return total_deleted


async def purge_user_everywhere(client: TelegramClient, user_id: int, user_name: str):
    """Удаляет все сообщения пользователя по всем диалогам."""
    print(f"[PURGE] ⏳ Начинаю зачистку сообщений от '{user_name}'...")
    total_deleted_count = 0
    dialog_count = 0
    
    try:
        async for dialog in client.iter_dialogs():
            dialog_count += 1
            print(f"\r[PURGE] Проверяю диалог {dialog_count}: {dialog.name}", end="")
            ids_to_delete = []
            try:
                async for msg in client.iter_messages(dialog.entity, from_user=user_id):
                    ids_to_delete.append(msg.id)
                
                if ids_to_delete:
                    deleted_in_chat = await delete_ids_for_me(client, dialog.entity, ids_to_delete)
                    total_deleted_count += deleted_in_chat

            except Exception as e:
                # Некоторые чаты могут быть недоступны, это нормально
                pass
    finally:
        print() # Перевод строки после завершения цикла
        
    print(f"[PURGE] ✅ Зачистка для '{user_name}' завершена. Удалено сообщений: {total_deleted_count}")
    await client.send_message(
        "me",
        f"✅ Зачистка завершена: удалено **{total_deleted_count}** сообщений от *{user_name}*."
    )


async def initial_presence_scan(client: TelegramClient, tracked_map: Dict[int, str]):
    """При запуске проверяет, в каких группах уже состоят отслеживаемые пользователи."""
    print("[SCAN] 🕵️ Проверяю текущее присутствие отслеживаемых пользователей (только в чатах)...")
    found_count = 0
    async for dialog in client.iter_dialogs():
        # >>> ИЗМЕНЕНИЕ ЗДЕСЬ: Проверяем только чаты
        if is_group(dialog.entity):
            for user_id, user_name in tracked_map.items():
                try:
                    # Этот вызов вызовет ошибку, если пользователя в чате нет
                    await client(functions.channels.GetParticipantRequest(channel=dialog.entity, participant=user_id))
                    message = f"ℹ️ **Уже в группе:** `{user_name}` состоит в чате «*{dialog.name}*»"
                    await client.send_message("me", message, parse_mode='md')
                    found_count += 1
                except errors.UserNotParticipantError:
                    pass  # Всё в порядке, пользователя просто нет в этой группе
                except Exception:
                    pass # Другие возможные ошибки (например, нет прав)
    print(f"[SCAN] ✅ Проверка завершена. Найдено совпадений: {found_count}.")


async def get_users_from_group(client: TelegramClient, group_identifier: Union[str, int]):
    """Получает всех участников из группы и возвращает их юзернеймы."""
    if not group_identifier:
        return set()
        
    print(f"[EXPORT] ⏳ Загружаю участников из группы '{group_identifier}'...")
    try:
        group_entity = await client.get_entity(group_identifier)
        participants = await client.get_participants(group_entity)
        
        # Собираем юзернеймы, если они есть. Можно добавить и ID, если нужно.
        usernames = {f"@{user.username}" for user in participants if user.username}
        print(f"[EXPORT] ✅ Найдено {len(usernames)} уникальных пользователей с юзернеймами.")
        return usernames
    except Exception as e:
        print(f"[ERROR] Не удалось получить участников из '{group_identifier}': {e}")
        return set()


# --- Основная логика ---

async def main():
    print("🚀 Запускаю Telegram-клиент...")
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"✅ Вход выполнен как: {get_display_name(me)}")

        # 1. Формируем итоговый список для отслеживания
        tracked_users_set = set(TRACKED)
        exported_users = await get_users_from_group(client, EXPORT_GROUP)
        tracked_users_set.update(exported_users)

        # 2. Преобразуем юзернеймы в ID для быстрой работы
        tracked_map = await resolve_users(client, tracked_users_set)
        blacklist_map = await resolve_users(client, BLACKLIST)
        
        tracked_ids: Set[int] = set(tracked_map.keys())
        blacklist_ids: Set[int] = set(blacklist_map.keys())

        print("\n--- Итоговые списки ---")
        print(f"👀 Отслеживаем ({len(tracked_map)}): {list(tracked_map.values())}")
        print(f"🚫 Чёрный список ({len(blacklist_map)}): {list(blacklist_map.values())}\n")

        # 3. Запускаем начальные проверки
        if ON_START_PURGE and blacklist_ids:
            for user_id, user_name in blacklist_map.items():
                await purge_user_everywhere(client, user_id, user_name)

        if tracked_ids:
            await initial_presence_scan(client, tracked_map)

        # 4. Регистрируем обработчики событий
        @client.on(events.ChatAction)
        async def on_chat_action(event: events.ChatAction.Event):
            if event.user_joined or event.user_added:
                # >>> ИЗМЕНЕНИЕ ЗДЕСЬ: Проверяем, что событие произошло в чате
                chat = await event.get_chat()
                if not is_group(chat):
                    return

                user = await event.get_user()
                if user and user.id in tracked_ids:
                    await client.send_message(
                        "me",
                        f"🚨🚨🚨 **Обнаружен пользователь!** 🚨🚨🚨\n\n"
                        f"**Кто:** `{get_display_name(user)}`\n"
                        f"**Где:** «*{get_display_name(chat)}*»",
                        parse_mode='md'
                    )

        @client.on(events.NewMessage)
        async def on_new_message(event: events.NewMessage.Event):
            if event.sender_id in blacklist_ids:
                try:
                    await event.delete(use_for_everyone=False)
                except Exception:
                    pass # Ошибки тут не критичны

        print("\n✅ Скрипт запущен и слушает события...")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())