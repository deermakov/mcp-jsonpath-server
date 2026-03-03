@echo off
REM Скрипт для запуска MCP-сервера JSON-файлов

echo ======================================
echo Запуск MCP-сервера JSON-файлов
echo ======================================

REM Проверка наличия директорий
if not exist "data" (
    echo Создание директории data...
    mkdir data
)

if not exist "logs" (
    echo Создание директории logs...
    mkdir logs
)

REM Запуск через Docker Compose
echo Запуск контейнера...
docker-compose up -d

echo.
echo ======================================
echo Сервер запущен!
echo ======================================
echo Проверка логов: docker-compose logs -f
echo Остановка сервера: docker-compose down
echo ======================================

pause