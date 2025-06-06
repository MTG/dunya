FROM python:3.11 AS base
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_SYSTEM_PYTHON=1
ENV UV_PYTHON_DOWNLOADS=never

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p /etc/apt/keyrings/
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list

RUN apt-get update && apt-get install -y --no-install-recommends \
         cmake \
         libmad0-dev \
         libsndfile1-dev \
         libgd-dev \
         libboost-filesystem-dev \
         libboost-program-options-dev \
         libboost-regex-dev \
         nodejs \
         libsndfile1-dev \
         lame \
         libffi-dev \
      && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

ADD pyproject.toml uv.lock /code/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev --frozen
ENV PATH=/code/.venv/bin:$PATH

ADD package.json package-lock.json /code/
WORKDIR /code
RUN npm install && rm -r ~/.npm

ADD . /code/

FROM base AS dev

RUN --mount=type=cache,target=/root/.cache/uv uv sync --dev --frozen

FROM base AS prod

RUN npm run build

# TODO: Could be made part of the frontend build script
RUN bash build-less.sh

RUN python manage.py collectstatic --settings dunya.build_settings --no-input
