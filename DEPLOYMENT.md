# Инструкция по развертыванию системы "Менеджер задач"

## Обзор

Данный документ содержит пошаговые инструкции по развертыванию корпоративной системы управления IT-заявками "Менеджер задач".

## Требования к системе

### Минимальные требования:
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **RAM**: 4 GB
- **CPU**: 2 ядра
- **Диск**: 20 GB свободного места
- **Сеть**: Статический IP адрес

### Рекомендуемые требования:
- **ОС**: Ubuntu 22.04 LTS
- **RAM**: 8 GB
- **CPU**: 4 ядра
- **Диск**: 50 GB SSD
- **Сеть**: Статический IP, SSL сертификат

## Варианты развертывания

### 1. Локальное развертывание (для разработки)

#### Установка зависимостей

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server nginx
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Настройка Python окружения

```bash
cd taskmanager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Настройка базы данных

```bash
# Создание пользователя и базы
sudo -u postgres psql
CREATE USER taskmanager_user WITH PASSWORD 'secure_password';
CREATE DATABASE taskmanager OWNER taskmanager_user;
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskmanager_user;
\q

# Инициализация таблиц
python setup_database.py
```

#### Запуск приложения

```bash
# Разработка
python app.py

# Продакшен
gunicorn --bind 0.0.0.0:5000 --workers 4 app:create_app()
```

### 2. Docker развертывание (рекомендуется)

#### Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

#### Установка Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Развертывание

```bash
cd taskmanager

# Копирование и настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 3. Облачное развертывание

#### Google Cloud Platform

```bash
# Установка gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Создание проекта
gcloud projects create taskmanager-project
gcloud config set project taskmanager-project

# Включение API
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Создание инстанса
gcloud compute instances create taskmanager \
  --zone=europe-west1-b \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# Открытие портов
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags=http-server \
  --source-ranges=0.0.0.0/0

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags=https-server \
  --source-ranges=0.0.0.0/0
```

#### AWS

```bash
# Установка AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Создание EC2 инстанса
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx
```

## Настройка переменных окружения

### Создание .env файла

```bash
cp .env.example .env
```

### Основные настройки

```bash
# Безопасность
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# База данных
DATABASE_URL=postgresql://username:password@localhost/taskmanager

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Google Forms
GOOGLE_FORMS_SECRET_TOKEN=your_secret_token
```

### Генерация секретного ключа

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Настройка базы данных

### PostgreSQL

```bash
# Создание пользователя
sudo -u postgres createuser --interactive taskmanager_user

# Создание базы
sudo -u postgres createdb taskmanager

# Настройка аутентификации
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Добавьте строку:
local   taskmanager       taskmanager_user                     md5

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

### Инициализация схемы

```bash
cd taskmanager
python setup_database.py
```

## Настройка веб-сервера

### Nginx

```bash
# Создание конфигурации
sudo nano /etc/nginx/sites-available/taskmanager
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/taskmanager/static;
        expires 30d;
    }
}
```

```bash
# Активация сайта
sudo ln -s /etc/nginx/sites-available/taskmanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL сертификат (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автообновление
sudo crontab -e
# Добавьте строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Настройка Telegram бота

### Создание бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Сохраните токен бота

### Настройка уведомлений

```bash
# Получение Chat ID
# Отправьте сообщение боту и перейдите по ссылке:
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

## Настройка Google Forms

### Создание формы

1. Перейдите на [Google Forms](https://forms.google.com)
2. Создайте форму с необходимыми полями
3. Настройте Apps Script (см. `google_forms_integration.md`)

### Тестирование интеграции

```bash
# Проверка API
curl -X POST http://your-domain.com/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Тест","description":"Описание","task_type":"Прочее"}'
```

## Мониторинг и логирование

### Настройка логов

```bash
# Создание директории для логов
mkdir -p /var/log/taskmanager

# Настройка ротации логов
sudo nano /etc/logrotate.d/taskmanager
```

```
/var/log/taskmanager/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### Мониторинг системы

```bash
# Установка мониторинга
sudo apt install htop iotop nethogs

# Проверка ресурсов
htop
df -h
free -h
```

## Резервное копирование

### База данных

```bash
# Создание скрипта бэкапа
sudo nano /usr/local/bin/backup-taskmanager.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/taskmanager"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="taskmanager"
DB_USER="taskmanager_user"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/taskmanager_$DATE.sql
gzip $BACKUP_DIR/taskmanager_$DATE.sql

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

```bash
# Права на выполнение
sudo chmod +x /usr/local/bin/backup-taskmanager.sh

# Добавление в cron
sudo crontab -e
# Добавьте строку:
0 2 * * * /usr/local/bin/backup-taskmanager.sh
```

### Файлы приложения

```bash
# Создание архива
tar -czf taskmanager_backup_$(date +%Y%m%d).tar.gz taskmanager/

# Автоматизация
sudo crontab -e
# Добавьте строку:
0 3 * * * cd /path/to/backup && tar -czf taskmanager_backup_$(date +%Y%m%d).tar.gz /path/to/taskmanager
```

## Обновление системы

### Обновление кода

```bash
cd taskmanager
git pull origin main
pip install -r requirements.txt
sudo systemctl restart taskmanager
```

### Обновление базы данных

```bash
# Создание бэкапа
pg_dump -U taskmanager_user taskmanager > backup_before_update.sql

# Применение миграций
flask db upgrade
```

## Устранение неполадок

### Проверка статуса сервисов

```bash
# Проверка статуса
sudo systemctl status taskmanager
sudo systemctl status postgresql
sudo systemctl status nginx

# Просмотр логов
sudo journalctl -u taskmanager -f
sudo tail -f /var/log/postgresql/postgresql-*.log
sudo tail -f /var/log/nginx/error.log
```

### Частые проблемы

1. **Ошибка подключения к базе данных**
   - Проверьте статус PostgreSQL
   - Проверьте настройки подключения
   - Проверьте права пользователя

2. **Ошибка 502 Bad Gateway**
   - Проверьте статус приложения
   - Проверьте конфигурацию Nginx
   - Проверьте порты

3. **Ошибки Telegram уведомлений**
   - Проверьте токен бота
   - Проверьте Chat ID
   - Проверьте доступность API

## Безопасность

### Firewall

```bash
# Настройка UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
```

### Обновления системы

```bash
# Автоматические обновления
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Мониторинг безопасности

```bash
# Установка fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Производительность

### Оптимизация базы данных

```bash
# Настройка PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf

# Основные параметры:
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Кеширование

```bash
# Установка Redis
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## Заключение

После выполнения всех шагов у вас будет полностью функционирующая система "Менеджер задач" с:

- ✅ Веб-интерфейсом для управления задачами
- ✅ API для интеграции с Google Forms
- ✅ Telegram уведомлениями
- ✅ Аналитикой эффективности
- ✅ Автоматическим резервным копированием
- ✅ Мониторингом и логированием
- ✅ SSL сертификатом
- ✅ Настроенной безопасностью

### Следующие шаги:

1. Настройте мониторинг производительности
2. Настройте алерты для критических событий
3. Проведите тестирование под нагрузкой
4. Обучите пользователей работе с системой
5. Документируйте процедуры эксплуатации

