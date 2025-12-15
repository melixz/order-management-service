# order-management-service

Сервис управления заказами (создание, хранение и обработка заказов) на FastAPI с PostgreSQL, Redis, Kafka и taskiq.

## Особенности

- **JWT-аутентификация**: регистрация и логин пользователя, выдача access-токена.
- **Заказы**: создание, чтение, обновление статуса, выборка заказов пользователя.
- **Кеширование**: заказы читаются из Redis (TTL 5 минут) при повторных запросах.
- **Очереди**: при создании заказа публикуется событие `new_order` в Kafka.
- **Фоновая обработка**: Kafka-консьюмер передаёт заказ в taskiq-задачу `process_order_task`.
- **Rate limiting**: простое ограничение частоты запросов через Redis.

## Быстрый старт

### Требования

- Docker и Docker Compose
- Опционально: `uv` и Python 3.13+ для локального запуска без Docker

### Запуск через Docker

В корне проекта:

```bash
docker-compose up --build
```

После старта:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Локальный запуск (без Docker, при наличии PostgreSQL/Redis/Kafka)

```bash
uv run uvicorn src.order_management_service.main:app --host 0.0.0.0 --port 8000
```

Переменные окружения можно задать через файл `.env` (см. `.env.example`) или напрямую в окружении:

- `DATABASE_URL` — строка подключения к PostgreSQL (asyncpg).
- `REDIS_URL` — URL Redis.
- `KAFKA_BOOTSTRAP_SERVERS` — адрес Kafka-брокера.
- `JWT_SECRET_KEY` — секрет для подписи JWT.

## Структура проекта

```text
order-management-service/
├── src/
│   └── order_management_service/
│       ├── main.py                  # Точка входа FastAPI, подключение роутеров
│       ├── api/                     # API-роутеры
│       │   ├── auth.py              # Регистрация и выдача JWT-токена
│       │   └── orders.py            # Эндпоинты управления заказами
│       ├── core/                    # Инфраструктура
│       │   ├── database.py          # Async SQLAlchemy + PostgreSQL
│       │   ├── settings.py          # Настройки (URL БД, Redis, Kafka, JWT и др.)
│       │   ├── redis.py             # Клиент Redis и утилиты кеша заказов
│       │   ├── kafka.py             # Продюсер Kafka для событий заказов
│       │   ├── tasks.py             # taskiq и задача process_order_task
│       │   ├── security.py          # JWT, хеширование паролей, get_current_user
│       │   └── rate_limiter.py      # Простое rate limiting на Redis
│       ├── models/                  # SQLAlchemy-модели
│       │   ├── user.py              # Модель пользователя
│       │   └── order.py             # Модель заказа + enum статусов
│       ├── repositories/            # Доступ к данным
│       │   ├── user_repository.py   # Репозиторий пользователей
│       │   └── order_repository.py  # Репозиторий заказов
│       ├── services/                # Бизнес-логика
│       │   ├── auth_service.py      # Регистрация, аутентификация
│       │   ├── order_service.py     # CRUD по заказам, кеш, события
│       │   └── order_consumer.py    # Kafka-консьюмер, связанный с taskiq
│       └── schemas/                 # Pydantic-схемы (Pydantic v2)
│           ├── user.py              # Пользователи
│           ├── order.py             # Заказы
│           └── auth.py              # Токены
├── migrations/                      # Alembic-миграции
├── tests/                           # Тесты
│   └── test_health.py               # Health-check
├── Dockerfile                       # Образ приложения
├── docker-compose.yml               # Docker-оркестрация
├── start.sh                         # Стартовый скрипт (ожидание БД + запуск API)
├── pyproject.toml                   # Зависимости
└── README.md
```

## API

### Аутентификация

- `POST /register/`  
  Регистрация пользователя. Тело запроса — `email` и `password`. Возвращает пользователя.

- `POST /token/`  
  OAuth2 Password Flow. Принимает `username` и `password` (как в документации FastAPI), возвращает `access_token`.

### Заказы

- `POST /orders/` — создать заказ (только авторизованные, с rate limiting).  
  Тело: список товаров и `total_price`.  
  Сохраняет заказ в БД, отправляет событие `new_order` в Kafka и кладёт заказ в кеш.

- `GET /orders/{order_id}/` — получить заказ по ID.  
  Сначала ищет в Redis, при отсутствии — читает из БД и кеширует.

- `PATCH /orders/{order_id}/` — обновить статус заказа.  
  При изменении статуса обновляет БД и кеш.

- `GET /orders/user/{user_id}/` — получить заказы пользователя.

## Тестирование

Запуск всех тестов:

```bash
uv run pytest
```
