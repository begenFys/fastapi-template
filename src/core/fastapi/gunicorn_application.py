"""Custom GunicornApplication for server FastAPI application."""

from typing import Any, cast

from gunicorn.app.base import BaseApplication
from gunicorn.util import import_app


class GunicornApplication(BaseApplication):  # type: ignore
    """Кастомное gunicorn приложение.

    Этот класс использует базовый класс gunicorn
    с кастомными uvicorn-воркерами.
    """

    def __init__(
        self,
        app: str,
        host: str,
        port: int,
        workers: int,
        worker_class: str = "src.core.fastapi.UvicornWorker",
        timeout: int = 60,
        graceful_timeout: int = 30,
        max_requests: int = 10000,
        max_requests_jitter: int = 1000,
        **kwargs: Any,
    ):
        self.options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": worker_class,
            "timeout": timeout,
            "graceful_timeout": graceful_timeout,
            "max_requests": max_requests,
            "max_requests_jitter": max_requests_jitter,
            **kwargs,
        }
        self.app = app
        super().__init__()

    def load_config(self) -> None:
        """Загрузка конфигурации для веб-сервера.

        Эта функция используется для установки параметров
        основному процессу gunicorn. Она устанавливает только те параметры,
        которые может обрабатывать gunicorn. Если передать ей неизвестный
        параметр, она завершится с ошибкой.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self) -> str:
        """Загрузка текущего приложения.

        Gunicorn загружает приложение на основе возвращаемого
        значения этой функции. Мы возвращаем путь в python к
        фабрике приложения.

        Returns:
            Путь в python к фабрике приложения.
        """
        return cast(str, import_app(self.app))
