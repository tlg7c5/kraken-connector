# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm AS base-image

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

WORKDIR /workspaces

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential curl gcc wget && \
  pip install --no-cache-dir pdm && \
  rm -rf /var/lib/apt/lists/*

COPY pyproject.toml pdm.lock ./

RUN pdm install --no-self -G dev

FROM python:3.11-slim-bookworm AS final

ENV VIRTUAL_ENV=/workspaces/.venv \
    PATH="/workspaces/.venv/bin:$PATH"

WORKDIR /workspaces
COPY --from=base-image ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app/
CMD [ "sleep", "infinity" ]
