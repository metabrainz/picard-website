FROM python:3.12-slim-bookworm

ARG BUILD_DEPS=" \
    curl \
    git \
    gcc g++ make \
    "

RUN apt-get update && \
    apt-get install \
        --no-install-suggests \
        --no-install-recommends \
        -y \
        $BUILD_DEPS

# Install nvm
SHELL ["/bin/bash", "--login", "-c"]
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install nodejs & npm
RUN nvm install --lts && npm install -g npm@latest

WORKDIR /code/website

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Python dependencies
RUN pip install --upgrade pip \
    && pip install uWSGI==2.0.23
COPY uv.lock pyproject.toml /code/website/
RUN uv sync --frozen --extra dev

# Node dependencies
COPY ./package.json /code/website/
RUN npm install

COPY website /code/website/website/
COPY run.py plugins-generate.py pytest.ini /code/website/

# Static files
RUN npm run build

# Plugins
RUN mkdir /code/plugins && chown www-data:www-data /code/plugins
USER www-data:www-data
RUN UV_NO_CACHE=1 uv run ./plugins-generate.py

USER root
RUN python -m pytest

COPY ./docker/uwsgi.ini /etc/uwsgi/uwsgi.ini

# Cleanup build dependencies
RUN uv pip uninstall flask-testing pytest pytest-cov
RUN rm -rf ./node_modules .pytest_cache .coverage \
    && apt-get purge -y $BUILD_DEPS \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3031
CMD ["uwsgi", "/etc/uwsgi/uwsgi.ini"]
