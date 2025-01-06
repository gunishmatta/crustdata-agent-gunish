FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN cp .env.template .env

EXPOSE 8002

CMD ["python", "main.py"]
