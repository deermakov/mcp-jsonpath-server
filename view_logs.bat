@echo off
REM Скрипт для просмотра логов MCP JSONPath сервера

echo 📋 Логи MCP JSONPath сервера
echo ============================

REM Проверка, запущен ли контейнер
docker ps | findstr mcp-jsonpath-server >nul 2>&1
if not errorlevel 1 (
    echo Просмотр логов в реальном времени (Ctrl+C для выхода):
    echo.
    docker-compose logs -f
) else (
    echo ⚠️  Контейнер не запущен
    echo.
    echo Просмотр последних логов:
    docker-compose logs --tail=50
)