# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for logs
RUN mkdir -p /app/logs /app/whatsapp-sessions

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app

# Make start script executable
RUN chmod +x /app/start_bots.sh

USER botuser

# Expose port (if needed for health checks)
EXPOSE 8000

# Run both bots using bash script
CMD ["/app/start_bots.sh"]
