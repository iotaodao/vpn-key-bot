# -*- coding: utf-8 -*-
import logging
from typing import List

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hcode, hbold

from config import ADMIN_IDS, MESSAGES, KEY_FORMAT
from database import UserDatabase

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь администратором"""
    return user_id in ADMIN_IDS

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")
    
    await message.reply(
        MESSAGES['welcome'],
        parse_mode=types.ParseMode.HTML
    )

async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    user_id = message.from_user.id
    
    if is_admin(user_id):
        help_text = MESSAGES['help'] + "\n\n" + MESSAGES['admin_help']
    else:
        help_text = MESSAGES['help']
    
    await message.reply(help_text, parse_mode=types.ParseMode.HTML)

async def cmd_key(message: types.Message, db: UserDatabase):
    """Обработчик команды /key для получения ключей доступа"""
    user = message.from_user
    user_id = user.id
    username = user.username
    
    logger.info(f"Запрос ключей от пользователя {user_id} ({username})")
    
    # Поиск пользователя в базе данных
    keys = db.get_user_keys(user_id, username)
    
    if not keys:
        # Проверяем, есть ли пользователь в базе, но без ключей
        user_data = db.find_user(user_id, username)
        if user_data:
            await message.reply(MESSAGES['no_keys'])
        else:
            await message.reply(MESSAGES['user_not_found'])
        return
    
    # Форматирование ответа с ключами
    if len(keys) == 1:
        response = KEY_FORMAT['single'].format(key=hcode(keys[0]))
    else:
        formatted_keys = "\n".join([
            f"{i+1}. `{key}`" for i, key in enumerate(keys)
        ])
        response = KEY_FORMAT['multiple'].format(keys=formatted_keys)
    
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN)
    logger.info(f"Ключи отправлены пользователю {user_id}")

# Административные команды

async def cmd_admin_stats(message: types.Message, db: UserDatabase):
    """Статистика для администраторов"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    stats = db.get_stats()
    
    stats_text = (
        f"📊 {hbold('Статистика базы данных')}\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"✅ С ключами: {stats['users_with_keys']}\n"
        f"❌ Без ключей: {stats['users_without_keys']}"
    )
    
    await message.reply(stats_text, parse_mode=types.ParseMode.HTML)

async def cmd_admin_users(message: types.Message, db: UserDatabase):
    """Список пользователей для администраторов"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    users = db.get_all_users()
    
    if not users:
        await message.reply("База данных пуста.")
        return
    
    users_text = f"{hbold('👥 Список пользователей:')}\n\n"
    
    for i, user in enumerate(users[:20], 1):  # Ограничиваем 20 пользователями
        user_id = user.get('telegram_id', 'N/A')
        username = user.get('telegram_username', 'N/A')
        keys_count = len(user.get('keys', []))
        
        users_text += f"{i}. ID: {hcode(user_id)} | @{username} | Ключей: {keys_count}\n"
    
    if len(users) > 20:
        users_text += f"\n... и еще {len(users) - 20} пользователей"
    
    await message.reply(users_text, parse_mode=types.ParseMode.HTML)

async def cmd_admin_reload(message: types.Message, db: UserDatabase):
    """Перезагрузка базы данных"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        db.reload()
        await message.reply("✅ База данных перезагружена успешно!")
        logger.info(f"База данных перезагружена администратором {message.from_user.id}")
    except Exception as e:
        await message.reply(f"❌ Ошибка при перезагрузке: {str(e)}")
        logger.error(f"Ошибка перезагрузки базы данных: {e}")

async def cmd_admin_help(message: types.Message):
    """Помощь для администраторов"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ У вас нет прав для выполнения этой команды.")
        return
    
    await message.reply(MESSAGES['admin_help'], parse_mode=types.ParseMode.HTML)

def register_handlers(dp: Dispatcher, db: UserDatabase):
    """Регистрация всех обработчиков"""
    
    # Основные команды
    dp.register_message_handler(cmd_start, Command('start'))
    dp.register_message_handler(cmd_help, Command('help'))
    dp.register_message_handler(
        lambda message: cmd_key(message, db), 
        Command('key')
    )
    
    # Административные команды
    dp.register_message_handler(
        lambda message: cmd_admin_stats(message, db),
        Command('stats')
    )
    dp.register_message_handler(
        lambda message: cmd_admin_users(message, db),
        Command('users')
    )
    dp.register_message_handler(
        lambda message: cmd_admin_reload(message, db),
        Command('reload')
    )
    dp.register_message_handler(cmd_admin_help, Command('admin_help'))
    
    logger.info("Обработчики зарегистрированы")
