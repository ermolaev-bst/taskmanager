# Быстрый запуск системы "Менеджер задач"

## 🚀 Быстрый старт (5 минут)

### 1. Клонирование и установка

```bash
# Клонирование репозитория
git clone <your-repo-url>
cd taskmanager

# Создание виртуального окружения
python -m venv venv

# Активация окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Установка PostgreSQL (если не установлен)
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres createdb taskmanager
sudo -u postgres createuser taskmanager_user

# Инициализация таблиц
python setup_database.py
```

### 3. Настройка переменных окружения

```bash
# Копирование примера
cp .env.example .env

# Редактирование .env файла
# Минимальные настройки:
DATABASE_URL=postgresql://taskmanager_user@localhost/taskmanager
SECRET_KEY=dev-secret-key-change-in-production
```

### 4. Запуск приложения

```bash
# Запуск в режиме разработки
python app.py

# Или через Flask
flask run
```

### 5. Открытие в браузере

Перейдите по адресу: http://localhost:5000

## 📋 Что получилось

✅ **Рабочий стол** - управление активными задачами  
✅ **Архив** - просмотр выполненных задач  
✅ **Аналитика** - статистика эффективности  
✅ **API** - готовые эндпоинты для интеграции  
✅ **База данных** - PostgreSQL с тестовыми данными  

## 🔧 Основные команды

```bash
# Запуск приложения
python app.py

# Настройка базы данных
python setup_database.py

# Запуск через Flask CLI
flask run

# Проверка зависимостей
pip check

# Обновление зависимостей
pip install -r requirements.txt --upgrade
```

## 🌐 API Endpoints

```
GET  /                    - Главная страница
GET  /archive            - Архив задач
GET  /analytics          - Аналитика
GET  /task/<id>          - Просмотр задачи

POST /api/tasks          - Создание задачи
GET  /api/tasks          - Список задач
PUT  /api/tasks/<id>     - Обновление задачи
GET  /api/analytics      - API аналитики
```

## 🧪 Тестирование

### Создание тестовой задачи через API

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-secret-key-change-in-production" \
  -d '{
    "title": "Тестовая задача",
    "description": "Описание тестовой задачи",
    "task_type": "Прочее",
    "priority": "Средний",
    "requester_name": "Тест",
    "requester_department": "IT"
  }'
```

### Проверка аналитики

```bash
curl http://localhost:5000/api/analytics
```

## 🐳 Docker (альтернативный способ)

```bash
# Быстрый запуск через Docker
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f app
```

## 📁 Структура проекта

```
taskmanager/
├── app.py                 # Основное приложение
├── config.py             # Конфигурация
├── models/               # Модели данных
├── services/             # Бизнес-логика
├── templates/            # HTML шаблоны
├── static/               # CSS/JS файлы
├── database/             # Скрипты БД
├── requirements.txt      # Зависимости
└── README.md            # Документация
```

## 🚨 Устранение неполадок

### Ошибка подключения к базе данных
```bash
# Проверка статуса PostgreSQL
sudo systemctl status postgresql

# Перезапуск сервиса
sudo systemctl restart postgresql
```

### Ошибка импорта модулей
```bash
# Активация виртуального окружения
source venv/bin/activate

# Проверка установленных пакетов
pip list
```

### Порт 5000 занят
```bash
# Поиск процесса
lsof -i :5000

# Завершение процесса
kill -9 <PID>

# Или использование другого порта
flask run --port 5001
```

## 🔄 Следующие шаги

1. **Настройка Telegram бота** - см. `google_forms_integration.md`
2. **Интеграция с Google Forms** - см. `google_forms_integration.md`
3. **Настройка продакшена** - см. `DEPLOYMENT.md`
4. **Кастомизация интерфейса** - редактирование `templates/` и `static/`

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки базы данных
4. Изучите документацию в папке проекта

## 🎯 Готово!

Теперь у вас есть полностью функционирующая система управления IT-заявками с современным веб-интерфейсом, API и аналитикой!

---

**Время разработки**: ~2 часа  
**Сложность**: Средняя  
**Статус**: Готово к использованию
