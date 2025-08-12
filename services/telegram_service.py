import requests
import os
from datetime import datetime, timedelta
from models.task import Task
from services.task_service import TaskService
import threading
import time

class TelegramService:
    """Сервис для работы с Telegram уведомлениями"""
    
    def __init__(self):
        # Инициализация с пустыми значениями, настройки будут загружаться динамически
        self.bot_token = None
        self.chat_id = None
        self.base_url = None
        self._settings_loaded = False
        
        # НЕ загружаем настройки здесь - это вызовет ошибку контекста приложения
        # Настройки будут загружены при первом вызове методов
    
    def _load_settings(self):
        """Загрузка настроек из базы данных"""
        if self._settings_loaded:
            return
            
        try:
            from models.settings import SystemSettings
            
            self.bot_token = SystemSettings.get_setting('telegram_bot_token')
            self.chat_id = SystemSettings.get_setting('telegram_chat_id')
            
            if self.bot_token:
                self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            
            self._settings_loaded = True
            
        except Exception as e:
            print(f"Ошибка загрузки настроек Telegram: {e}")
            # Fallback к переменным окружения
            self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            if self.bot_token:
                self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            self._settings_loaded = True
    
    def reload_settings(self):
        """Перезагрузка настроек из базы данных"""
        self._settings_loaded = False
        self._load_settings()
    
    def send_message(self, message, parse_mode='HTML'):
        """Отправка сообщения в Telegram"""
        # Загружаем настройки при первом вызове
        if not self._settings_loaded:
            self._load_settings()
            
        if not self.bot_token or not self.chat_id:
            print(f"Telegram не настроен. Сообщение: {message}")
            return True  # Возвращаем True, чтобы не блокировать создание задачи
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print(f"Уведомление в Telegram отправлено успешно")
                return True
            else:
                print(f"Ошибка отправки в Telegram: HTTP {response.status_code}")
                return False
            
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")
            return False
    
    def send_private_message(self, telegram_username, message, parse_mode='HTML'):
        """Отправка личного сообщения пользователю по Telegram username"""
        if not self._settings_loaded:
            self._load_settings()
            
        if not self.bot_token:
            print(f"Telegram бот не настроен. Не удалось отправить сообщение пользователю {telegram_username}")
            return False
            
        if not telegram_username:
            print(f"Telegram username не указан для пользователя")
            return False
        
        try:
            # Убираем @ если есть
            username = telegram_username.lstrip('@')
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': f"@{username}",
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print(f"Личное сообщение пользователю {telegram_username} отправлено успешно")
                return True
            else:
                print(f"Ошибка отправки личного сообщения пользователю {telegram_username}: HTTP {response.status_code}")
                return False
            
        except Exception as e:
            print(f"Ошибка отправки личного сообщения пользователю {telegram_username}: {e}")
            return False
    
    def send_new_task_notification(self, task):
        """Уведомление о новой заявке"""
        message = f"""
🚨 <b>Новая заявка!</b>

📋 <b>Задача:</b> {task.task_number}
🏷 <b>Название:</b> {task.title}
📝 <b>Тип:</b> {task.task_type}
⚡ <b>Приоритет:</b> {task.priority}
👤 <b>От:</b> {task.requester_name} ({task.requester_department})
⏰ <b>Создано:</b> {task.created_at.strftime('%d.%m.%Y %H:%M')}
        """.strip()
        
        # Отправляем в общий чат
        self.send_message(message)
        
        # Отправляем личные уведомления IT сотрудникам
        self._notify_it_staff_new_task(task)
    
    def send_status_change_notification(self, task):
        """Уведомление об изменении статуса задачи"""
        status_emoji = {
            'В работе': '🔄',
            'В очереди': '⏳',
            'Ожидает': '⏸',
            'Готово': '✅',
            'Отменено': '❌'
        }
        
        emoji = status_emoji.get(task.status, '📊')
        
        message = f"""
{emoji} <b>Изменение статуса задачи</b>

📋 <b>Задача:</b> {task.task_number}
🏷 <b>Название:</b> {task.title}
🔄 <b>Новый статус:</b> {task.status}
👤 <b>Исполнитель:</b> {task.assigned_to.name if task.assigned_to else 'Не назначен'}
⏰ <b>Обновлено:</b> {task.updated_at.strftime('%d.%m.%Y %H:%M')}
        """.strip()
        
        # Отправляем в общий чат
        self.send_message(message)
        
        # Отправляем личное уведомление заявителю
        if task.requester_email:
            self._notify_requester_status_change(task)
    
    def _notify_it_staff_new_task(self, task):
        """Уведомление IT сотрудников о новой задаче"""
        try:
            from models.user import User
            
            # Получаем всех активных IT сотрудников
            it_staff = User.query.filter_by(role='it_staff', is_active=True).all()
            
            for user in it_staff:
                if user.telegram_username:
                    message = f"""
🔔 <b>Новая задача для IT отдела!</b>

📋 <b>Задача:</b> {task.task_number}
🏷 <b>Название:</b> {task.title}
📝 <b>Тип:</b> {task.task_type}
⚡ <b>Приоритет:</b> {task.priority}
👤 <b>От:</b> {task.requester_name} ({task.requester_department})
⏰ <b>Создано:</b> {task.created_at.strftime('%d.%m.%Y %H:%M')}

💻 Перейдите в систему для принятия задачи в работу.
                    """.strip()
                    
                    self.send_private_message(user.telegram_username, message)
                    
        except Exception as e:
            print(f"Ошибка при уведомлении IT сотрудников: {e}")
    
    def _notify_requester_status_change(self, task):
        """Уведомление заявителя об изменении статуса задачи"""
        try:
            from models.user import User
            
            # Ищем пользователя по email
            user = User.query.filter_by(email=task.requester_email, is_active=True).first()
            
            if user and user.telegram_username:
                status_emoji = {
                    'В работе': '🔄',
                    'В очереди': '⏳',
                    'Ожидает': '⏸',
                    'Готово': '✅',
                    'Отменено': '❌'
                }
                
                emoji = status_emoji.get(task.status, '📊')
                
                message = f"""
{emoji} <b>Статус вашей задачи изменен</b>

📋 <b>Задача:</b> {task.task_number}
🏷 <b>Название:</b> {task.title}
🔄 <b>Новый статус:</b> {task.status}
👤 <b>Исполнитель:</b> {task.assigned_to.name if task.assigned_to else 'Не назначен'}
⏰ <b>Обновлено:</b> {task.updated_at.strftime('%d.%m.%Y %H:%M')}

🔗 Следите за статусом в системе: {self._get_system_url()}
                """.strip()
                
                self.send_private_message(user.telegram_username, message)
                
        except Exception as e:
            print(f"Ошибка при уведомлении заявителя: {e}")
    
    def _get_system_url(self):
        """Получение URL системы для ссылок в уведомлениях"""
        # В реальном проекте это должно быть в настройках
        return "http://localhost:5000"  # Заглушка
    
    def send_overdue_reminder(self, overdue_tasks):
        """Напоминание о просроченных задачах"""
        if not overdue_tasks:
            return
        
        message = f"""
⚠️ <b>Просроченные задачи!</b>

Найдено <b>{len(overdue_tasks)}</b> просроченных задач:

"""
        
        for task in overdue_tasks[:5]:  # Показываем только первые 5
            overdue_days = (datetime.utcnow() - task.deadline).days
            message += f"• {task.task_number}: {task.title} (просрочено на {overdue_days} дн.)\n"
        
        if len(overdue_tasks) > 5:
            message += f"\n... и еще {len(overdue_tasks) - 5} задач"
        
        self.send_message(message)
    
    def send_unassigned_reminder(self, unassigned_tasks):
        """Напоминание о неразобранных заявках"""
        if not unassigned_tasks:
            return
        
        message = f"""
📋 <b>Неразобранные заявки</b>

Найдено <b>{len(unassigned_tasks)}</b> неразобранных заявок:

"""
        
        for task in unassigned_tasks[:5]:  # Показываем только первые 5
            hours_ago = int((datetime.utcnow() - task.created_at).total_seconds() / 3600)
            message += f"• {task.task_number}: {task.title} ({hours_ago} ч. назад)\n"
        
        if len(unassigned_tasks) > 5:
            message += f"\n... и еще {len(unassigned_tasks) - 5} заявок"
        
        self.send_message(message)
    
    def _start_background_notifications(self):
        """Запуск фонового процесса для периодических уведомлений"""
        def background_worker():
            while True:
                try:
                    # Проверка каждые 2 часа
                    time.sleep(2 * 60 * 60)
                    
                    # Отправка напоминаний
                    self._send_periodic_reminders()
                    
                except Exception as e:
                    print(f"Ошибка в фоновом процессе уведомлений: {e}")
                    time.sleep(60)  # Пауза при ошибке
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
    
    def _send_periodic_reminders(self):
        """Отправка периодических напоминаний"""
        try:
            # Получение просроченных задач
            task_service = TaskService()
            overdue_tasks = task_service.get_overdue_tasks()
            
            if overdue_tasks:
                self.send_overdue_reminder(overdue_tasks)
            
            # Получение неразобранных заявок
            unassigned_tasks = task_service.get_unassigned_tasks()
            
            if unassigned_tasks:
                self.send_unassigned_reminder(unassigned_tasks)
                
        except Exception as e:
            print(f"Ошибка при отправке периодических напоминаний: {e}")
    
    def test_connection(self):
        """Тестирование подключения к Telegram"""
        # Загружаем настройки при первом вызове
        if not self._settings_loaded:
            self._load_settings()
            
        if not self.bot_token:
            return False, "Токен бота не настроен", None, None
        
        try:
            # Тестируем подключение к боту
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return False, f"Ошибка API бота: {response.status_code}", None, None
            
            bot_info = response.json()['result']
            
            # Тестируем отправку сообщения в чат
            if self.chat_id:
                test_url = f"{self.base_url}/sendMessage"
                test_data = {
                    'chat_id': self.chat_id,
                    'text': '🧪 Тестовое сообщение от Менеджера задач\n\nЕсли вы видите это сообщение, значит настройки корректны!',
                    'parse_mode': 'HTML'
                }
                
                test_response = requests.post(test_url, data=test_data, timeout=10)
                
                if test_response.status_code == 200:
                    chat_info = test_response.json()['result']['chat']
                    return True, f"Подключение успешно! Бот: {bot_info['username']}", bot_info, chat_info
                else:
                    return False, f"Ошибка отправки в чат: {test_response.status_code}", bot_info, None
            else:
                return False, "ID чата не настроен", bot_info, None
                
        except Exception as e:
            return False, f"Ошибка подключения: {e}", None, None
