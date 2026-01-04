# Python 3.12 Alpine image as base (matches README recommendation)
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for building wheels and SQLite support
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    sqlite-dev

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default to running the API; can be overridden by docker-compose command
EXPOSE 8000 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
