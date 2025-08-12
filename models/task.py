from datetime import datetime
from .database import db
import uuid

class Task(db.Model):
    """Модель данных для задачи"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Основная информация
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50), nullable=False)  # Сбой, Новая разработка, Консультация, Прочее
    status = db.Column(db.String(50), nullable=False, default='Неразобранная')
    priority = db.Column(db.String(20), nullable=False, default='Средний')
    
    # Данные о постановщике
    requester_name = db.Column(db.String(100), nullable=False)
    requester_department = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(120))
    requester_phone = db.Column(db.String(20))
    
    # Временные метки
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    taken_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    
    # Прочие поля
    estimated_hours = db.Column(db.Float)
    screenshot_url = db.Column(db.String(500))
    completion_comment = db.Column(db.Text)
    
    # Связи
    assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    assigned_to = db.relationship('User', backref='assigned_tasks')
    
    # Метаданные
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.task_number}: {self.title}>'
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            'id': str(self.id),
            'task_number': self.task_number,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'status': self.status,
            'priority': self.priority,
            'requester_name': self.requester_name,
            'requester_department': self.requester_department,
            'requester_email': self.requester_email,
            'requester_phone': self.requester_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'taken_at': self.taken_at.isoformat() if self.taken_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_hours': self.estimated_hours,
            'screenshot_url': self.screenshot_url,
            'completion_comment': self.completion_comment,
            'assigned_to_id': str(self.assigned_to_id) if self.assigned_to_id else None,
            'assigned_to_name': self.assigned_to.name if self.assigned_to else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_status(self, new_status, user_id=None):
        """Обновление статуса задачи с автоматической фиксацией времени"""
        old_status = self.status
        self.status = new_status
        
        # Автоматическая фиксация времени взятия в работу
        if new_status == 'В работе' and old_status != 'В работе':
            self.taken_at = datetime.utcnow()
            if user_id:
                self.assigned_to_id = user_id
        
        # Автоматическая фиксация времени выполнения
        if new_status == 'Готово' and old_status != 'Готово':
            self.completed_at = datetime.utcnow()
        
        self.updated_at = datetime.utcnow()
    
    @property
    def is_active(self):
        """Проверка, является ли задача активной"""
        return self.status not in ['Готово', 'Отменено']
    
    @property
    def is_overdue(self):
        """Проверка, просрочена ли задача"""
        if not self.deadline or self.status in ['Готово', 'Отменено']:
            return False
        return datetime.utcnow() > self.deadline
    
    @property
    def time_to_take(self):
        """Время от создания до взятия в работу (в минутах)"""
        if not self.taken_at or not self.created_at:
            return None
        delta = self.taken_at - self.created_at
        return int(delta.total_seconds() / 60)
    
    @property
    def time_to_complete(self):
        """Время от взятия в работу до выполнения (в часах)"""
        if not self.completed_at or not self.taken_at:
            return None
        delta = self.completed_at - self.taken_at
        return round(delta.total_seconds() / 3600, 2)
