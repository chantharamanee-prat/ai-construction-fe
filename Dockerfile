# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Expose port (change if your server uses a different port)
EXPOSE 8000

# Set environment variables (optional, adjust as needed)
ENV PYTHONUNBUFFERED=1

# Start the server (adjust the command as needed for your entrypoint)
CMD ["python", "-m", "server.api"]
