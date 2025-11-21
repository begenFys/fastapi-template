# fastapi-template

**Database:** PostgreSQL

**Creator:** [@begenFys](https://t.me/begenFys)

**Creator's channel:** [@begenFys_life](https://t.me/begenFys_life)

## 🔧 Локальное окружение
- Заполнить env файл:
```shell
cp .env.dev.example .env.dev
```

- Установить зависимости:
```shell
make sync
```

- Основные команды разработки:
Все команды видны через:
```shell
make help
```

- Локальный запуск приложения:
```shell
make start
```

## 🐋 Docker окружение
- Создать файл окружения:
```shell
cp .env.test.example .env.test
```

- Запустить:
```shell
make dc-start-test
```

- Остановить:
```shell
make dc-rm-test
```

## 🚀 Production
- Подготовить окружение:
```shell
cp .env.prod.example .env.prod
```

- Запуск prod-стека:
```shell
make dc-start-prod
```
