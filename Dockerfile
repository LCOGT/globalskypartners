FROM python:3.8-slim-buster
WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install gettext python3-cffi  \
    gcc g++ \
    libjpeg62-turbo-dev zlib1g-dev \
    postgresql-11 libpq-dev \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y \
    && python3 -m pip install -r requirements.txt \
    && apt-get -y clean

COPY . /app
