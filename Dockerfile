# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any are needed)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY *.py ./

# Create directory for certificates (can be mounted as volume)
RUN mkdir -p /app/certs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash pihole && \
    chown -R pihole:pihole /app
USER pihole

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check (optional - checks if the process is running)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ps aux | grep -v grep | grep python || exit 1

# Run the monitor
CMD ["python", "monitor.py"]