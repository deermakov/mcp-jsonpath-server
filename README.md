# MCP JSONPath Server

MCP-сервер для работы с JSON-файлами через JSONPath выражения.

## Функциональность

- ✅ Реализация протокола MCP (Model Context Protocol)
- ✅ SSE (Server-Sent Events) транспорт
- ✅ Инструмент `read_json` для чтения данных из JSON-файлов
- ✅ Поддержка JSONPath выражений для выборки данных
- ✅ Логирование всех операций
- ✅ Docker контейнеризация

## Структура проекта

```
mcp-jsonpath-server/
├── src/
│   └── server.py          # Основной файл сервера
├── config/                # Конфигурационные файлы
├── logs/                  # Логи сервера
├── data/                  # Данные (JSON файлы)
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
├── requirements.txt       # Python зависимости
├── .dockerignore          # Исключения для Docker
└── .env.example           # Пример файла окружения
```

## Установка и запуск

### Вариант 1: Docker Compose

```bash
# Клонирование или копирование проекта
cd mcp-jsonpath-server

# Создание файла окружения (опционально)
cp .env.example .env

# Запуск через Docker Compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Вариант 2: Docker

```bash
# Сборка образа
docker build -t mcp-jsonpath-server .

# Запуск контейнера
docker run -d \
  --name mcp-jsonpath-server \
  -p 3000:3000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  mcp-jsonpath-server
```

### Вариант 3: Локально (без Docker)

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python src/server.py
```

## Подключение MCP-клиентов

### 1. Claude Desktop (Desktop App)

Откройте файл конфигурации Claude Desktop:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Добавьте следующий конфиг:

```json
{
  "mcpServers": {
    "jsonpath-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "HOST=0.0.0.0",
        "-e", "PORT=3000",
        "-v", "${HOME}/mcp-jsonpath-server/logs:/app/logs",
        "-v", "${HOME}/mcp-jsonpath-server/data:/app/data",
        "mcp-jsonpath-server"
      ]
    }
  }
}
```

### 2. VS Code (MCP Inspector)

Установите расширение "MCP Inspector" в VS Code.

Откройте MCP Inspector и настройте подключение:

```json
{
  "mcpServers": {
    "jsonpath-server": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

### 3. Через HTTP API (для тестирования)

```bash
# Проверка доступности сервера
curl http://localhost:3000/health

# Пример запроса через cURL (если есть клиент)
curl -X POST http://localhost:3000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

## Использование инструмента `read_json`

### Примеры JSONPath выражений

1. **Чтение всего файла:**
   ```
   file_path: "data.json"
   json_path: "$"
   ```

2. **Чтение списка пользователей:**
   ```
   file_path: "users.json"
   json_path: "$.users[*].name"
   ```

3. **Чтение конкретного поля:**
   ```
   file_path: "config.json"
   json_path: "$.database.host"
   ```

4. **Чтение всех цен:**
   ```
   file_path: "products.json"
   json_path: "$.products[*].price"
   ```

5. **Чтение вложенных объектов:**
   ```
   file_path: "data.json"
   json_path: "$.store.book[*].author"
   ```

### Примеры использования в Claude

```
Прочитай данные из файла config.json по JSONPath "$.database"
Покажи все имена пользователей из файла users.json
Получи все цены из файла products.json
```

## Логирование

Логи сервера сохраняются в директории `logs/`:

```
logs/
├── mcp_server_20240101.log
├── mcp_server_20240102.log
└── ...
```

Формат логов:
```
2024-01-01 12:00:00 - __main__ - INFO - Запуск MCP JSONPath сервера
2024-01-01 12:00:01 - __main__ - INFO - Сервер запущен на 0.0.0.0:3000
2024-01-01 12:00:05 - __main__ - INFO - Вызов инструмента: read_json
2024-01-01 12:00:05 - __main__ - INFO - Успешно прочитан файл: data.json
```

## API Reference

### Инструменты

#### `read_json`

Читает данные из JSON-файла по указанному пути и JSONPath выражению.

**Параметры:**
- `file_path` (string, обязательный): Путь к JSON-файлу
- `json_path` (string, обязательный): JSONPath выражение

**Пример ответа:**
```json
{
  "file_path": "data.json",
  "json_path": "$.users[*].name",
  "matches_count": 3,
  "data": ["Alice", "Bob", "Charlie"]
}
```

### Промпты

#### `read_json_help`

Получает справку по использованию инструмента чтения JSON.

## Управление контейнером

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f

# Очистка логов
docker-compose down -v
rm -rf logs/*
```

## Технические детали

- **Протокол**: MCP (Model Context Protocol)
- **Транспорт**: SSE (Server-Sent Events)
- **Язык**: Python 3.11+
- **Зависимости**:
  - mcp (библиотека MCP)
  - starlette (ASGI фреймворк)
  - uvicorn (ASGI сервер)
  - jsonpath-ng (парсер JSONPath)

## Troubleshooting

### Контейнер не запускается

```bash
# Проверка логов
docker-compose logs

# Проверка порта
netstat -tuln | grep 3000
```

### Ошибка доступа к файлам

```bash
# Проверка прав доступа
ls -la logs/
chmod 755 logs/
```

### JSONPath не работает

Убедитесь, что JSONPath выражение корректно:
- Используйте `$` для корневого элемента
- Используйте `[*]` для всех элементов массива
- Проверьте структуру JSON файла

## Лицензия

MIT License