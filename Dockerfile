# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy application code
COPY . .

# Expose Flask app port
EXPOSE 5001

# Environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV QDRANT_HOST=qdrant
ENV QDRANT_PORT=6333

# Command to run the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "main:app"]
