FROM python:3.10-alpine as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5001

ENV FLASK_APP=main.py \
    FLASK_RUN_HOST=0.0.0.0 \
    QDRANT_HOST=qdrant \
    QDRANT_PORT=6333

CMD ["gunicorn", "-b", "0.0.0.0:5001", "main:app"]
