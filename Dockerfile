FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (Docker layer caching)
# If pyproject.toml hasn't changed, this layer is cached
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -e "."

# Copy application code
COPY app/ ./app/

# Create non-root user for security
# Running as root inside a container is a security risk
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
