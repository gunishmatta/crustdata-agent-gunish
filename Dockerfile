# Use an official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY app/pipeline.py /app
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the app port
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
