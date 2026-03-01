@echo off
REM Скрипт для запуска MCP JSONPath Server

echo ========================================
echo Запуск MCP JSONPath Server
echo ========================================
echo.

REM Проверка наличия виртуального окружения
if not exist "venv" (
    echo Виртуальное окружение не найдено. Создание...
    python -m venv venv
    echo.
    echo Активация виртуального окружения...
    call venv\Scripts\activate
    echo.
    echo Установка зависимостей...
    pip install -r requirements.txt
    echo.
) else (
    echo Активация виртуального окружения...
    call venv\Scripts\activate
    echo.
)

REM Запуск сервера
echo Запуск сервера...
python src\server.py

pause