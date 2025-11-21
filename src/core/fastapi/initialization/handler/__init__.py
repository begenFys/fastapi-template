"""FastAPI handler exceptions."""

from .custom_http_exception import init_orjson_for_custom_http_exception
from .exception import init_orjson_for_exception
from .httpx_exception import init_orjson_for_httpx_exception
from .sqlalchemy_exception import init_orjson_for_sqlalchemy_exception

__all__ = [
    "init_orjson_for_httpx_exception",
    "init_orjson_for_custom_http_exception",
    "init_orjson_for_exception",
    "init_orjson_for_sqlalchemy_exception",
]
