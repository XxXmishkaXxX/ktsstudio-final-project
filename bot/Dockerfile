FROM python:3.12-slim

WORKDIR /bot

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://astral.sh/uv/install.sh -o /uv-installer.sh \
    && sh /uv-installer.sh \
    && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

COPY bot/ .
COPY db_core/ .

RUN uv venv
RUN uv sync

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8081

CMD ["uv", "run", "python", "bot/main.py"]

