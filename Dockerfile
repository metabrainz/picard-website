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
RUN pip install --upgrade pip
COPY uv.lock pyproject.toml /code/website/
RUN uv sync --frozen --group dev

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
RUN uv run pytest

# Cleanup build dependencies
RUN uv pip uninstall flask-testing pytest pytest-cov
RUN rm -rf ./node_modules .pytest_cache .coverage \
    && apt-get purge -y $BUILD_DEPS \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Serve the Flask WSGI app with granian over plain HTTP.
# uwsgi previously exposed the legacy binary protocol on 3031 and plain HTTP on
# 3032; granian is HTTP-only and takes over the service port 3031.
# Invoke granian directly from the venv (not via `uv run`) so no uv cache is
# needed at runtime under the unprivileged www-data user.
# Worker count is overridable at runtime via the GRANIAN_WORKERS env var
# (granian reads GRANIAN_* env vars natively); the reverse proxy/orchestrator
# may prefer 1 worker per container and scaling containers instead.
USER www-data:www-data
ENV GRANIAN_WORKERS=4
# Access logging on by default (granian disables it otherwise). The format
# mirrors uwsgi's log-x-forwarded-for: %(addr)s is the immediate peer (the
# reverse proxy), and xff carries the real client chain from X-Forwarded-For.
# Both are overridable/disableable at runtime via these GRANIAN_* env vars.
ENV GRANIAN_LOG_ACCESS_ENABLED=true
ENV GRANIAN_LOG_ACCESS_FMT="[%(time)s] %(addr)s xff=%(header{x-forwarded-for})s \"%(method)s %(path)s %(protocol)s\" %(status)d %(dt_ms).3f"
EXPOSE 3031
CMD ["/code/website/.venv/bin/granian", \
     "--interface", "wsgi", \
     "--factory", \
     "--host", "0.0.0.0", \
     "--port", "3031", \
     "website.wsgi:create_wsgi_app"]
