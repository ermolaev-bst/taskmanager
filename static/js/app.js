/**
 * Основной JavaScript файл для Менеджера задач
 */

// Глобальные переменные
let currentUser = null;
let notifications = [];

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Инициализация приложения
 */
function initializeApp() {
    console.log('Инициализация Менеджера задач...');
    
    // Инициализация компонентов
    initializeNotifications();
    initializeTooltips();
    initializeModals();
    
    // Загрузка данных пользователя
    loadCurrentUser();
    
    // Настройка автообновления
    setupAutoRefresh();
    
    console.log('Приложение инициализировано');
}

/**
 * Инициализация уведомлений
 */
function initializeNotifications() {
    // Создание контейнера для уведомлений
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

/**
 * Инициализация всплывающих подсказок
 */
function initializeTooltips() {
    // Инициализация Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализация модальных окон
 */
function initializeModals() {
    // Обработка закрытия модальных окон
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal') || e.target.classList.contains('modal-backdrop')) {
            closeAllModals();
        }
    });
}

/**
 * Загрузка данных текущего пользователя
 */
function loadCurrentUser() {
    // В реальном приложении здесь будет API запрос
    currentUser = {
        id: '1',
        name: 'IT Сотрудник',
        role: 'user',
        department: 'IT отдел'
    };
    
    updateUserInterface();
}

/**
 * Обновление пользовательского интерфейса
 */
function updateUserInterface() {
    if (currentUser) {
        // Обновление имени пользователя в навигации
        const userMenu = document.querySelector('.navbar-nav .dropdown-toggle');
        if (userMenu) {
            userMenu.innerHTML = `<i class="bi bi-person-circle"></i> ${currentUser.name}`;
        }
    }
}

/**
 * Настройка автообновления
 */
function setupAutoRefresh() {
    // Автообновление каждые 5 минут
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            refreshData();
        }
    }, 5 * 60 * 1000);
}

/**
 * Обновление данных
 */
function refreshData() {
    // Обновление только если страница активна
    if (document.visibilityState === 'visible') {
        location.reload();
    }
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Автоматическое скрытие
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Сохранение в историю
    notifications.push({
        message: message,
        type: type,
        timestamp: new Date()
    });
}

/**
 * Закрыть все модальные окна
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

/**
 * Форматирование даты
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Форматирование времени
 */
function formatDuration(minutes) {
    if (!minutes || minutes < 0) return '-';
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}ч ${mins}м`;
    } else {
        return `${mins}м`;
    }
}

/**
 * Валидация формы
 */
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Очистка формы
 */
function clearForm(formElement) {
    formElement.reset();
    formElement.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
}

/**
 * Экспорт данных в CSV
 */
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showNotification('Нет данных для экспорта', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Поиск по таблице
 */
function searchTable(searchTerm, tableSelector) {
    const table = document.querySelector(tableSelector);
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Сортировка таблицы
 */
function sortTable(tableSelector, columnIndex, type = 'string') {
    const table = document.querySelector(tableSelector);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].textContent.trim();
        let bValue = b.cells[columnIndex].textContent.trim();
        
        if (type === 'number') {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        } else if (type === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        
        if (aValue < bValue) return -1;
        if (aValue > bValue) return 1;
        return 0;
    });
    
    // Пересортировка строк
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Фильтрация задач
 */
function filterTasks(filters) {
    const taskRows = document.querySelectorAll('.task-row');
    
    taskRows.forEach(row => {
        let show = true;
        
        // Применение фильтров
        if (filters.status && filters.status !== 'all') {
            const status = row.querySelector('.task-status').textContent;
            if (status !== filters.status) show = false;
        }
        
        if (filters.type && filters.type !== 'all') {
            const type = row.querySelector('.task-type').textContent;
            if (type !== filters.type) show = false;
        }
        
        if (filters.priority && filters.priority !== 'all') {
            const priority = row.querySelector('.task-priority').textContent;
            if (priority !== filters.priority) show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

/**
 * Обновление статистики в реальном времени
 */
function updateStatistics() {
    // Обновление счетчиков
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const current = parseInt(counter.textContent);
        
        if (current < target) {
            counter.textContent = current + 1;
        }
    });
}

/**
 * Обработка ошибок API
 */
function handleApiError(error, context = '') {
    console.error(`API Error in ${context}:`, error);
    
    let message = 'Произошла ошибка при выполнении операции';
    
    if (error.response) {
        switch (error.response.status) {
            case 400:
                message = 'Неверный запрос';
                break;
            case 401:
                message = 'Необходима авторизация';
                break;
            case 403:
                message = 'Доступ запрещен';
                break;
            case 404:
                message = 'Ресурс не найден';
                break;
            case 500:
                message = 'Внутренняя ошибка сервера';
                break;
            default:
                message = `Ошибка ${error.response.status}`;
        }
    } else if (error.request) {
        message = 'Ошибка сети';
    }
    
    showNotification(message, 'danger');
}

/**
 * Утилиты для работы с данными
 */
const DataUtils = {
    // Группировка по полю
    groupBy: (array, key) => {
        return array.reduce((result, item) => {
            const group = item[key];
            if (!result[group]) {
                result[group] = [];
            }
            result[group].push(item);
            return result;
        }, {});
    },
    
    // Сортировка по полю
    sortBy: (array, key, direction = 'asc') => {
        return array.sort((a, b) => {
            let aVal = a[key];
            let bVal = b[key];
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (direction === 'desc') {
                [aVal, bVal] = [bVal, aVal];
            }
            
            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
        });
    },
    
    // Фильтрация по условию
    filterBy: (array, condition) => {
        return array.filter(condition);
    }
};

// Экспорт функций для использования в других модулях
window.TaskManager = {
    showNotification,
    formatDate,
    formatDuration,
    validateForm,
    clearForm,
    exportToCSV,
    searchTable,
    sortTable,
    filterTasks,
    DataUtils
};
