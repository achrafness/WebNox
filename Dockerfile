# WebNoX - Web Security Training Platform
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite database
RUN mkdir -p instance

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "run.py"]
