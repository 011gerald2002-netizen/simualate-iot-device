FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Flask health endpoint
EXPOSE 8080

# Start Flask + background thread
CMD ["python", "app.py"]
