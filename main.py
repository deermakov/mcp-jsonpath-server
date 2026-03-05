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
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
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

# Limit all tool responses to 500KB
mcp.add_middleware(ResponseLimitingMiddleware(max_size=5_000_000))

def load_json_file(file_path: str) -> Any:
    """
    Загружает JSON-файл по указанному пути

    Args:
        file_path: Путь к JSON-файлу

    Returns:
        Структурированный словарь с данными JSON файла
    """
    logger.info(f"load_json_file(): Попытка загрузки JSON-файла: {file_path}")

    try:
        # Проверка существования файла
        if not os.path.exists(file_path):
            logger.error(f"load_json_file(): Файл не существует: {file_path}")
            return None

        # Проверка, что это файл
        if not os.path.isfile(file_path):
            logger.error(f"load_json_file(): Указанный путь не является файлом: {file_path}")
            return None

        # Чтение файла
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"load_json_file(): Успешно загружен JSON-файл: {file_path}, размер: {len(json.dumps(data))} байт")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"load_json_file(): Ошибка декодирования JSON в файле {file_path}: {e}")
        return None

    except Exception as e:
        logger.exception(f"load_json_file(): Ошибка при чтении файла {file_path}: {e}")
        return None

def get_json_path_value(data: Dict[str, Any], json_path: str) -> Any:
    """
    Получает значение из JSON-данных по jsonPath

    Args:
        data: Данные JSON
        json_path: Путь в формате jsonPath

    Returns:
        Структурированный словарь с результатом поиска
    """
    logger.info(f"get_json_path_value(): Запрос значения по jsonPath: {json_path}")

    try:
        # Нормализация jsonPath: если начинается с "data", заменяем на "$"
        normalized_json_path = json_path
        if json_path.startswith("data"):
            normalized_json_path = "$" + json_path[4:]
            logger.info(f"get_json_path_value(): Нормализация jsonPath: '{json_path}' -> '{normalized_json_path}'")
        
        # Используем jsonpath-ng для парсинга и поиска значения
        jsonpath_expr = ext_parse(normalized_json_path)
        matches = jsonpath_expr.find(data)
        
        if not matches:
            logger.error(f"get_json_path_value(): Значение не найдено по jsonPath: {json_path}")
            return None
        
        # Возвращаем массив всех совпадений
        # result = [match.value for match in matches] # возвращаем МАССИВ найденных результатов !
        result = matches[0].value # возвращаем ПЕРВЫЙ из найденных результатов !
        logger.info(f"get_json_path_value(): Успешно получены значения по jsonPath: {json_path}, count: {len(result)}")
        return result

    except Exception as e:
        logger.exception(f"get_json_path_value(): Ошибка при получении значения по jsonPath {json_path}: {e}")
        return None

@mcp.tool(output_schema={
    "type": "object", 
    "properties": {
        "data": {"type": ["object", "array", "null"]}
    }
})
def read_json_file(file_path: str, json_path: Optional[str] = None) -> dict:
    """
    Читает JSON-файл и возвращает данные по указанному jsonPath

    Args:
        file_path: Путь к JSON-файлу
        json_path: Опциональный jsonPath для получения конкретного значения
                  (например, "user.name" или "items[0].price")

    Returns:
        Структурированный словарь с результатом операции
    """
    logger.info(f"read_json_file(): Запрос на чтение JSON-файла: {file_path}, jsonPath: {json_path}")

    try:
        # Загрузка JSON-файла
        data = load_json_file(file_path)

        # Проверка на None (файл не найден/не является файлом/ошибка)
        if data is None:
            logger.error(f"read_json_file(): load_json_file вернул None для файла: {file_path}")
            return {
                "data": None
            }

        # Если jsonPath не указан или является пустой строкой, возвращаем все данные как есть
        if json_path is None or (isinstance(json_path, str) and json_path.strip() == ""):
            logger.info(f"read_json_file(): jsonPath не указан или пустой, возвращаем загруженные данные (тип: {type(data).__name__})")
            return {
                "data": data
            }

        # Получение значения по jsonPath
        result = get_json_path_value(data, json_path)

        # Добавляем метаданные к результату
        return {
            "data": result
        }

    except Exception as e:
        logger.exception(f"read_json_file(): Критическая ошибка при обработке запроса: {e}")
        return {
            "data": None
        }


@mcp.tool()
def read_json_file_array_size(file_path: str, json_path: str) -> Dict[str, Any]:
    """
    Читает JSON-файл и возвращает размер массива по указанному jsonPath

    Args:
        file_path: Путь к JSON-файлу
        json_path: Обязательный jsonPath для получения массива (например, "items" или "logs")

    Returns:
        Структурированный словарь с результатом операции: {"array_size": N} или {"error": "..."}
    """
    logger.info(f"read_json_file_array_size(): Запрос на получение размера массива из JSON-файла: {file_path}, jsonPath: {json_path}")

    try:
        # Вызываем read_json_file для получения данных
        result = read_json_file(file_path, json_path)

        # Проверяем успешность
        if not result.get("data"):
            return {
                "success": False,
                "data": None,
                "error": result.get("error", "Массив не найден")
            }

        # Проверяем, что результат - список (массив)
        content = result.get("data")
        logger.info(f"debug: {content}")


        if isinstance(content, list):
            array_size = len(content)
            logger.info(f"read_json_file_array_size(): Массив найден по jsonPath: {json_path}, размер массива: {array_size}")
            return {
                "success": True,
                "array_size": array_size
            }
        else:
            return {
                "success": False,
                "error": f"Результат по jsonPath не является массивом, тип: {type(content).__name__}"
            }

    except Exception as e:
        logger.exception(f"read_json_file_array_size(): Критическая ошибка при обработке запроса: {e}")
        return {
            "success": False,
            "error": f"Критическая ошибка: {str(e)}"
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
        logger.exception(f"Ошибка при перечислении JSON-файлов: {e}")
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