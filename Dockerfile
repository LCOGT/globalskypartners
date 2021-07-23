FROM python:3.8-alpine

# Set working directory
WORKDIR /app

# Install runtime dependencies, build dependencies, Python dependencies, and
# then remove build dependencies to keep the image as small as possible
COPY requirements.txt /app/requirements.txt

RUN pip3 install -U pip
RUN apk --no-cache add libffi libpng postgresql-client postgresql-libs zlib cairo-dev pango-dev gdk-pixbuf \
        && apk --no-cache add --virtual .build-deps gcc libffi-dev make musl-dev postgresql-dev libjpeg-turbo-dev libpng-dev zlib-dev g++ \
        && pip3 --no-cache-dir install -r requirements.txt \
        && apk --no-cache del .build-deps

# Install application
COPY . /app
