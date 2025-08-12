from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, make_response
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
import uuid

from config import config
from models.database import db
from models.task import Task
from models.user import User
from services.telegram_service import TelegramService
from services.task_service import TaskService
from services.analytics_service import AnalyticsService
from services.auth_service import AuthService
from services.settings_service import SettingsService
from utils.decorators import login_required, admin_required, it_staff_required, user_or_higher_required, get_current_user

def create_app(config_name='default'):
    """Фабрика создания Flask приложения"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Секретный ключ для сессий
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Инициализация сервисов
    telegram_service = TelegramService()
    task_service = TaskService()
    analytics_service = AnalyticsService()
    auth_service = AuthService()
    settings_service = SettingsService()
    
    # Главная страница - рабочий стол с активными задачами
    @app.route('/')
    @user_or_higher_required
    def dashboard():
        """Основной рабочий стол с активными задачами"""
        current_user = get_current_user()
        if current_user.is_admin or current_user.is_it_staff:
            # Администраторы и IT сотрудники видят все задачи
            tasks = task_service.get_active_tasks()
        else:
            # Обычные пользователи видят только свои задачи
            tasks = task_service.get_tasks_by_requester(str(current_user.id))
        return render_template('dashboard.html', tasks=tasks, current_user=current_user)
    
    # Архив выполненных задач
    @app.route('/archive')
    @it_staff_required
    def archive():
        """Архив выполненных и отмененных задач"""
        current_user = get_current_user()
        if current_user.is_admin:
            # Администраторы видят все задачи
            tasks = task_service.get_completed_tasks()
        else:
            # IT сотрудники видят только задачи, которые они обрабатывали
            tasks = task_service.get_completed_tasks_by_user(str(current_user.id))
        return render_template('archive.html', tasks=tasks, current_user=current_user)
    
    # Страница аналитики
    @app.route('/analytics')
    @admin_required
    def analytics():
        """Страница аналитики эффективности"""
        stats = analytics_service.get_performance_stats()
        return render_template('analytics.html', stats=stats, current_user=get_current_user())
    
    # Просмотр и редактирование задачи
    @app.route('/task/<task_id>')
    @user_or_higher_required
    def view_task(task_id):
        """Просмотр и редактирование задачи"""
        current_user = get_current_user()
        task = task_service.get_task_by_id(task_id)
        if not task:
            return redirect(url_for('dashboard'))
        
        # Проверка прав доступа
        if current_user.is_user and task.requester_email != current_user.email:
            flash('У вас нет прав для просмотра этой задачи', 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template('task_detail.html', task=task, current_user=current_user)
    
    # Аутентификация
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Вход в систему"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = auth_service.authenticate_user(username, password)
            if user:
                session['user_id'] = str(user.id)
                flash(f'Добро пожаловать, {user.name}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Выход из системы"""
        session.pop('user_id', None)
        flash('Вы успешно вышли из системы', 'info')
        return redirect(url_for('login'))
    
    # Веб-форма создания заявок
    @app.route('/create-task', methods=['GET'])
    @user_or_higher_required
    def create_task_form():
        """Отображение веб-формы для создания заявок"""
        return render_template('create_task.html')
    
    # API для создания задач из веб-формы
    @app.route('/api/tasks', methods=['POST'])
    @user_or_higher_required
    def create_task():
        """API для создания новой задачи из веб-формы"""
        try:
            # Получение данных из формы
            data = {
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'task_type': request.form.get('task_type'),
                'priority': request.form.get('priority'),
                'requester_name': request.form.get('requester_name'),
                'requester_department': request.form.get('requester_department'),
                'requester_email': request.form.get('requester_email'),
                'requester_phone': request.form.get('requester_phone'),
                'deadline': request.form.get('deadline'),
                'estimated_hours': request.form.get('estimated_hours'),
                'screenshot_url': request.form.get('screenshot_url')
            }
            
            # Обработка пустых значений
            if data['estimated_hours'] == '':
                data['estimated_hours'] = None
            elif data['estimated_hours']:
                try:
                    data['estimated_hours'] = float(data['estimated_hours'])
                except ValueError:
                    data['estimated_hours'] = None
            
            if data['deadline'] == '':
                data['deadline'] = None
                
            if data['requester_email'] == '':
                data['requester_email'] = None
                
            if data['requester_phone'] == '':
                data['requester_phone'] = None
                
            if data['screenshot_url'] == '':
                data['screenshot_url'] = None
            
            # Обработка загруженного файла
            if 'screenshot' in request.files:
                file = request.files['screenshot']
                if file and file.filename:
                    # Здесь можно добавить логику сохранения файла
                    # Пока просто сохраняем имя файла
                    data['screenshot_url'] = f"uploaded_file_{file.filename}"
            
            # Создание новой задачи
            task = task_service.create_task_from_form(data)
            
            # Отправка уведомления в Telegram (не блокируем создание задачи при ошибке)
            try:
                telegram_service.send_new_task_notification(task)
            except Exception as telegram_error:
                print(f"Ошибка отправки уведомления в Telegram: {telegram_error}")
                # Продолжаем выполнение, так как задача уже создана
            
            return jsonify({
                'success': True,
                'message': f'Заявка №{task.task_number} успешно создана!',
                'task_id': str(task.id),
                'task_number': task.task_number
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Ошибка при создании заявки: {str(e)}'
            }), 400
    
    # API для создания задач из Google Forms (оставляем для обратной совместимости)
    @app.route('/api/tasks/google-forms', methods=['POST'])
    def create_task_google_forms():
        """API для создания новой задачи из Google Forms (обратная совместимость)"""
        # Проверка секретного токена
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token != f"Bearer {app.config['GOOGLE_FORMS_SECRET_TOKEN']}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            data = request.get_json()
            
            # Создание новой задачи
            task = task_service.create_task_from_form(data)
            
            # Отправка уведомления в Telegram (не блокируем создание задачи при ошибке)
            try:
                telegram_service.send_new_task_notification(task)
            except Exception as telegram_error:
                print(f"Ошибка отправки уведомления в Telegram: {telegram_error}")
                # Продолжаем выполнение, так как задача уже создана
            
            return jsonify({
                'success': True,
                'task_id': str(task.id),
                'task_number': task.task_number
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    # API для получения списка задач
    @app.route('/api/tasks', methods=['GET'])
    @user_or_higher_required
    def get_tasks():
        """API для получения списка задач с фильтрацией"""
        current_user = get_current_user()
        status = request.args.get('status')
        task_type = request.args.get('type')
        priority = request.args.get('priority')
        
        if current_user.is_admin or current_user.is_it_staff:
            # Администраторы и IT сотрудники видят все задачи
            tasks = task_service.get_tasks_filtered(
                status=status,
                task_type=task_type,
                priority=priority
            )
        else:
            # Обычные пользователи видят только свои задачи
            tasks = task_service.get_tasks_by_requester(str(current_user.id))
        
        return jsonify([task.to_dict() for task in tasks])
    
    # API для обновления задачи
    @app.route('/api/tasks/<task_id>', methods=['PUT'])
    @it_staff_required
    def update_task(task_id):
        """API для обновления задачи"""
        try:
            data = request.get_json()
            task = task_service.update_task(task_id, data)
            
            # Отправка уведомления об изменении статуса (не блокируем обновление при ошибке)
            if 'status' in data:
                try:
                    telegram_service.send_status_change_notification(task)
                except Exception as telegram_error:
                    print(f"Ошибка отправки уведомления в Telegram: {telegram_error}")
                    # Продолжаем выполнение, так как задача уже обновлена
            
            return jsonify(task.to_dict())
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    # Управление пользователями (только для администраторов)
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """Страница управления пользователями"""
        users = auth_service.get_all_users()
        return render_template('admin_users.html', users=users)
    
    # Настройки системы (только для администраторов)
    @app.route('/admin/settings')
    @admin_required
    def admin_settings():
        """Страница настроек системы"""
        users = auth_service.get_all_users()
        telegram_settings = settings_service.get_telegram_settings()
        ldap_settings = settings_service.get_ldap_settings()
        
        # Отключаем кэширование для этой страницы
        response = make_response(render_template('admin_settings.html', 
                                              users=users, 
                                              telegram_settings=telegram_settings,
                                              ldap_settings=ldap_settings))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/admin/settings-v2')
    @admin_required
    def admin_settings_v2():
        """Тестовая страница настроек системы V2"""
        users = auth_service.get_all_users()
        telegram_settings = settings_service.get_telegram_settings()
        
        # Отключаем кэширование для этой страницы
        response = make_response(render_template('admin_settings_v2.html', users=users, telegram_settings=telegram_settings))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # API для управления пользователями
    @app.route('/api/users', methods=['POST'])
    @admin_required
    def create_user():
        """API для создания нового пользователя"""
        try:
            data = request.get_json()
            user = auth_service.register_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                name=data['name'],
                department=data['department'],
                role=data['role'],
                telegram_username=data.get('telegram_username')
            )
            return jsonify({
                'success': True,
                'message': f'Пользователь {user.username} успешно создан',
                'user_id': str(user.id)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/users/<user_id>/role', methods=['PUT'])
    @admin_required
    def update_user_role(user_id):
        """API для изменения роли пользователя"""
        try:
            data = request.get_json()
            user = auth_service.update_user_role(user_id, data['role'])
            return jsonify({
                'success': True,
                'message': f'Роль пользователя {user.username} изменена на {data["role"]}'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/users/<user_id>', methods=['PUT'])
    @admin_required
    def update_user(user_id):
        """API для обновления данных пользователя"""
        try:
            data = request.get_json()
            
            # Обновляем пользователя
            user = auth_service.update_user(
                user_id=user_id,
                username=data.get('username'),
                email=data.get('email'),
                name=data.get('name'),
                department=data.get('department'),
                role=data.get('role'),
                telegram_username=data.get('telegram_username')
            )
            
            return jsonify({
                'success': True,
                'message': f'Пользователь {user.username} успешно обновлен'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/users/<user_id>/toggle-status', methods=['PUT'])
    @admin_required
    def toggle_user_status(user_id):
        """API для переключения статуса пользователя"""
        try:
            user = auth_service.deactivate_user(user_id)
            return jsonify({
                'success': True,
                'message': f'Статус пользователя {user.username} изменен'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400

    @app.route('/api/users/<user_id>', methods=['GET'])
    @admin_required
    def get_user(user_id):
        """API для получения данных пользователя по ID"""
        try:
            user = auth_service.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Пользователь не найден'
                }), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'department': user.department,
                    'role': user.role,
                    'is_active': user.is_active
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    # API для получения аналитики
    @app.route('/api/analytics', methods=['GET'])
    @admin_required
    def get_analytics():
        """API для получения аналитических данных"""
        stats = analytics_service.get_performance_stats()
        return jsonify(stats)
    
    # API для настроек Telegram
    @app.route('/api/settings/telegram', methods=['GET'])
    @admin_required
    def get_telegram_settings():
        """API для получения настроек Telegram"""
        try:
            settings = settings_service.get_telegram_settings()
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/telegram', methods=['POST'])
    @admin_required
    def save_telegram_settings():
        """API для сохранения настроек Telegram"""
        try:
            data = request.get_json()
            bot_token = data.get('bot_token', '')
            chat_id = data.get('chat_id', '')
            
            # Сохраняем настройки
            settings_service.save_telegram_settings(bot_token, chat_id, str(get_current_user().id))
            
            # Перезагружаем настройки в TelegramService
            telegram_service.reload_settings()
            
            return jsonify({
                'success': True,
                'message': 'Настройки Telegram успешно сохранены'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/telegram/status', methods=['GET'])
    @admin_required
    def get_telegram_status():
        """API для получения статуса подключения к Telegram"""
        try:
            settings = settings_service.get_telegram_settings()
            
            if not settings['bot_token'] or not settings['chat_id']:
                return jsonify({
                    'success': False,
                    'message': 'Telegram не настроен'
                })
            
            # Тестируем подключение
            success, message, bot_info, chat_info = telegram_service.test_connection()
            
            return jsonify({
                'success': success,
                'message': message,
                'bot_info': bot_info,
                'chat_info': chat_info
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/telegram/test', methods=['GET'])
    @admin_required
    def test_telegram_connection():
        """API для тестирования подключения к Telegram"""
        try:
            success, message, bot_info, chat_info = telegram_service.test_connection()
            
            return jsonify({
                'success': success,
                'message': message,
                'bot_info': bot_info,
                'chat_info': chat_info
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    # LDAP API endpoints
    @app.route('/api/settings/ldap', methods=['GET'])
    @admin_required
    def get_ldap_settings():
        """API для получения настроек LDAP"""
        try:
            ldap_settings = settings_service.get_ldap_settings()
            return jsonify({
                'success': True,
                'settings': ldap_settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/ldap', methods=['POST'])
    @admin_required
    def save_ldap_settings():
        """API для сохранения настроек LDAP"""
        try:
            data = request.get_json()
            
            # Валидация данных
            required_fields = ['ldap_enabled', 'ldap_server_url', 'ldap_port', 'ldap_use_ssl',
                             'ldap_bind_dn', 'ldap_bind_password', 'ldap_auth_method',
                             'ldap_user_search_base', 'ldap_user_search_filter',
                             'ldap_auto_create_users', 'ldap_default_role', 'ldap_sync_groups']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'Отсутствует обязательное поле: {field}'
                    }), 400
            
            # Сохранение настроек
            settings_service.save_ldap_settings(
                ldap_enabled=data['ldap_enabled'],
                ldap_server_url=data['ldap_server_url'],
                ldap_port=int(data['ldap_port']),
                ldap_use_ssl=data['ldap_use_ssl'],
                ldap_bind_dn=data['ldap_bind_dn'],
                ldap_bind_password=data['ldap_bind_password'],
                ldap_auth_method=data['ldap_auth_method'],
                ldap_user_search_base=data['ldap_user_search_base'],
                ldap_user_search_filter=data['ldap_user_search_filter'],
                ldap_auto_create_users=data['ldap_auto_create_users'],
                ldap_default_role=data['ldap_default_role'],
                ldap_sync_groups=data['ldap_sync_groups'],
                user_id=session.get('user_id')
            )
            
            return jsonify({
                'success': True,
                'message': 'Настройки LDAP успешно сохранены'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/ldap/test', methods=['POST'])
    @admin_required
    def test_ldap_connection():
        """API для тестирования подключения к LDAP"""
        try:
            data = request.get_json()
            
            # Импортируем LDAPService здесь для избежания циклических импортов
            from services.ldap_service import LDAPService
            ldap_service = LDAPService()
            
            # Тестирование подключения
            result = ldap_service.test_connection(
                server_url=data['ldap_server_url'],
                port=int(data['ldap_port']),
                use_ssl=data['ldap_use_ssl'],
                bind_dn=data['ldap_bind_dn'],
                bind_password=data['ldap_bind_password'],
                auth_method=data['ldap_auth_method']
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/ldap/search', methods=['POST'])
    @admin_required
    def search_ldap_users():
        """API для поиска пользователей в LDAP"""
        try:
            data = request.get_json()
            
            # Получаем текущие настройки LDAP
            ldap_settings = settings_service.get_ldap_settings()
            
            if ldap_settings['ldap_enabled'] != 'true':
                return jsonify({
                    'success': False,
                    'message': 'LDAP интеграция отключена'
                }), 400
            
            # Импортируем LDAPService здесь для избежания циклических импортов
            from services.ldap_service import LDAPService
            ldap_service = LDAPService()
            
            # Поиск пользователей
            result = ldap_service.search_users(
                search_term=data.get('search_term', ''),
                server_url=ldap_settings['ldap_server_url'],
                port=int(ldap_settings['ldap_port']),
                use_ssl=ldap_settings['ldap_use_ssl'] == 'true',
                bind_dn=ldap_settings['ldap_bind_dn'],
                bind_password=ldap_settings['ldap_bind_password'],
                auth_method=ldap_settings['ldap_auth_method']
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    @app.route('/api/settings/ldap/server-info', methods=['POST'])
    @admin_required
    def get_ldap_server_info():
        """API для получения информации о LDAP сервере"""
        try:
            data = request.get_json()
            
            # Импортируем LDAPService здесь для избежания циклических импортов
            from services.ldap_service import LDAPService
            ldap_service = LDAPService()
            
            # Получение информации о сервере
            result = ldap_service.get_server_info(
                server_url=data['ldap_server_url'],
                port=int(data['ldap_port']),
                use_ssl=data['ldap_use_ssl']
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    # Контекстный процессор для передачи текущего пользователя во все шаблоны
    @app.context_processor
    def inject_user():
        return dict(current_user=get_current_user())
    
    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.route('/test-js')
    def test_js():
        return render_template('test_js.html')

    @app.route('/debug-js')
    def debug_js():
        """Страница для отладки JavaScript"""
        return render_template('debug_js.html')

    @app.route('/admin/settings-fixed')
    @admin_required
    def admin_settings_fixed():
        """Исправленная страница настроек системы"""
        users = auth_service.get_all_users()
        telegram_settings = settings_service.get_telegram_settings()
        
        # Отключаем кэширование для этой страницы
        response = make_response(render_template('admin_settings_fixed.html', users=users, telegram_settings=telegram_settings))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    return app, auth_service, settings_service

if __name__ == '__main__':
    app, auth_service, settings_service = create_app(os.environ.get('FLASK_ENV', 'development'))
    
    # Создание таблиц при первом запуске
    with app.app_context():
        db.create_all()
        # Создание пользователей по умолчанию
        auth_service.create_default_users()
        # Создание настроек по умолчанию
        settings_service.create_default_settings()
    
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
