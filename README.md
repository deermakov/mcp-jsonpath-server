# MCP-сервер для работы с JSON-файлами

Модельный контекстный протокол (MCP) сервер, который предоставляет инструменты для работы с JSON-файлами с использованием jsonPath.

## Функциональность

### Инструменты (Tools)

#### 1. `read_json_file`
Читает JSON-файл и возвращает данные по указанному jsonPath.

**Параметры:**
- `file_path` (str): Путь к JSON-файлу
- `json_path` (str, optional): Опциональный jsonPath для получения конкретного значения
  - Примеры: `"user.name"`, `"items[0].price"`, `"data.users[1].email"`

**Возвращает:**
```json
{
  "success": true,
  "data": {...},
  "file_path": "/path/to/file.json",
  "path_used": "user.name"
}
```

#### 2. `list_json_files`
Перечисляет все JSON-файлы в указанной директории.

**Параметры:**
- `directory` (str): Путь к директории для поиска JSON-файлов

**Возвращает:**
```json
{
  "success": true,
  "files": ["/path/to/file1.json", "/path/to/file2.json"],
  "count": 2,
  "directory": "/path/to/dir"
}
```

## Логирование

Все операции сервера логируются в файл `mcp_json_server.log` и выводятся в консоль.

Формат логов:
```
2024-01-01 12:00:00 - __main__ - INFO - Запрос на чтение JSON-файла: /app/data/config.json, jsonPath: user.name
2024-01-01 12:00:00 - __main__ - INFO - Успешно загружен JSON-файл: /app/data/config.json, размер: 1234 байт
2024-01-01 12:00:00 - __main__ - INFO - Успешно получено значение по jsonPath: user.name
```

## Установка и запуск

### Требования
- Docker
- Docker Compose

### Шаги установки

1. **Клонирование или копирование проекта**
   ```bash
   cd C:\_Work\ML\MCPJSON\mcp-json
   ```

2. **Создание директории для данных**
   ```bash
   mkdir data
   mkdir logs
   ```

3. **Запуск через Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Проверка работы**
   ```bash
   docker-compose logs -f
   ```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

## Структура проекта

```
mcp-json/
├── main.py              # Основной файл MCP-сервера
├── requirements.txt     # Зависимости Python
├── Dockerfile           # Docker-образ
├── docker-compose.yml   # Конфигурация Docker Compose
├── .dockerignore        # Исключения для Docker
├── README.md            # Документация
├── data/                # Директория для JSON-файлов (создается вручную)
└── logs/                # Директория для логов (создается автоматически)
```

## Использование jsonPath

Сервер поддерживает стандартный синтаксис jsonPath:

- `field` - доступ к полю объекта
- `field.subfield` - доступ к вложенному полю
- `array[0]` - доступ к элементу массива по индексу
- `array[0].field` - доступ к полю внутри элемента массива

### Примеры

Если у вас есть JSON-файл `data/config.json`:
```json
{
  "user": {
    "name": "John",
    "email": "john@example.com"
  },
  "items": [
    {"id": 1, "price": 100},
    {"id": 2, "price": 200}
  ]
}
```

Использование:
- `read_json_file("data/config.json", "user.name")` → `"John"`
- `read_json_file("data/config.json", "items[0].price")` → `100`
- `read_json_file("data/config.json")` → все данные

## Безопасность

- Доступ к файлам ограничен директорией `data` (монтируется как read-only)
- Логи записываются в директорию `logs`
- Используется минимальный набор зависимостей

## Технологии

- Python 3.11
- FastMCP - библиотека для создания MCP-серверов
- Docker - контейнеризация
- Docker Compose - оркестрация контейнеров

## Лицензия

MIT License