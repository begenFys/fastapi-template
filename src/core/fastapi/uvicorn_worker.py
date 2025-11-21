"""Custom GunicornApplication for server FastAPI application."""

from types import ModuleType

from uvicorn_worker import UvicornWorker as BaseUvicornWorker

uvloop: ModuleType | None = None
try:
    import uvloop
except ImportError:
    pass


class UvicornWorker(BaseUvicornWorker):  # type: ignore[misc]
    """Конфигурация для uvicorn-воркеров.

    Этот класс является подклассом UvicornWorker и определяет
    некоторые параметры на уровне класса, так как невозможно
    передать эти параметры через gunicorn.
    """

    CONFIG_KWARGS = {
        "loop": "uvloop" if uvloop is not None else "asyncio",
        "http": "httptools",
        "timeout_keep_alive": 60,
        "lifespan": "on",
        "proxy_headers": True,
    }
