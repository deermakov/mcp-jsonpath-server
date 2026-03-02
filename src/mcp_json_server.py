#!/usr/bin/env python3
"""
Класс MCPJSONPathServer для работы с JSON-файлами через JSONPath
Реализует протокол Model Context Protocol с SSE транспортом
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    Tool,
    TextContent,
    JSONRPCError,
    Prompt,
    PromptArgument,
    Resource,
    ResourceTemplate,
    JSONRPCNotification,
    JSONRPCRequest,
    JSONRPCResponse,
)

# JSONRPCErrorCode может быть доступен через JSONRPCError или в другом месте
# Попробуем импортировать из разных мест
try:
    from mcp.types import JSONRPCErrorCode
except ImportError:
    try:
        from mcp.types.jsonrpc import JSONRPCErrorCode
    except ImportError:
        # Если не найден, создадим константы вручную
        # В новых версиях MCP используются другие подходы
        class JSONRPCErrorCode:
            MethodNotFound = -32601
            InvalidRequest = -32600
            InternalError = -32603
            ParseError = -32700

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import StreamingResponse, JSONResponse, Response
from starlette.requests import Request
import jsonpath_ng
import jsonpath_ng.ext


# Настройка логирования
def setup_logging(log_dir: str = "logs") -> None:
    """Настройка логирования всех операцион"""
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    log_file = log_dir_path / f"mcp_server_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class MCPJSONPathServer:
    """Сервер MCP для работы с JSON-файлами"""

    def __init__(self, name: str = "jsonpath-server"):
        logger.info(f"__init__")
        self.name = name
        self.server = Server(name)
        self.sse_transport = SseServerTransport("/messages/")
        self._setup_tools()
        self._setup_prompts()
        self._setup_resources()

    def _setup_tools(self) -> None:
        """Настройка инструментов MCP"""
        logger.info(f"_setup_tools")
        self.server.list_tools_handler = self._list_tools
        self.server.call_tool_handler = self._call_tool

    def _setup_prompts(self) -> None:
        """Настройка промптов MCP"""
        logger.info(f"_setup_prompts")
        self.server.list_prompts_handler = self._list_prompts
        self.server.get_prompt_handler = self._get_prompt

    def _setup_resources(self) -> None:
        """Настройка ресурсов MCP"""
        logger.info(f"_setup_resources")
        self.server.list_resources_handler = self._list_resources
        self.server.read_resource_handler = self._read_resource

    def _list_tools(self) -> List[Tool]:
        """Возвращает список доступных инструментов"""
        logger.info(f"_list_tools")
        tools = [
            Tool(
                name="read_json",
                description="Чтение данных из JSON-файла по указанному пути и JSONPath выражению",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к JSON-файлу"
                        },
                        "json_path": {
                            "type": "string",
                            "description": "JSONPath выражение для выборки данных (например, '$.users[*].name')"
                        }
                    },
                    "required": ["file_path", "json_path"]
                }
            )
        ]
        logger.info(f"Список инструментов: {[tool.name for tool in tools]}")
        return tools

    def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Обработка вызова инструментов"""
        logger.info(f"Вызов инструмента: {name}, аргументы: {arguments}")

        if name == "read_json":
            return self._read_json(arguments)
        else:
            raise JSONRPCError(
                code=JSONRPCErrorCode.MethodNotFound,
                message=f"Неизвестный инструмент: {name}"
            )

    def _read_json(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Чтение данных из JSON-файла по JSONPath"""
        logger.info(f"_read_json")
        file_path = arguments.get("file_path", "")
        json_path = arguments.get("json_path", "")

        logger.info(f"Чтение JSON файла: {file_path}, JSONPath: {json_path}")

        try:
            # Проверка существования файла
            if not os.path.exists(file_path):
                error_msg = f"Файл не найден: {file_path}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"❌ Ошибка: {error_msg}"
                )]

            # Проверка расширения
            if not file_path.lower().endswith('.json'):
                error_msg = f"Файл должен иметь расширение .json: {file_path}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"❌ Ошибка: {error_msg}"
                )]

            # Чтение файла
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"Успешно прочитан файл: {file_path}, размер: {len(json.dumps(data))} байт")

            # Парсинг JSONPath выражения
            try:
                jsonpath_expr = jsonpath_ng.parse(json_path)
                matches = [match.value for match in jsonpath_expr.find(data)]

                if not matches:
                    logger.info(f"JSONPath не нашел совпадений: {json_path}")
                    return [TextContent(
                        type="text",
                        text=f"ℹ️ JSONPath '{json_path}' не нашел совпадений в файле."
                    )]

                # Формирование результата
                result = {
                    "file_path": file_path,
                    "json_path": json_path,
                    "matches_count": len(matches),
                    "data": matches
                }

                logger.info(f"Успешно выполнен JSONPath запрос, найдено совпадений: {len(matches)}")

                return [TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]

            except Exception as e:
                error_msg = f"Ошибка JSONPath выражения: {str(e)}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"❌ Ошибка: {error_msg}"
                )]

        except json.JSONDecodeError as e:
            error_msg = f"Ошибка парсинга JSON: {str(e)}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=f"❌ Ошибка: {error_msg}"
            )]

        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(
                type="text",
                text=f"❌ Ошибка: {error_msg}"
            )]

    def _list_prompts(self) -> List[Prompt]:
        """Возвращает список доступных промптов"""
        logger.info(f"_list_prompts")
        prompts = [
            Prompt(
                name="read_json_help",
                description="Получить справку по использованию инструмента чтения JSON",
                arguments=[
                    PromptArgument(
                        name="file_path",
                        description="Путь к JSON-файлу",
                        required=False
                    )
                ]
            )
        ]
        logger.info(f"Список промптов: {[prompt.name for prompt in prompts]}")
        return prompts

    def _get_prompt(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Получение промпта"""
        logger.info(f"Получение промпта: {name}")

        if name == "read_json_help":
            help_text = """📖 Справка по инструменту чтения JSON

Этот инструмент позволяет читать данные из JSON-файлов с использованием JSONPath выражений.

Параметры:
- file_path (обязательный): Путь к JSON-файлу
- json_path (обязательный): JSONPath выражение для выборки данных

Примеры JSONPath выражений:
- '$' - выбрать весь объект
- '$.users[*].name' - выбрать все имена из массива users
- '$.users[0].name' - выбрать имя первого пользователя
- '$.data.items[*].price' - выбрать все цены из items
- '$.store.book[*].author' - выбрать всех авторов книг

Примеры использования:
1. Чтение всего файла: file_path="data.json", json_path="$"
2. Чтение списка пользователей: file_path="users.json", json_path="$.users[*].name"
3. Чтение конкретного поля: file_path="config.json", json_path="$.database.host"
"""
            return [TextContent(type="text", text=help_text)]

        raise JSONRPCError(
            code=JSONRPCErrorCode.MethodNotFound,
            message=f"Неизвестный промпт: {name}"
        )

    def _list_resources(self) -> List[Resource]:
        """Возвращает список доступных ресурсов"""
        resources = []
        logger.info("Список ресурсов: []")
        return resources

    def _read_resource(self, uri: str) -> str:
        """Чтение ресурса"""
        logger.info(f"_read_resource")
        raise JSONRPCError(
            code=JSONRPCErrorCode.MethodNotFound,
            message=f"Ресурс не найден: {uri}"
        )

    async def handle_sse(self, request: Request):
        """Обработка сообщений через SSE"""

        logger.info(f"handle_sse")

        # Логируем заголовки
        logger.info(f"Headers: {dict(request.headers)}")

        # Логируем параметры запроса (query params)
        logger.info(f"Query Params: {dict(request.query_params)}")

        # Логируем тело запроса
        body = await request.body()
        logger.info(f"Body: {body.decode('utf-8')}")

        async with self.sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as streams:
            await self.server.run(
                streams[0],
                streams[1],
                self.server.create_initialization_options(),
            )
        # Return empty response to avoid NoneType error
        return Response()

    async def handle_resources(self, request: Request):
        """Обработка запросов ресурсов"""
        logger.info(f"handle_resources")
        if request.method == "GET":
            resources = self.server._list_resources()
            return JSONResponse([r.model_dump() for r in resources])
        elif request.method == "POST":
            # Обработка запросов на чтение ресурсов
            data = await request.json()
            uri = data.get("uri")
            if uri:
                content = self.server._read_resource(uri)
                return JSONResponse({"content": content})
        return JSONResponse({"error": "Method not allowed"}, status_code=405)