FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto "=https" --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

COPY pyproject.toml uv.lock justfile ./

RUN just syncprod

COPY . .

ENV PYTHONUNBUFFERED=1



COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN just deploy

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
