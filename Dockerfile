# Python 3.12 Debian Slim image (better compatibility than Alpine)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for building wheels and SQLite support
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    musl-dev \
    libffi-dev \
    openssl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default to running the API; can be overridden by docker-compose command
EXPOSE 8000 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
