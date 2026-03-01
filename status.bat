@echo off
REM Скрипт для проверки статуса MCP JSONPath сервера

echo 📊 Статус MCP JSONPath сервера
echo ==============================

REM Проверка, запущен ли контейнер
docker ps | findstr mcp-jsonpath-server >nul 2>&1
if not errorlevel 1 (
    echo ✅ Сервер запущен
    echo.
    echo 📋 Информация о контейнере:
    docker ps --filter "name=mcp-jsonpath-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
    echo.
    echo 🌐 URL сервера: http://localhost:3000
    echo.
    echo 📊 Логи (последние 10 строк):
    docker-compose logs --tail=10
) else (
    echo ⚠️  Сервер не запущен
    echo.
    echo 📋 Информация о контейнерах:
    docker ps -a --filter "name=mcp-jsonpath-server" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    echo.
    echo 💡 Для запуска сервера выполните:
    echo    docker-compose up -d
)