from typing import Iterable, Dict
from telethon.tl.types import Channel, Chat, User
from telethon.utils import get_display_name


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


async def resolve_users(client, ids_or_usernames: Iterable) -> Dict[int, str]:
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


def is_alert_message_text(text: str, alert_prefix: str) -> bool:
    """Вернуть True, если это оповещение, которое нельзя удалять из 'Избранного'."""
    if not isinstance(text, str):
        return False
    return text.startswith(alert_prefix)
