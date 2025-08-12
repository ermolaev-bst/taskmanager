import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовая конфигурация приложения"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/taskmanager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    
    # Настройки Google Forms
    GOOGLE_FORMS_SECRET_TOKEN = os.environ.get('GOOGLE_FORMS_SECRET_TOKEN')
    
    # Настройки приложения
    TASKS_PER_PAGE = 20
    NOTIFICATION_INTERVAL_HOURS = 2
    
    # Типы задач
    TASK_TYPES = [
        'Сбой',
        'Новая разработка', 
        'Консультация',
        'Прочее'
    ]
    
    # Статусы задач
    TASK_STATUSES = [
        'Неразобранная',
        'В работе',
        'В очереди',
        'Ожидает',
        'Готово',
        'Отменено'
    ]
    
    # Приоритеты задач
    TASK_PRIORITIES = [
        'Высокий',
        'Средний',
        'Низкий'
    ]

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///taskmanager_dev.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
