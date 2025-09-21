import asyncio
from typing import List, Dict
from telethon import TelegramClient, events, errors
from telethon.tl.types import Message
from telethon.utils import get_display_name

from .config_manager import get_config
from .utils import is_broadcast_channel, is_alert_message_text


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


async def send_to_saved(client: TelegramClient, text: str, keep: bool = False, parse_mode: str = 'md') -> Message:
    """
    Отправляет сообщение себе ('Избранное'). Если keep=False и включен режим,
    планирует автоудаление через DELETE_SAVED_DELAY_SECONDS.
    """
    config = get_config()
    msg = await client.send_message("me", text, parse_mode=parse_mode)
    if config['DELETE_SAVED_MESSAGES'] and not keep:
        asyncio.create_task(
            schedule_delete_message(
                client, "me", [msg.id], config['DELETE_SAVED_DELAY_SECONDS']
            )
        )
    return msg


async def delete_ids_for_me(client: TelegramClient, entity, ids: List[int]) -> int:
    """Удаляет пачку сообщений 'только для меня' с обработкой FloodWait."""
    if not ids:
        return 0

    config = get_config()
    total_deleted = 0
    for i in range(0, len(ids), config['DELETE_CHUNK']):
        chunk = ids[i:i + config['DELETE_CHUNK']]
        while True:
            try:
                await client.delete_messages(entity, chunk, revoke=False)
                total_deleted += len(chunk)
                await asyncio.sleep(config['DELETE_PAUSE'])
                break
            except errors.FloodWaitError as e:
                print(f"[FLOOD] Слишком много запросов. Жду {e.seconds} секунд...")
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении сообщений: {e}")
                break
    return total_deleted


async def purge_user_everywhere(client: TelegramClient, user_id: int, user_name: str):
    """Удаляет все сообщения пользователя во всех ЛС и группах (каналы игнорируются)."""
    from .utils import is_personal, is_group
    
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


async def purge_own_messages_everywhere(client: TelegramClient, me_id: int, exclusion_map: Dict[int, str]):
    """
    Удаляет все собственные сообщения во всех чатах,
    кроме тех, что с пользователями из списка исключений.
    """
    from .utils import is_personal, is_group
    
    print(f"[SELF-PURGE] ⚠️  Начинаю самоочистку всех сообщений...")
    print(f"[SELF-PURGE] 🔒 Исключения ({len(exclusion_map)}): {list(exclusion_map.values())}")
    
    total_deleted_count = 0
    dialog_count = 0
    excluded_dialogs = 0
    
    try:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            
            # Сканим только ЛС и группы (ни одного канала)
            if not (is_personal(entity) or is_group(entity)):
                continue
                
            dialog_count += 1
            
            # Проверяем, не в списке ли исключений этот чат
            should_exclude = False
            
            if is_personal(entity):
                # Личный чат - проверяем ID пользователя
                if entity.id in exclusion_map:
                    should_exclude = True
                    excluded_dialogs += 1
                    print(f"[SELF-PURGE] 🔒 Пропускаю ЛС с {exclusion_map[entity.id]}")
            
            if should_exclude:
                continue
            
            print(f"\r[SELF-PURGE] ⚙️ Проверяю диалог {dialog_count}: {dialog.name}", end="")
            
            ids_to_delete: List[int] = []
            try:
                # Находим все сообщения от меня
                async for msg in client.iter_messages(entity, from_user=me_id):
                    # Пропускаем оповещения в Избранном
                    if entity.id == me_id:  # Избранное
                        config = get_config()
                        text = msg.raw_text or ""
                        if is_alert_message_text(text, config['ALERT_PREFIX']):
                            continue
                    
                    ids_to_delete.append(msg.id)
                
                if ids_to_delete:
                    deleted_in_chat = await delete_ids_for_me(client, entity, ids_to_delete)
                    total_deleted_count += deleted_in_chat
                    
            except Exception as e:
                # Некоторые чаты могут быть недоступны, это не критично
                print(f"\n[SELF-PURGE] ⚠️  Ошибка в диалоге '{dialog.name}': {e}")
                pass
                
    finally:
        print()  # Перевод строки после завершения цикла
    
    print(f"[SELF-PURGE] ✅ Самоочистка завершена!")
    print(f"[SELF-PURGE] 📈 Обработано диалогов: {dialog_count}")
    print(f"[SELF-PURGE] 🔒 Пропущено (исключения): {excluded_dialogs}")
    print(f"[SELF-PURGE] 🗑️ Удалено сообщений: {total_deleted_count}")
    
    await send_to_saved(
        client,
        f"✅ **Самоочистка завершена!**\n\n"
        f"📈 **Обработано диалогов:** {dialog_count}\n"
        f"🔒 **Пропущено (исключения):** {excluded_dialogs}\n"
        f"🗝 **Удалено сообщений:** **{total_deleted_count}**",
        keep=True
    )


def setup_saved_messages_auto_delete(client: TelegramClient, me_id: int):
    """Настраивает автоудаление сообщений в 'Избранном'."""
    config = get_config()
    
    if not config['DELETE_SAVED_MESSAGES']:
        return
    
    @client.on(events.NewMessage(incoming=True, outgoing=True))
    async def on_saved_new_message(event: events.NewMessage.Event):
        try:
            if event.chat_id != me_id:
                return
            # Пиннутые не трогаем
            if event.message and event.message.pinned:
                return
            text = event.raw_text or ""
            if is_alert_message_text(text, config['ALERT_PREFIX']):
                # Оповещения — оставляем
                return
            # Удаляем через задержку
            asyncio.create_task(
                schedule_delete_message(
                    client, "me", [event.id], config['DELETE_SAVED_DELAY_SECONDS']
                )
            )
        except Exception:
            pass
