# Stage 1: Build stage
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    gcc \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set default timezone to UTC if TZ is not set
ARG DEFAULT_TZ=UTC
ENV TZ=${TZ:-$DEFAULT_TZ}

# Configure timezone with fallback
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy fonts and application source code
COPY ./fonts /fonts
COPY . .

# Stage 2: Runtime stage
FROM python:3.10-slim

# Set default timezone to UTC if TZ is not set
ARG DEFAULT_TZ=UTC
ENV TZ=${TZ:-$DEFAULT_TZ}

# Configure timezone with fallback
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /install /usr/local
COPY ./fonts /fonts
COPY . .

# Default entrypoint
ENTRYPOINT ["python3", "run_status.py"]
