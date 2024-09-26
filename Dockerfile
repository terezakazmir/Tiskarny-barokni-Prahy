FROM python:3.12-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    echo "cs_CZ.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=cs_CZ.UTF-8 && \
    dpkg-reconfigure locales

ENV LANG=cs_CZ.UTF-8 \
    LC_ALL=cs_CZ.UTF-8 \
    LC_CTYPE=cs_CZ.UTF-8 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


COPY . /app
