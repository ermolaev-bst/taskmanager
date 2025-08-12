from functools import wraps
from flask import session, redirect, url_for, flash, abort
from models.user import User

def login_required(f):
    """Декоратор для проверки аутентификации пользователя"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо войти в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    """Декоратор для проверки роли пользователя"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Необходимо войти в систему', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                session.pop('user_id', None)
                flash('Сессия истекла. Войдите снова.', 'warning')
                return redirect(url_for('login'))
            
            if user.role not in required_roles:
                flash('Недостаточно прав для доступа к этой странице', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    return role_required(['admin'])(f)

def it_staff_required(f):
    """Декоратор для проверки прав IT сотрудника"""
    return role_required(['admin', 'it_staff'])(f)

def user_or_higher_required(f):
    """Декоратор для проверки прав пользователя или выше"""
    return role_required(['admin', 'it_staff', 'user'])(f)

def get_current_user():
    """Получение текущего пользователя из сессии"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def can_manage_tasks(user):
    """Проверка, может ли пользователь управлять задачами"""
    return user and user.can_manage_tasks

def can_view_analytics(user):
    """Проверка, может ли пользователь просматривать аналитику"""
    return user and user.can_view_analytics
