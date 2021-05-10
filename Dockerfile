FROM python:3.9.5

ARG BUILD_DEPS=" \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    nodejs"

# Configure apt repository for node
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -

RUN apt-get update && \
    apt-get install \
        --no-install-suggests \
        --no-install-recommends \
        -y \
        $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code/website

# Python dependencies
RUN pip install uWSGI==2.0.19.1
COPY ./requirements.txt /code/website
RUN pip install -r requirements.txt

# Node dependencies
COPY ./package.json /code/website
RUN npm install

COPY . /code/website

# Static files
RUN npm run build

# Plugins
RUN ./plugins-generate.py

RUN apt-get update && apt-get purge -y $BUILD_DEPS && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY ./docker/uwsgi.ini /etc/uwsgi/uwsgi.ini
EXPOSE 3031
CMD ["uwsgi", "/etc/uwsgi/uwsgi.ini"]
