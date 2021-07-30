FROM python:3.8-slim
WORKDIR /app
RUN apt-get update && \
    apt-get install gettext python3-cffi libcairo2 libpango-1.0-0 \
    gcc g++ \
    libjpeg62-turbo-dev zlib1g-dev \
    postgresql-client postgresql libpq-dev \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
