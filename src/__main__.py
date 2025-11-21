"""Главная функция для старта сервера."""

import uvicorn

from src.core.fastapi import GunicornApplication
from src.core.setting import EnvironmentType, settings


def main() -> None:
    """Точка входа в сервис."""
    if settings.ENVIRONMENT == EnvironmentType.DEVELOPMENT:
        uvicorn.run(
            app="src.core.fastapi.application:get_app",
            workers=settings.WORKERS_COUNT,
            host="127.0.0.1",
            port=settings.PORT,
            reload=True,
            log_level="debug",
            factory=True,
        )
    else:
        GunicornApplication(
            app="src.core.fastapi.application:get_app",
            host="0.0.0.0",  # noqa: S104
            port=settings.PORT,
            workers=settings.WORKERS_COUNT,
            accesslog="-",
            loglevel="info",
            access_log_format='%r "-" %s "-" %Tf',
        ).run()


if __name__ == "__main__":
    main()
