#!/usr/bin/env python3
"""
Скрипт для настройки и инициализации базы данных Менеджера задач
"""

import os
import sys
from datetime import datetime, timedelta
import uuid

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from models.task import db, Task
from models.user import User

def create_tables():
    """Создание всех таблиц в базе данных"""
    print("Создание таблиц...")
    
    try:
        db.create_all()
        print("✅ Таблицы успешно созданы")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False

def create_sample_users():
    """Создание тестовых пользователей"""
    print("Создание тестовых пользователей...")
    
    try:
        # Проверка существования пользователей
        if User.query.first():
            print("ℹ️ Пользователи уже существуют, пропускаем создание")
            return True
        
        # Создание администратора
        admin_user = User(
            username='admin',
            email='admin@company.com',
            name='Администратор системы',
            department='IT отдел',
            role='admin',
            password_hash='admin123'  # В реальном проекте должен быть хеш
        )
        
        # Создание обычного пользователя
        regular_user = User(
            username='it_user',
            email='it_user@company.com',
            name='IT Сотрудник',
            department='IT отдел',
            role='user',
            password_hash='user123'  # В реальном проекте должен быть хеш
        )
        
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
        
        print("✅ Тестовые пользователи созданы")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании пользователей: {e}")
        db.session.rollback()
        return False

def create_sample_tasks():
    """Создание тестовых задач"""
    print("Создание тестовых задач...")
    
    try:
        # Проверка существования задач
        if Task.query.first():
            print("ℹ️ Задачи уже существуют, пропускаем создание")
            return True
        
        # Получение пользователей
        admin_user = User.query.filter_by(username='admin').first()
        regular_user = User.query.filter_by(username='it_user').first()
        
        if not admin_user or not regular_user:
            print("❌ Пользователи не найдены, сначала создайте пользователей")
            return False
        
        # Создание тестовых задач
        sample_tasks = [
            {
                'title': 'Не работает принтер в бухгалтерии',
                'description': 'Принтер HP LaserJet не печатает, выдает ошибку "Paper Jam"',
                'task_type': 'Сбой',
                'priority': 'Высокий',
                'requester_name': 'Иванова А.П.',
                'requester_department': 'Бухгалтерия',
                'deadline': datetime.now() + timedelta(days=1),
                'estimated_hours': 2.0,
                'assigned_to_id': regular_user.id
            },
            {
                'title': 'Разработка отчета по продажам',
                'description': 'Создать новый отчет в Excel с графиками и диаграммами',
                'task_type': 'Новая разработка',
                'priority': 'Средний',
                'requester_name': 'Петров В.С.',
                'requester_department': 'Отдел продаж',
                'deadline': datetime.now() + timedelta(days=3),
                'estimated_hours': 8.0,
                'assigned_to_id': admin_user.id
            },
            {
                'title': 'Консультация по Excel',
                'description': 'Объяснить как создать сводную таблицу в Excel 2019',
                'task_type': 'Консультация',
                'priority': 'Низкий',
                'requester_name': 'Сидорова Е.М.',
                'requester_department': 'Маркетинг',
                'deadline': datetime.now() + timedelta(days=5),
                'estimated_hours': 1.0
            },
            {
                'title': 'Обновление антивируса',
                'description': 'Обновить антивирусное ПО на всех компьютерах офиса',
                'task_type': 'Прочее',
                'priority': 'Средний',
                'requester_name': 'Козлов Д.А.',
                'requester_department': 'Безопасность',
                'deadline': datetime.now() + timedelta(days=2),
                'estimated_hours': 4.0,
                'assigned_to_id': regular_user.id
            }
        ]
        
        for task_data in sample_tasks:
            task = Task(
                task_number=generate_task_number(),
                **task_data
            )
            db.session.add(task)
        
        db.session.commit()
        print("✅ Тестовые задачи созданы")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании задач: {e}")
        db.session.rollback()
        return False

def generate_task_number():
    """Генерация номера задачи"""
    today = datetime.now().strftime('%Y%m%d')
    return f'TASK-{today}-0001'

def check_database_connection():
    """Проверка подключения к базе данных"""
    print("Проверка подключения к базе данных...")
    
    try:
        # Простой запрос для проверки подключения
        db.session.execute('SELECT 1')
        print("✅ Подключение к базе данных успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 50)
    print("Настройка базы данных Менеджера задач")
    print("=" * 50)
    
    # Проверка подключения
    if not check_database_connection():
        print("❌ Невозможно продолжить без подключения к базе данных")
        sys.exit(1)
    
    # Создание таблиц
    if not create_tables():
        print("❌ Невозможно продолжить без создания таблиц")
        sys.exit(1)
    
    # Создание пользователей
    if not create_sample_users():
        print("⚠️ Пользователи не созданы, но можно продолжить")
    
    # Создание задач
    if not create_sample_tasks():
        print("⚠️ Задачи не созданы, но можно продолжить")
    
    print("\n" + "=" * 50)
    print("✅ Настройка базы данных завершена успешно!")
    print("=" * 50)
    print("\nТеперь вы можете запустить приложение командой:")
    print("python app.py")
    print("\nИли использовать Flask CLI:")
    print("flask run")

if __name__ == '__main__':
    # Инициализация Flask приложения
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        main()
