from datetime import datetime
from .database import db
import uuid

class User(db.Model):
    """Модель данных для пользователя системы"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, it_staff, user
    
    # Telegram username для уведомлений
    telegram_username = db.Column(db.String(50), nullable=True)
    
    # Пароль (в реальном проекте должен быть хеширован)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Статус пользователя
    is_active = db.Column(db.Boolean, default=True)
    
    # Временные метки
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}: {self.name}>'
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'role': self.role,
            'telegram_username': self.telegram_username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @property
    def is_admin(self):
        """Проверка, является ли пользователь администратором"""
        return self.role == 'admin'
    
    @property
    def is_it_staff(self):
        """Проверка, является ли пользователь IT сотрудником"""
        return self.role == 'it_staff'
    
    @property
    def is_user(self):
        """Проверка, является ли пользователь обычным пользователем"""
        return self.role == 'user'
    
    @property
    def can_manage_tasks(self):
        """Проверка, может ли пользователь управлять задачами"""
        return self.role in ['admin', 'it_staff']
    
    @property
    def can_view_analytics(self):
        """Проверка, может ли пользователь просматривать аналитику"""
        return self.role == 'admin'
    
    def update_last_login(self):
        """Обновление времени последнего входа"""
        self.last_login = datetime.utcnow()
