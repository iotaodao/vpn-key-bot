# -*- coding: utf-8 -*-
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config import BOT_TOKEN, ADMIN_IDS
from database import UserDatabase
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация базы данных
db = UserDatabase()

async def on_startup(dp):
    """Функция, выполняемая при запуске бота"""
    logger.info("Бот запущен и готов к работе!")
    
    # Отправка уведомления администраторам о запуске
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, 
                "🤖 VPN Support Bot запущен и готов к работе!"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение админу {admin_id}: {e}")

async def on_shutdown(dp):
    """Функция, выполняемая при остановке бота"""
    logger.info("Бот остановлен")

def main():
    """Основная функция запуска бота"""
    # Регистрация обработчиков
    register_handlers(dp, db)
    
    # Запуск бота
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )

if __name__ == '__main__':
    main()
