FROM python:3.10-slim

WORKDIR /app

# Copy the pipeline.py and requirements.txt into the container
COPY app/pipeline.py /app
COPY requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
