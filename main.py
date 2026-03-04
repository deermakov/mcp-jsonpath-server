"""
MCP-сервер для работы с JSON-файлами
Реализует tool для запроса данных из JSON-файлов с использованием jsonPath
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from pathlib import Path

from fastmcp import FastMCP, settings
from jsonpath_ng import parse
from jsonpath_ng.ext import parse as ext_parse

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/mcp_json_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создание MCP-сервера
mcp = FastMCP("mcp-json")

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Загружает JSON-файл по указанному пути

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Словарь с данными из JSON или None при ошибке
    """
    logger.info(f"Попытка загрузки JSON-файла: {file_path}")

    try:
        # Проверка существования файла
        if not os.path.exists(file_path):
            logger.error(f"Файл не существует: {file_path}")
            return None

        # Проверка, что это файл
        if not os.path.isfile(file_path):
            logger.error(f"Указанный путь не является файлом: {file_path}")
            return None

        # Чтение файла
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Успешно загружен JSON-файл: {file_path}, размер: {len(json.dumps(data))} байт")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return None

def get_json_path_value(data: Dict[str, Any], json_path: str) -> Any:
    """
    Получает значение из JSON-данных по jsonPath

    Args:
        data: Данные JSON
        json_path: Путь в формате jsonPath

    Returns:
        Значение по указанному пути или None
    """
    logger.info(f"Запрос значения по jsonPath: {json_path}")

    try:
        # Используем jsonpath-ng для парсинга и поиска значения
        jsonpath_expr = ext_parse(json_path)
        matches = jsonpath_expr.find(data)
        
        if not matches:
            logger.error(f"Значение не найдено по jsonPath: {json_path}")
            return None
        
        # Возвращаем массив всех совпадений
        result = [match.value for match in matches]
        logger.info(f"Успешно получены значения по jsonPath: {json_path}, count: {len(result)}")
        return result

    except Exception as e:
        logger.error(f"Ошибка при получении значения по jsonPath {json_path}: {e}")
        return None

@mcp.tool()
def read_json_file(file_path: str, json_path: Optional[str] = None) -> Any:
    """
    Читает JSON-файл и возвращает данные по указанному jsonPath

    Args:
        file_path: Путь к JSON-файлу
        json_path: Опциональный jsonPath для получения конкретного значения
                  (например, "user.name" или "items[0].price")

    Returns:
        Словарь с результатом операции
    """
    logger.info(f"Запрос на чтение JSON-файла: {file_path}, jsonPath: {json_path}")

    try:
        # Загрузка JSON-файла
        data = load_json_file(file_path)

        if data is None:
            return None

        # Если jsonPath не указан, возвращаем все данные
        if json_path is None:
            logger.info("jsonPath не указан, возвращаем все данные")
            return data

        # Получение значения по jsonPath
        result = get_json_path_value(data, json_path)

        if result is None:
            return None

        return result

    except Exception as e:
        logger.error(f"Критическая ошибка при обработке запроса: {e}")
        return {
            "success": False,
            "error": f"Критическая ошибка: {str(e)}",
            "file_path": file_path,
            "json_path": json_path
        }

@mcp.tool()
def list_json_files(directory: str) -> Dict[str, Any]:
    """
    Перечисляет все JSON-файлы в указанной директории

    Args:
        directory: Путь к директории для поиска JSON-файлов

    Returns:
        Словарь с результатом операции
    """
    logger.info(f"Запрос на перечисление JSON-файлов в директории: {directory}")

    try:
        json_files = []

        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Директория не существует: {directory}",
                "directory": directory
            }

        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Указанный путь не является директорией: {directory}",
                "directory": directory
            }

        # Поиск всех JSON-файлов
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    json_files.append(file_path)

        logger.info(f"Найдено {len(json_files)} JSON-файлов в директории: {directory}")

        return {
            "success": True,
            "files": json_files,
            "count": len(json_files),
            "directory": directory
        }

    except Exception as e:
        logger.error(f"Ошибка при перечислении JSON-файлов: {e}")
        return {
            "success": False,
            "error": f"Ошибка: {str(e)}",
            "directory": directory
        }

if __name__ == "__main__":
    logger.info("Запуск MCP-сервера JSON-файлов")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3000"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")

    # Обновление конфигурации логирования
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    logger.info(f"Сервер запущен на {host}:{port}")
    
    # Запуск сервера через FastMCP
    settings.host = host
    settings.port = port
    mcp.run(transport="streamable-http")