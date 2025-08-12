from models.database import db
from models.settings import SystemSettings
from models.user import User
import uuid

class SettingsService:
    """Сервис для работы с настройками системы"""
    
    def __init__(self):
        self.db = db
    
    def get_telegram_settings(self):
        """Получение настроек Telegram"""
        bot_token = SystemSettings.get_setting('telegram_bot_token')
        chat_id = SystemSettings.get_setting('telegram_chat_id')
        
        return {
            'bot_token': bot_token,
            'chat_id': chat_id
        }
    
    def save_telegram_settings(self, bot_token, chat_id, user_id=None):
        """Сохранение настроек Telegram"""
        SystemSettings.set_setting(
            'telegram_bot_token', 
            bot_token, 
            'Токен Telegram бота для уведомлений',
            user_id
        )
        
        SystemSettings.set_setting(
            'telegram_chat_id', 
            chat_id, 
            'ID чата/группы для уведомлений',
            user_id
        )
        
        return True
    
    def get_all_settings(self):
        """Получение всех настроек системы"""
        settings = SystemSettings.query.all()
        return [setting.to_dict() for setting in settings]
    
    def get_setting(self, key, default=None):
        """Получение значения настройки по ключу"""
        return SystemSettings.get_setting(key, default)
    
    def set_setting(self, key, value, description=None, user_id=None):
        """Установка значения настройки"""
        return SystemSettings.set_setting(key, value, description, user_id)
    
    def create_default_settings(self):
        """Создание настроек по умолчанию"""
        default_settings = [
            ('telegram_bot_token', '', 'Токен Telegram бота для уведомлений'),
            ('telegram_chat_id', '', 'ID чата/группы для уведомлений'),
            ('system_name', 'Менеджер задач', 'Название системы'),
            ('company_name', 'Компания', 'Название компании'),
            ('notification_email', '', 'Email для системных уведомлений'),
            ('max_file_size', '10485760', 'Максимальный размер файла в байтах (10MB)'),
            ('auto_archive_days', '30', 'Автоматическое архивирование задач через N дней'),
            ('backup_enabled', 'true', 'Включить автоматическое резервное копирование'),
            ('backup_interval_hours', '24', 'Интервал резервного копирования в часах')
        ]
        
        for key, value, description in default_settings:
            if not SystemSettings.query.filter_by(key=key).first():
                SystemSettings.set_setting(key, value, description)
        
        return True
