FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 8002

CMD ["gunicorn", "-b", "0.0.0.0:8002", "main:app"]
