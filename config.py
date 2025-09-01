# Список пользователей для отслеживания (юзернеймы с @ или без)
TRACKED = ["@lokkopy", "@F2ki52", "@yaystalfxck", "@Sunshess228", "@y4rz0r", "@Voronovshina", "@absence_of_fear", "@Vlaudic", "@ChocoRobotsAndGonOneLove_bykilla", "@btlvm", "@Ront0s", "@SeVeesh", "@MaxBaran1", "@Kanitelka21", "@semigal01", "@lilboo8", "@KKUST1", "@elisstarkovskaya", "@Shimichka"]

# Список пользователей в чёрном списке (их сообщения будут удаляться)
BLACKLIST = ["@lokkopy"]

# Группа для экспорта участников (добавляются к TRACKED)
EXPORT_GROUP = ""

# Настройки автоудаления сообщений в 'Избранном'
DELETE_SAVED_DELAY_SECONDS = 30  # Задержка перед удалением (в секундах)
DELETE_SAVED_MESSAGES = True     # Включить автоудаление сообщений в 'Избранном'

# Настройки массового удаления
DELETE_CHUNK = 100       # Максимум сообщений за один запрос
DELETE_PAUSE = 0.6       # Пауза между пачками (в секундах)

# Устаревшая настройка (теперь управляется через меню)
ON_START_PURGE = True    # Используется только в комбинированном режиме

# Дополнительные настройки для новых режимов
ENABLE_LOGGING = True    # Включить подробное логирование действий
SHOW_DELETION_NOTIFICATIONS = True  # Показывать уведомления об удалении сообщений