
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /app

COPY requirements.txt .

# install OS-level build dependencies
RUN apt-get -y update \
    && apt-get -y install \
      gcc \
      g++ \
      gfortran \
      libffi-dev \
      libjpeg-dev \
      libpng-dev \
      postgresql-client postgresql libpq-dev \
      libpango1.0-dev python3-cffi python3-cairocffi libglib2.0-dev \
      make \
    && pip3 --no-cache-dir install -r requirements.txt \
    && apt-get -y clean

# Install application
COPY . /app
