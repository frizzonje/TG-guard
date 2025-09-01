
import asyncio
from modules.telegram_client import run_telegram_client


async def main():
    """Главная функция программы."""
    try:
        await run_telegram_client()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
