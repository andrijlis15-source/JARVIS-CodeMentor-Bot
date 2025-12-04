import asyncio
import logging

from aiogram import Bot, Dispatcher
from telegram_bot.config import BOT_TOKEN
from telegram_bot.handlers import router 

async def main():
    # Встановлення рівня логування
    logging.basicConfig(level=logging.INFO)
    
    # Ініціалізація бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Реєстрація роутера, що містить всю логіку
    dp.include_router(router) 

    print("J.A.R.V.I.S. is starting...")
    # Видалення старих вебхуків та запуск поллінгу
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("J.A.R.V.I.S. has been shut down.")