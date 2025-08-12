from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, asc
from models.task import Task, db
from models.user import User
import uuid

class TaskService:
    """Сервис для работы с задачами"""
    
    def __init__(self):
        self.db = db
    
    def create_task_from_form(self, form_data):
        """Создание задачи из данных веб-формы или Google Forms"""
        try:
            # Генерация уникального номера задачи
            task_number = self._generate_task_number()
            
            print(f"Создание задачи с номером: {task_number}")
            print(f"Данные формы: {form_data}")
            
            # Создание новой задачи
            task = Task(
                task_number=task_number,
                title=form_data.get('title', 'Без названия'),
                description=form_data.get('description', ''),
                task_type=form_data.get('task_type', 'Прочее'),
                priority=form_data.get('priority', 'Средний'),
                requester_name=form_data.get('requester_name', 'Не указано'),
                requester_department=form_data.get('requester_department', 'Не указано'),
                requester_email=form_data.get('requester_email'),
                requester_phone=form_data.get('requester_phone'),
                deadline=self._parse_deadline(form_data.get('deadline')),
                estimated_hours=form_data.get('estimated_hours'),
                screenshot_url=form_data.get('screenshot_url')
            )
            
            print(f"Объект задачи создан: {task}")
            
            self.db.session.add(task)
            self.db.session.commit()
            
            print(f"Задача успешно сохранена в базе данных с ID: {task.id}")
            
            return task
            
        except Exception as e:
            print(f"Ошибка при создании задачи: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def get_active_tasks(self):
        """Получение активных задач с сортировкой по приоритету"""
        tasks = Task.query.filter(
            Task.status.notin_(['Готово', 'Отменено'])
        ).order_by(
            # 1. По типу задачи (сбои сверху)
            desc(Task.task_type == 'Сбой'),
            # 2. По статусу (неразобранные выше тех, что в работе)
            asc(Task.status == 'Неразобранная'),
            desc(Task.status == 'В работе'),
            # 3. По приоритету (высокий приоритет выше низкого)
            desc(Task.priority == 'Высокий'),
            desc(Task.priority == 'Средний'),
            # 4. По дедлайну
            asc(Task.deadline)
        ).all()
        
        return tasks
    
    def get_completed_tasks(self):
        """Получение выполненных и отмененных задач"""
        tasks = Task.query.filter(
            Task.status.in_(['Готово', 'Отменено'])
        ).order_by(desc(Task.completed_at)).all()
        
        return tasks
    
    def get_tasks_filtered(self, status=None, task_type=None, priority=None):
        """Получение задач с фильтрацией"""
        query = Task.query
        
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if priority:
            query = query.filter(Task.priority == priority)
        
        return query.order_by(desc(Task.created_at)).all()
    
    def get_task_by_id(self, task_id):
        """Получение задачи по ID"""
        try:
            return Task.query.get(task_id)
        except:
            return None
    
    def update_task(self, task_id, update_data):
        """Обновление задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        
        # Обновление полей
        for field, value in update_data.items():
            if hasattr(task, field):
                if field == 'status':
                    # Использование специального метода для обновления статуса
                    task.update_status(value, update_data.get('assigned_to_id'))
                elif field == 'deadline' and value:
                    task.deadline = self._parse_deadline(value)
                else:
                    setattr(task, field, value)
        
        task.updated_at = datetime.utcnow()
        self.db.session.commit()
        
        return task
    
    def assign_task(self, task_id, user_id):
        """Назначение задачи пользователю"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        task.assigned_to_id = user_id
        task.updated_at = datetime.utcnow()
        
        self.db.session.commit()
        return task
    
    def get_overdue_tasks(self):
        """Получение просроченных задач"""
        return Task.query.filter(
            and_(
                Task.deadline < datetime.utcnow(),
                Task.status.notin_(['Готово', 'Отменено'])
            )
        ).all()
    
    def get_tasks_by_user(self, user_id):
        """Получение задач, назначенных пользователю"""
        return Task.query.filter(
            Task.assigned_to_id == user_id
        ).order_by(desc(Task.created_at)).all()
    
    def get_tasks_by_requester(self, user_id):
        """Получение задач, созданных пользователем"""
        # Находим пользователя по ID
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Ищем задачи по email пользователя
        return Task.query.filter(
            Task.requester_email == user.email
        ).order_by(desc(Task.created_at)).all()
    
    def get_completed_tasks_by_user(self, user_id):
        """Получение выполненных задач, которые обрабатывал пользователь"""
        return Task.query.filter(
            and_(
                Task.assigned_to_id == user_id,
                Task.status.in_(['Готово', 'Отменено'])
            )
        ).order_by(desc(Task.completed_at)).all()
    
    def get_unassigned_tasks(self):
        """Получение неразобранных задач"""
        return Task.query.filter(
            Task.status == 'Неразобранная'
        ).order_by(desc(Task.created_at)).all()
    
    def _generate_task_number(self):
        """Генерация уникального номера задачи"""
        # Формат: TASK-YYYYMMDD-XXXX
        today = datetime.now().strftime('%Y%m%d')
        
        # Поиск последнего номера за сегодня
        last_task = Task.query.filter(
            Task.task_number.like(f'TASK-{today}-%')
        ).order_by(desc(Task.task_number)).first()
        
        if last_task:
            # Извлечение номера и увеличение на 1
            last_number = int(last_task.task_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'TASK-{today}-{new_number:04d}'
    
    def _parse_deadline(self, deadline_str):
        """Парсинг дедлайна из строки"""
        if not deadline_str:
            return None
        
        try:
            # Попытка парсинга различных форматов даты
            formats = [
                '%Y-%m-%d',
                '%d.%m.%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M'  # Формат datetime-local
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(deadline_str, fmt)
                except ValueError:
                    continue
            
            # Если не удалось распарсить, возвращаем None
            return None
            
        except:
            return None
