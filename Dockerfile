# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libglib2.0-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# For development we use Django's runserver command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
