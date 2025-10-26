# Multi-stage build for Python + Node.js
FROM node:18-alpine AS node-base

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy Node.js bridge
COPY whatsapp_bridge.js ./

# Python stage
FROM python:3.11-slim

# Install Node.js and system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js dependencies from node-base
COPY --from=node-base /app/node_modules ./node_modules
COPY --from=node-base /app/whatsapp_bridge.js ./

# Copy application files
COPY app.py .
COPY whatsapp_bot.py .
COPY multi_bot.py .
COPY yclients_client.py .

# Create directories for logs and sessions
RUN mkdir -p logs whatsapp-sessions

# Make scripts executable
RUN chmod +x whatsapp_bridge.js

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Expose port (if needed for health checks)
EXPOSE 8000

# Default command - run multi-platform bot
CMD ["python", "multi_bot.py"]
