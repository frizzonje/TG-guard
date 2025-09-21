from telethon import TelegramClient
from telethon.utils import get_display_name

from .config_manager import get_config
from .ui_manager import show_list_management_menu, show_mode_selection
from .utils import resolve_users
from .message_handler import setup_saved_messages_auto_delete
from .modes import (
    mode_tracked_scanning, mode_blacklist_purge_all, 
    mode_blacklist_new_only, mode_combined, mode_self_purge, get_users_from_group
)


async def run_telegram_client():
    """Основная функция для запуска Telegram клиента."""
    print("🚀 Запускаю Telegram-клиент...")
    
    # Показываем меню настройки списков
    print("\n" + "="*60)
    print("🤖 TG-Guard - Настройка и запуск")
    print("="*60)
    
    # Настройка списков
    tracked_list, blacklist_list, exclusion_list = show_list_management_menu()
    
    # Показываем меню выбора режима
    selected_mode = show_mode_selection()
    
    config = get_config()
    async with TelegramClient(config['SESSION'], config['API_ID'], config['API_HASH']) as client:
        me = await client.get_me()
        me_id = me.id
        print(f"✅ Вход выполнен как: {get_display_name(me)}")

        # 1) Формируем итоговый набор отслеживаемых (TRACKED + EXPORT_GROUP)
        tracked_users_set = set(tracked_list)  # Используем настроенный список
        exported_users = await get_users_from_group(client, config['EXPORT_GROUP'])
        tracked_users_set.update(exported_users)

        # 2) Резолвим юзернеймы в ID
        tracked_map = await resolve_users(client, tracked_users_set)
        blacklist_map = await resolve_users(client, blacklist_list)  # Используем настроенный список
        exclusion_map = await resolve_users(client, exclusion_list)  # Резолвим список исключений

        print("\n--- Итоговые списки ---")
        print(f"👀 Отслеживаем ({len(tracked_map)}): {list(tracked_map.values())}")
        print(f"🚫 Чёрный список ({len(blacklist_map)}): {list(blacklist_map.values())}")
        print(f"🔒 Исключения ({len(exclusion_map)}): {list(exclusion_map.values())}\n")

        # 3) Регистрация обработчиков автоудаления в 'Избранном' (если включено)
        setup_saved_messages_auto_delete(client, me_id)

        # 4) Запускаем выбранный режим
        if selected_mode == 1:
            await mode_tracked_scanning(client, tracked_map)
        elif selected_mode == 2:
            await mode_blacklist_purge_all(client, blacklist_map)
        elif selected_mode == 3:
            await mode_blacklist_new_only(client, blacklist_map)
        elif selected_mode == 4:
            await mode_combined(client, tracked_map, blacklist_map)
        elif selected_mode == 5:
            await mode_self_purge(client, me_id, exclusion_map)
            return  # Выходим после самоочистки, не слушаем события

        print("\n✅ Скрипт запущен и слушает события...")
        print("💡 Для остановки нажмите Ctrl+C")
        await client.run_until_disconnected()
