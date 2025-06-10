# -*- coding: utf-8 -*-
import json
import logging
import os
from typing import Optional, List, Union, Dict, Any

from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class UserDatabase:
    """Класс для работы с базой данных пользователей в формате JSON"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.data: Dict[str, Any] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Загрузка данных из JSON файла"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"База данных загружена: {len(self.data)} пользователей")
            else:
                logger.warning(f"Файл базы данных не найден: {self.db_path}")
                self.data = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки базы данных: {e}")
            self.data = {}
    
    def save_data(self) -> None:
        """Сохранение данных в JSON файл"""
        try:
            # Создаем директорию если её нет
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info("База данных сохранена")
        except Exception as e:
            logger.error(f"Ошибка сохранения базы данных: {e}")
    
    def find_user(self, user_id: int, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Поиск пользователя по ID или username
        
        Args:
            user_id: Telegram ID пользователя
            username: Telegram username пользователя (без @)
            
        Returns:
            Словарь с данными пользователя или None если не найден
        """
        # Поиск по точному совпадению user_id
        for key, user_data in self.data.items():
            if user_data.get('telegram_id') == user_id:
                return {'key': key, **user_data}
        
        # Поиск по username если указан
        if username:
            username_clean = username.lower().replace('@', '')
            for key, user_data in self.data.items():
                db_username = user_data.get('telegram_username', '').lower().replace('@', '')
                if db_username == username_clean:
                    return {'key': key, **user_data}
        
        return None
    
    def get_user_keys(self, user_id: int, username: Optional[str] = None) -> List[str]:
        """
        Получение ключей пользователя
        
        Args:
            user_id: Telegram ID пользователя
            username: Telegram username пользователя
            
        Returns:
            Список ключей доступа
        """
        user_data = self.find_user(user_id, username)
        if not user_data:
            return []
        
        keys = user_data.get('keys', [])
        
        # Поддержка как списка ключей, так и одного ключа
        if isinstance(keys, str):
            return [keys] if keys else []
        elif isinstance(keys, list):
            return [key for key in keys if key]
        else:
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение списка всех пользователей"""
        return [
            {'key': key, **user_data} 
            for key, user_data in self.data.items()
        ]
    
    def get_stats(self) -> Dict[str, int]:
        """Получение статистики базы данных"""
        total_users = len(self.data)
        users_with_keys = sum(
            1 for user_data in self.data.values()
            if user_data.get('keys')
        )
        users_without_keys = total_users - users_with_keys
        
        return {
            'total_users': total_users,
            'users_with_keys': users_with_keys,
            'users_without_keys': users_without_keys
        }
    
    def reload(self) -> None:
        """Перезагрузка данных из файла"""
        self.load_data()
