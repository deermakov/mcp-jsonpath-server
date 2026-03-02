#!/usr/bin/env python3
"""
MCP-сервер для работы с JSON-файлами через JSONPath
Реализует протокол Model Context Protocol с SSE транспортом
"""

import os
import sys
import logging
from typing import Any, Dict

from mcp.server.sse import SseServerTransport
from mcp.types import JSONRPCError
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, Response
from starlette.requests import Request

from mcp_json_server import MCPJSONPathServer


# Настройка логирования
def setup_logging(log_dir: str = "logs") -> None:
    """Настройка логирования всех операцион"""
    from pathlib import Path
    from datetime import datetime

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


def create_app(server: MCPJSONPathServer) -> Starlette:
    """Создание Starlette приложения для SSE транспорта"""
    logger.info(f"create_app")

    app = Starlette(
        routes=[
            Route("/sse", endpoint=server.handle_sse, methods=["GET", "POST"]),
            Route("/resources", endpoint=server.handle_resources, methods=["GET", "POST"]),
            Mount("/messages/", app=server.sse_transport.handle_post_message),
        ]
    )

    return app


def main():
    """Главная функция запуска сервера"""
    logger.info("Запуск MCP JSONPath сервера")

    server = MCPJSONPathServer(name="jsonpath-server")
    app = create_app(server)

    # Запуск через uvicorn
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3000"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")
    data_dir = os.getenv("DATA_DIR", "data")

    # Обновление конфигурации логирования
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    logger.info(f"Сервер запущен на {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()