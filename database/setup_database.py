#!/usr/bin/env python3
"""
Скрипт для настройки базы данных Менеджера задач
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.task import db, Task
from models.user import User

def setup_database():
    """Настройка базы данных и создание тестовых данных"""
    app = create_app()
    
    with app.app_context():
        # Создание таблиц
        print("Создание таблиц...")
        db.create_all()
        print("✓ Таблицы созданы")
        
        # Создание тестовых пользователей
        print("Создание тестовых пользователей...")
        
        # Администратор
        admin_user = User(
            username='admin',
            email='admin@company.com',
            name='Администратор Системы',
            department='IT отдел',
            role='admin',
            password_hash='admin_hash_123',  # В реальном проекте использовать хеширование
            is_active=True
        )
        
        # IT специалист
        it_user = User(
            username='it_user',
            email='it@company.com',
            name='Иванов Иван Иванович',
            department='IT отдел',
            role='user',
            password_hash='user_hash_123',
            is_active=True
        )
        
        db.session.add(admin_user)
        db.session.add(it_user)
        db.session.commit()
        print("✓ Тестовые пользователи созданы")
        
        # Создание тестовых задач
        print("Создание тестовых задач...")
        
        # Задача 1 - Сбой
        task1 = Task(
            task_number='TASK-001',
            title='Не работает принтер в бухгалтерии',
            description='Принтер HP LaserJet Pro M404n не печатает документы. При попытке печати выдает ошибку "Paper Jam". Проверил лоток - бумага загружена корректно.',
            task_type='Сбой',
            priority='Высокий',
            requester_name='Петрова Анна Сергеевна',
            requester_department='Бухгалтерия',
            requester_email='petrova@company.com',
            requester_phone='+7 (999) 123-45-67',
            status='В работе',
            deadline=datetime.utcnow() + timedelta(hours=4),
            estimated_hours=2.0,
            assigned_to_id=it_user.id,
            taken_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Задача 2 - Новая разработка
        task2 = Task(
            task_number='TASK-002',
            title='Создание отчета по продажам',
            description='Необходимо разработать автоматический отчет по продажам за месяц с возможностью экспорта в Excel. Отчет должен включать данные по регионам, менеджерам и продуктам.',
            task_type='Новая разработка',
            priority='Средний',
            requester_name='Сидоров Михаил Петрович',
            requester_department='Отдел продаж',
            requester_email='sidorov@company.com',
            requester_phone='+7 (999) 234-56-78',
            status='Неразобранная',
            deadline=datetime.utcnow() + timedelta(days=7),
            estimated_hours=16.0
        )
        
        # Задача 3 - Консультация
        task3 = Task(
            task_number='TASK-003',
            title='Настройка VPN для удаленной работы',
            description='Сотрудник переходит на удаленную работу и нуждается в настройке VPN-соединения. Необходимо предоставить инструкции по настройке и проверить доступ.',
            task_type='Консультация',
            priority='Низкий',
            requester_name='Козлова Елена Владимировна',
            requester_department='HR отдел',
            requester_email='kozlova@company.com',
            requester_phone='+7 (999) 345-67-89',
            status='Неразобранная',
            deadline=datetime.utcnow() + timedelta(days=3),
            estimated_hours=1.0
        )
        
        # Задача 4 - Завершенная
        task4 = Task(
            task_number='TASK-004',
            title='Обновление антивируса',
            description='Обновить антивирусное ПО на всех рабочих станциях до последней версии. Проверить совместимость с корпоративными приложениями.',
            task_type='Прочее',
            priority='Средний',
            requester_name='Васильев Дмитрий Александрович',
            requester_department='IT отдел',
            requester_email='vasiliev@company.com',
            requester_phone='+7 (999) 456-78-90',
            status='Готово',
            deadline=datetime.utcnow() - timedelta(days=1),
            estimated_hours=8.0,
            assigned_to_id=it_user.id,
            taken_at=datetime.utcnow() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(hours=12),
            completion_comment='Антивирус успешно обновлен на всех 25 рабочих станциях. Совместимость проверена, проблем не выявлено.'
        )
        
        db.session.add(task1)
        db.session.add(task2)
        db.session.add(task3)
        db.session.add(task4)
        db.session.commit()
        print("✓ Тестовые задачи созданы")
        
        print("\n🎉 База данных успешно настроена!")
        print(f"Создано пользователей: {User.query.count()}")
        print(f"Создано задач: {Task.query.count()}")
        print("\nДанные для входа:")
        print("Администратор: admin / admin_hash_123")
        print("IT пользователь: it_user / user_hash_123")

if __name__ == '__main__':
    setup_database()
