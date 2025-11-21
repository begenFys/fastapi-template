"""Loguru middleware."""

import time
from collections.abc import Callable
from typing import Any
from uuid import uuid4

from fastapi import Request
from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.logger import LOGGER_REQUEST_ID_CTX


class LoguruMiddleware:
    """Loguru middleware."""

    def __init__(
        self,
        app: ASGIApp,
        user_transform_func: Callable[[Any | None], Any] | None = None,
    ) -> None:
        """Инициализация middleware.

        Args:
            app: ASGI-приложение.
            user_transform_func: Функция для преобразования request.user.
        """
        self.app_ = app
        self.user_transform_func = (
            user_transform_func or self.default_user_transform
        )

    @staticmethod
    def default_user_transform(user: Any | None) -> str:
        """Функция по умолчанию для преобразования пользователя.

        Args:
            user: Объект пользователя или None.
        """
        return str(user) if user else "unknown"

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Обработка запроса-ответа сервера."""
        if scope["type"] not in ["http", "https"]:
            await self.app_(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        request_id: str = request.headers.get("X-Request-Id", str(uuid4()))
        token = LOGGER_REQUEST_ID_CTX.set(request_id)
        request_ip = request.client.host if request.client else "unknown"

        # TODO: Auth
        # user = getattr(request, "user", None)
        # request_user = self.user_transform_func(user)

        request_body_length = request.headers.get("Content-Length", 0)
        logger_with_context = logger.bind(
            request_ip=request_ip,
            # request_user=request_user,
            request_method=request.method,
            request_path=request.url.path,
            request_query=request.url.query,
            request_body_length=request_body_length,
        )
        logger_with_context.debug(
            f"[{request_id}] "
            f"REQUEST: method={request.method} path={request.url.path} | "
            f"IP: {request_ip} | "
            f"Request body size: {request_body_length} bytes",
        )

        start_time = time.time()

        # Перехват отправки ответа
        response_body_len = 0
        response_status_code = 500  # По умолчанию, в случае ошибки

        async def send_wrapper(message: Message) -> None:
            nonlocal response_status_code, response_body_len
            if message["type"] in [
                "http.response.start",
                "https.response.start",
            ]:
                response_status_code = message["status"]
            if message["type"] in ["http.response.body", "https.response.body"]:
                response_body_len += len(message.get("body", b""))
            await send(message)

        try:
            await self.app_(scope, receive, send_wrapper)
        except Exception as exc:
            process_time = time.time() - start_time
            logger_with_context.exception(
                f"[{request_id}] "
                f"ERROR: {exc} | "
                f"Processing time: {process_time:.4f} sec.",
            )
            raise exc
        finally:
            LOGGER_REQUEST_ID_CTX.reset(token)
            process_time = time.time() - start_time

        # Логирование ответа
        logger_with_context.debug(
            f"[{request_id}] "
            f"RESPONSE: status_code={response_status_code} | "
            f"Processing time: {process_time:.4f} sec. | "
            f"Response body size: {response_body_len} bytes",
            response_status_code=response_status_code,
        )
