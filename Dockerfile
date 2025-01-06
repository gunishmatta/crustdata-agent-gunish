FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV SLACK_APP_TOKEN=<your_slack_app_token>
ENV SLACK_TOKEN=<your_slack_token>

CMD ["python", "app.py"]
