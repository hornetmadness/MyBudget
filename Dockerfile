# Builder stage - compile dependencies
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    musl-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install Python dependencies to /build
COPY requirements.txt ./
RUN pip install --no-cache-dir --target /build/deps -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Only install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libffi8 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy precompiled dependencies from builder
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages

# Copy the application code
COPY . .

EXPOSE 8000 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
