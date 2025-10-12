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

ARG DATABASE_URL
ARG DJANGO_ADMIN_PREFIX
ARG DJANGO_ALLOWED_HOSTS
ARG DJANGO_DEBUG
ARG DJANGO_SECRET_KEY
ARG DJANGO_SITE_DISPLAY_NAME
ARG DJANGO_SITE_DOMAIN_NAME
ARG SENTRY_DSN

RUN just deploy

EXPOSE 8000

CMD ["just", "prodserve"]
