from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db
from models.user import User
from services.settings_service import SettingsService
from services.ldap_service import LDAPService
import uuid

class AuthService:
    """Сервис для аутентификации и авторизации пользователей"""
    
    def __init__(self):
        self.db = db
        self.settings_service = SettingsService()
        self.ldap_service = LDAPService()
    
    def register_user(self, username, email, password, name, department, role='user', telegram_username=None):
        """Регистрация нового пользователя"""
        # Проверка существования пользователя
        if User.query.filter_by(username=username).first():
            raise ValueError("Пользователь с таким именем уже существует")
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Пользователь с таким email уже существует")
        
        # Создание нового пользователя
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            name=name,
            department=department,
            role=role,
            telegram_username=telegram_username
        )
        
        self.db.session.add(user)
        self.db.session.commit()
        
        return user
    
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        # Сначала пробуем локальную аутентификацию
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            user.update_last_login()
            self.db.session.commit()
            return user
        
        # Если локальная аутентификация не удалась, пробуем LDAP
        ldap_settings = self.settings_service.get_ldap_settings()
        
        if ldap_settings['ldap_enabled'] == 'true':
            try:
                ldap_result = self.ldap_service.authenticate_user(
                    username=username,
                    password=password,
                    server_url=ldap_settings['ldap_server_url'],
                    port=int(ldap_settings['ldap_port']),
                    use_ssl=ldap_settings['ldap_use_ssl'] == 'true',
                    bind_dn=ldap_settings['ldap_bind_dn'],
                    bind_password=ldap_settings['ldap_bind_password'],
                    user_search_base=ldap_settings['ldap_user_search_base'],
                    user_search_filter=ldap_settings['ldap_user_search_filter'],
                    auth_method=ldap_settings['ldap_auth_method']
                )
                
                if ldap_result['success']:
                    user_info = ldap_result['user_info']
                    
                    # Ищем пользователя в локальной базе
                    user = User.query.filter_by(username=username).first()
                    
                    if not user and ldap_settings['ldap_auto_create_users'] == 'true':
                        # Автоматически создаем пользователя
                        user = self._create_user_from_ldap(user_info, ldap_settings)
                    elif user:
                        # Обновляем информацию о пользователе из LDAP
                        self._update_user_from_ldap(user, user_info)
                    
                    if user:
                        user.update_last_login()
                        self.db.session.commit()
                        return user
                        
            except Exception as e:
                # Логируем ошибку, но не прерываем процесс
                print(f"Ошибка LDAP аутентификации: {str(e)}")
        
        return None
    
    def _create_user_from_ldap(self, user_info, ldap_settings):
        """Создание пользователя из информации LDAP"""
        try:
            # Генерируем случайный пароль для локальной записи
            import secrets
            temp_password = secrets.token_urlsafe(16)
            
            user = User(
                username=user_info['username'],
                email=user_info['email'] or f"{user_info['username']}@company.local",
                password_hash=generate_password_hash(temp_password),
                name=user_info['cn'] or user_info['username'],
                department=user_info['department'] or 'Не указан',
                role=ldap_settings['ldap_default_role'],
                telegram_username=None
            )
            
            self.db.session.add(user)
            self.db.session.commit()
            
            return user
            
        except Exception as e:
            print(f"Ошибка создания пользователя из LDAP: {str(e)}")
            return None
    
    def _update_user_from_ldap(self, user, user_info):
        """Обновление информации о пользователе из LDAP"""
        try:
            if user_info.get('email') and user_info['email'] != user.email:
                user.email = user_info['email']
            
            if user_info.get('cn') and user_info['cn'] != user.name:
                user.name = user_info['cn']
            
            if user_info.get('department') and user_info['department'] != user.department:
                user.department = user_info['department']
            
            self.db.session.commit()
            
        except Exception as e:
            print(f"Ошибка обновления пользователя из LDAP: {str(e)}")
    
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """Получение пользователя по имени пользователя"""
        return User.query.filter_by(username=username).first()
    
    def update_user_role(self, user_id, new_role):
        """Обновление роли пользователя (только для администраторов)"""
        if new_role not in ['admin', 'it_staff', 'user']:
            raise ValueError("Недопустимая роль")
        
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        user.role = new_role
        self.db.session.commit()
        
        return user
    
    def update_user(self, user_id, username=None, email=None, name=None, department=None, role=None, telegram_username=None):
        """Обновление данных пользователя (только для администраторов)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Обновляем только переданные поля
        if username is not None:
            # Проверяем, что новое имя пользователя не занято другим пользователем
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user_id:
                raise ValueError("Пользователь с таким именем уже существует")
            user.username = username
        
        if email is not None:
            # Проверяем, что новый email не занят другим пользователем
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                raise ValueError("Пользователь с таким email уже существует")
            user.email = email
        
        if name is not None:
            user.name = name
        
        if department is not None:
            user.department = department
        
        if role is not None:
            if role not in ['admin', 'it_staff', 'user']:
                raise ValueError("Недопустимая роль")
            user.role = role
        
        if telegram_username is not None:
            user.telegram_username = telegram_username
        
        self.db.session.commit()
        return user
    
    def deactivate_user(self, user_id):
        """Деактивация пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        user.is_active = False
        self.db.session.commit()
        
        return user
    
    def get_all_users(self):
        """Получение всех пользователей (только для администраторов)"""
        return User.query.filter_by(is_active=True).all()
    
    def get_users_by_role(self, role):
        """Получение пользователей по роли"""
        return User.query.filter_by(role=role, is_active=True).all()
    
    def create_default_users(self):
        """Создание пользователей по умолчанию для демонстрации"""
        # Проверяем, есть ли уже пользователи
        if User.query.first():
            return
        
        # Создаем администратора
        admin = User(
            username='admin',
            email='admin@company.com',
            password_hash=generate_password_hash('admin123'),
            name='Администратор Системы',
            department='IT',
            role='admin'
        )
        
        # Создаем IT сотрудника
        it_staff = User(
            username='it_staff',
            email='it@company.com',
            password_hash=generate_password_hash('it123'),
            name='IT Сотрудник',
            department='IT',
            role='it_staff'
        )
        
        # Создаем обычного пользователя
        user = User(
            username='user',
            email='user@company.com',
            password_hash=generate_password_hash('user123'),
            name='Обычный Пользователь',
            department='Продажи',
            role='user'
        )
        
        self.db.session.add_all([admin, it_staff, user])
        self.db.session.commit()
