# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm AS base-image

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  POETRY_VERSION=1.6.1 \
  POETRY_HOME=/opt/poetry \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_NO_CACHE=1

ENV PATH="$POETRY_HOME/bin:$PATH"
WORKDIR /workspaces

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential curl gcc wget
  # install Poetry
RUN curl -sSL https://install.python-poetry.org | python \
  # cleanup
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --with dev

FROM python:3.11-slim-bookworm AS final

ENV VIRTUAL_ENV=/workspaces/.venv \
    PATH="/workspaces/.venv/bin:$PATH"

WORKDIR /workspaces
COPY --from=base-image ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app/
CMD [ "sleep", "infinity" ]
