from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models.task import Task, db
from models.user import User

class AnalyticsService:
    """Сервис для аналитики эффективности выполнения задач"""
    
    def __init__(self):
        self.db = db
    
    def get_performance_stats(self):
        """Получение основных показателей эффективности"""
        # Получение выполненных задач за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        completed_tasks = Task.query.filter(
            and_(
                Task.status == 'Готово',
                Task.completed_at >= thirty_days_ago
            )
        ).all()
        
        # Расчет средних показателей
        avg_time_to_take = self._calculate_avg_time_to_take(completed_tasks)
        avg_time_to_complete = self._calculate_avg_time_to_complete(completed_tasks)
        
        # Статистика по типам задач
        task_type_stats = self._get_task_type_statistics()
        
        # Статистика по приоритетам
        priority_stats = self._get_priority_statistics()
        
        # Статистика по исполнителям
        user_stats = self._get_user_statistics()
        
        # Тренды по дням
        daily_trends = self._get_daily_trends()
        
        return {
            'overview': {
                'total_completed_tasks': len(completed_tasks),
                'avg_time_to_take_minutes': avg_time_to_take,
                'avg_time_to_complete_hours': avg_time_to_complete,
                'period_days': 30
            },
            'task_type_statistics': task_type_stats,
            'priority_statistics': priority_stats,
            'user_statistics': user_stats,
            'daily_trends': daily_trends,
            'detailed_tasks': [task.to_dict() for task in completed_tasks[:50]]  # Последние 50 задач
        }
    
    def _calculate_avg_time_to_take(self, tasks):
        """Расчет среднего времени от создания до взятия в работу (в минутах)"""
        valid_tasks = [task for task in tasks if task.time_to_take is not None]
        
        if not valid_tasks:
            return 0
        
        total_minutes = sum(task.time_to_take for task in valid_tasks)
        return round(total_minutes / len(valid_tasks), 1)
    
    def _calculate_avg_time_to_complete(self, tasks):
        """Расчет среднего времени от взятия в работу до выполнения (в часах)"""
        valid_tasks = [task for task in tasks if task.time_to_complete is not None]
        
        if not valid_tasks:
            return 0
        
        total_hours = sum(task.time_to_complete for task in valid_tasks)
        return round(total_hours / len(valid_tasks), 2)
    
    def _get_task_type_statistics(self):
        """Статистика по типам задач"""
        stats = db.session.query(
            Task.task_type,
            func.count(Task.id).label('total'),
            func.avg(func.extract('epoch', Task.completed_at - Task.created_at) / 3600).label('avg_hours')
        ).filter(
            Task.status == 'Готово'
        ).group_by(Task.task_type).all()
        
        return [
            {
                'task_type': stat.task_type,
                'total': stat.total,
                'avg_hours': round(stat.avg_hours, 2) if stat.avg_hours else 0
            }
            for stat in stats
        ]
    
    def _get_priority_statistics(self):
        """Статистика по приоритетам задач"""
        stats = db.session.query(
            Task.priority,
            func.count(Task.id).label('total'),
            func.avg(func.extract('epoch', Task.completed_at - Task.created_at) / 3600).label('avg_hours')
        ).filter(
            Task.status == 'Готово'
        ).group_by(Task.priority).all()
        
        return [
            {
                'priority': stat.priority,
                'total': stat.total,
                'avg_hours': round(stat.avg_hours, 2) if stat.avg_hours else 0
            }
            for stat in stats
        ]
    
    def _get_user_statistics(self):
        """Статистика по исполнителям"""
        stats = db.session.query(
            User.name,
            func.count(Task.id).label('total'),
            func.avg(func.extract('epoch', Task.completed_at - Task.taken_at) / 3600).label('avg_hours')
        ).join(Task, User.id == Task.assigned_to_id).filter(
            Task.status == 'Готово'
        ).group_by(User.name).all()
        
        return [
            {
                'user_name': stat.name,
                'total': stat.total,
                'avg_hours': round(stat.avg_hours, 2) if stat.avg_hours else 0
            }
            for stat in stats
        ]
    
    def _get_daily_trends(self):
        """Тренды по дням за последние 30 дней"""
        trends = []
        for i in range(30):
            date = datetime.utcnow().date() - timedelta(days=i)
            
            # Задачи, созданные в этот день
            created_count = Task.query.filter(
                func.date(Task.created_at) == date
            ).count()
            
            # Задачи, завершенные в этот день
            completed_count = Task.query.filter(
                func.date(Task.completed_at) == date
            ).count()
            
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'created': created_count,
                'completed': completed_count
            })
        
        return list(reversed(trends))
    
    def get_user_performance(self, user_id, days=30):
        """Детальная статистика по конкретному пользователю"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Задачи пользователя
        user_tasks = Task.query.filter(
            and_(
                Task.assigned_to_id == user_id,
                Task.created_at >= start_date
            )
        ).all()
        
        # Статистика по статусам
        status_stats = {}
        for task in user_tasks:
            status = task.status
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # Средние показатели
        completed_tasks = [t for t in user_tasks if t.status == 'Готово']
        avg_time_to_complete = self._calculate_avg_time_to_complete(completed_tasks)
        
        return {
            'user_id': str(user_id),
            'period_days': days,
            'total_tasks': len(user_tasks),
            'completed_tasks': len(completed_tasks),
            'status_distribution': status_stats,
            'avg_time_to_complete_hours': avg_time_to_complete,
            'tasks': [task.to_dict() for task in user_tasks]
        }
    
    def get_department_performance(self, department, days=30):
        """Статистика по отделу"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Задачи отдела
        dept_tasks = Task.query.filter(
            and_(
                Task.requester_department == department,
                Task.created_at >= start_date
        )).all()
        
        # Статистика по статусам
        status_stats = {}
        for task in dept_tasks:
            status = task.status
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # Средние показатели
        completed_tasks = [t for t in dept_tasks if t.status == 'Готово']
        avg_time_to_take = self._calculate_avg_time_to_take(completed_tasks)
        avg_time_to_complete = self._calculate_avg_time_to_complete(completed_tasks)
        
        return {
            'department': department,
            'period_days': days,
            'total_tasks': len(dept_tasks),
            'completed_tasks': len(completed_tasks),
            'status_distribution': status_stats,
            'avg_time_to_take_minutes': avg_time_to_take,
            'avg_time_to_complete_hours': avg_time_to_complete,
            'tasks': [task.to_dict() for task in dept_tasks]
        }
    
    def get_overdue_analysis(self):
        """Анализ просроченных задач"""
        overdue_tasks = Task.query.filter(
            and_(
                Task.deadline < datetime.utcnow(),
                Task.status.notin_(['Готово', 'Отменено'])
            )
        ).all()
        
        if not overdue_tasks:
            return {'total': 0, 'tasks': []}
        
        # Группировка по дням просрочки
        overdue_days = {}
        for task in overdue_tasks:
            days = (datetime.utcnow() - task.deadline).days
            if days not in overdue_days:
                overdue_days[days] = []
            overdue_days[days].append(task)
        
        return {
            'total': len(overdue_tasks),
            'by_days': {
                days: len(tasks) for days, tasks in overdue_days.items()
            },
            'tasks': [task.to_dict() for task in overdue_tasks]
        }
