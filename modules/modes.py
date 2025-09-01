from typing import Dict
from telethon import TelegramClient, events, errors, functions
from telethon.utils import get_display_name

from .config_manager import get_config
from .utils import is_group, is_broadcast_channel, is_personal, is_supergroup, is_basic_group
from .message_handler import send_to_saved, purge_user_everywhere


async def mode_tracked_scanning(client: TelegramClient, tracked_map: Dict[int, str]):
    """Режим 1: Только сканирование присутствия TRACKED пользователей."""
    print("\n🔍 Режим: Сканирование присутствия TRACKED пользователей")
    print("="*50)
    
    if not tracked_map:
        print("⚠️ Список TRACKED пуст. Нечего отслеживать.")
        return
    
    config = get_config()
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
                    f"{config['ALERT_PREFIX']}**Обнаружен пользователь!**\n\n"
                    f"**Кто:** `{get_display_name(user)}`\n"
                    f"**Где:** «*{get_display_name(chat)}*»",
                    keep=True
                )
    
    # Выполняем начальное сканирование
    await initial_presence_scan(client, tracked_map)
    print("✅ Режим сканирования активирован. Ожидаю новых вступлений...")


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
                    from telethon.tl.types import User
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


async def get_users_from_group(client: TelegramClient, group_identifier):
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
        from telethon.tl.types import User
        usernames = {f"@{user.username}" for user in participants if isinstance(user, User) and user.username}
        print(f"[EXPORT] ✅ Найдено {len(usernames)} уникальных пользователей с юзернеймами.")
        return usernames
    except Exception as e:
        print(f"[ERROR] Не удалось получить участников из '{group_identifier}': {e}")
        return set()
