FROM python:3.8-alpine

# Set working directory
WORKDIR /app

# Install runtime dependencies, build dependencies, Python dependencies, and
# then remove build dependencies to keep the image as small as possible
COPY requirements.txt /app/requirements.txt

RUN apk --no-cache add libffi libpng postgresql-client postgresql-libs zlib \
        && apk --no-cache add --virtual .build-deps gcc libffi-dev make musl-dev postgresql-dev g++ \
        && pip --no-cache-dir install -r requirements.txt \
        && apk --no-cache del .build-deps

# Install application
COPY . /app
