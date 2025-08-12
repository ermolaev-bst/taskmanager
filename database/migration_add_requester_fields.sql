-- Миграция для добавления новых полей заявителя в таблицу tasks
-- Выполнить после обновления модели Task

-- Добавление поля для email заявителя
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS requester_email VARCHAR(120);

-- Добавление поля для телефона заявителя  
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS requester_phone VARCHAR(20);

-- Обновление существующих записей (опционально)
-- UPDATE tasks SET requester_email = 'unknown@company.com' WHERE requester_email IS NULL;
-- UPDATE tasks SET requester_phone = 'Не указан' WHERE requester_phone IS NULL;

-- Создание индекса для поиска по email (опционально)
-- CREATE INDEX IF NOT EXISTS idx_tasks_requester_email ON tasks(requester_email);

-- Создание индекса для поиска по телефону (опционально)
-- CREATE INDEX IF NOT EXISTS idx_tasks_requester_phone ON tasks(requester_phone);

COMMENT ON COLUMN tasks.requester_email IS 'Email адрес заявителя';
COMMENT ON COLUMN tasks.requester_phone IS 'Телефон заявителя';
