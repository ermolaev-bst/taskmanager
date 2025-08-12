from datetime import datetime
from .database import db

class SystemSettings(db.Model):
    """Модель для хранения настроек системы"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.String(36), primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value}>'
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            'id': str(self.id),
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Получение значения настройки по ключу"""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set_setting(cls, key, value, description=None, user_id=None):
        """Установка значения настройки"""
        setting = cls.query.filter_by(key=key).first()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            setting.updated_by = user_id
        else:
            import uuid
            setting = cls(
                id=str(uuid.uuid4()),
                key=key,
                value=value,
                description=description,
                updated_by=user_id
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
