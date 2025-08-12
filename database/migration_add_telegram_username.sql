-- Миграция: Добавление поля telegram_username в таблицу users
-- Дата: 2024-01-XX
-- Описание: Добавляет поле для хранения Telegram username пользователей

-- Добавляем новое поле telegram_username
ALTER TABLE users ADD COLUMN telegram_username VARCHAR(50);

-- Добавляем комментарий к полю
COMMENT ON COLUMN users.telegram_username IS 'Telegram username пользователя для отправки уведомлений';

-- Создаем индекс для быстрого поиска по telegram_username
CREATE INDEX idx_users_telegram_username ON users(telegram_username);

-- Обновляем существующих пользователей (опционально)
-- UPDATE users SET telegram_username = NULL WHERE telegram_username IS NULL;

-- Проверяем структуру таблицы
-- \d users;
