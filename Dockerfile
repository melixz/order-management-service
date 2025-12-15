FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir -e .

COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY start.sh ./

RUN chmod +x start.sh

RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["./start.sh"]

