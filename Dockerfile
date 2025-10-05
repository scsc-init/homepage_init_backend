FROM python:3.12-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /uvx /bin/

RUN apt-get update && apt-get install -y sqlite3 bash && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
