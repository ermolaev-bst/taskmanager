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
    
    def get_ldap_settings(self):
        """Получение настроек LDAP/Active Directory"""
        return {
            'ldap_enabled': SystemSettings.get_setting('ldap_enabled', 'false'),
            'ldap_server_url': SystemSettings.get_setting('ldap_server_url', ''),
            'ldap_port': SystemSettings.get_setting('ldap_port', '389'),
            'ldap_use_ssl': SystemSettings.get_setting('ldap_use_ssl', 'false'),
            'ldap_bind_dn': SystemSettings.get_setting('ldap_bind_dn', ''),
            'ldap_bind_password': SystemSettings.get_setting('ldap_bind_password', ''),
            'ldap_auth_method': SystemSettings.get_setting('ldap_auth_method', 'SIMPLE'),
            'ldap_user_search_base': SystemSettings.get_setting('ldap_user_search_base', ''),
            'ldap_user_search_filter': SystemSettings.get_setting('ldap_user_search_filter', '(sAMAccountName={username})'),
            'ldap_auto_create_users': SystemSettings.get_setting('ldap_auto_create_users', 'false'),
            'ldap_default_role': SystemSettings.get_setting('ldap_default_role', 'user'),
            'ldap_sync_groups': SystemSettings.get_setting('ldap_sync_groups', 'false')
        }
    
    def save_ldap_settings(self, ldap_enabled, ldap_server_url, ldap_port, ldap_use_ssl,
                          ldap_bind_dn, ldap_bind_password, ldap_auth_method,
                          ldap_user_search_base, ldap_user_search_filter,
                          ldap_auto_create_users, ldap_default_role, ldap_sync_groups, user_id=None):
        """Сохранение настроек LDAP/Active Directory"""
        settings = [
            ('ldap_enabled', str(ldap_enabled).lower(), 'Включить интеграцию с LDAP/Active Directory'),
            ('ldap_server_url', ldap_server_url, 'URL или IP адрес LDAP сервера'),
            ('ldap_port', str(ldap_port), 'Порт LDAP сервера'),
            ('ldap_use_ssl', str(ldap_use_ssl).lower(), 'Использовать SSL/TLS для подключения'),
            ('ldap_bind_dn', ldap_bind_dn, 'DN пользователя для подключения к LDAP'),
            ('ldap_bind_password', ldap_bind_password, 'Пароль пользователя LDAP'),
            ('ldap_auth_method', ldap_auth_method, 'Метод аутентификации (SIMPLE, NTLM, ANONYMOUS)'),
            ('ldap_user_search_base', ldap_user_search_base, 'База поиска пользователей в LDAP'),
            ('ldap_user_search_filter', ldap_user_search_filter, 'Фильтр поиска пользователей'),
            ('ldap_auto_create_users', str(ldap_auto_create_users).lower(), 'Автоматически создавать пользователей при первом входе'),
            ('ldap_default_role', ldap_default_role, 'Роль по умолчанию для новых пользователей LDAP'),
            ('ldap_sync_groups', str(ldap_sync_groups).lower(), 'Синхронизировать группы пользователей из LDAP')
        ]
        
        for key, value, description in settings:
            SystemSettings.set_setting(key, value, description, user_id)
        
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
            ('backup_interval_hours', '24', 'Интервал резервного копирования в часах'),
            # LDAP настройки
            ('ldap_enabled', 'false', 'Включить интеграцию с LDAP/Active Directory'),
            ('ldap_server_url', '', 'URL или IP адрес LDAP сервера'),
            ('ldap_port', '389', 'Порт LDAP сервера'),
            ('ldap_use_ssl', 'false', 'Использовать SSL/TLS для подключения'),
            ('ldap_bind_dn', '', 'DN пользователя для подключения к LDAP'),
            ('ldap_bind_password', '', 'Пароль пользователя LDAP'),
            ('ldap_auth_method', 'SIMPLE', 'Метод аутентификации (SIMPLE, NTLM, ANONYMOUS)'),
            ('ldap_user_search_base', '', 'База поиска пользователей в LDAP'),
            ('ldap_user_search_filter', '(sAMAccountName={username})', 'Фильтр поиска пользователей'),
            ('ldap_auto_create_users', 'false', 'Автоматически создавать пользователей при первом входе'),
            ('ldap_default_role', 'user', 'Роль по умолчанию для новых пользователей LDAP'),
            ('ldap_sync_groups', 'false', 'Синхронизировать группы пользователей из LDAP')
        ]
        
        for key, value, description in default_settings:
            if not SystemSettings.query.filter_by(key=key).first():
                SystemSettings.set_setting(key, value, description)
        
        return True
