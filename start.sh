#!/bin/bash

# Скрипт для запуска MCP-сервера JSON-файлов

echo "======================================"
echo "Запуск MCP-сервера JSON-файлов"
echo "======================================"

# Проверка наличия директорий
if [ ! -d "data" ]; then
    echo "Создание директории data..."
    mkdir -p data
fi

if [ ! -d "logs" ]; then
    echo "Создание директории logs..."
    mkdir -p logs
fi

# Запуск через Docker Compose
echo "Запуск контейнера..."
docker-compose up -d

echo ""
echo "======================================"
echo "Сервер запущен!"
echo "======================================"
echo "Проверка логов: docker-compose logs -f"
echo "Остановка сервера: docker-compose down"
echo "======================================"