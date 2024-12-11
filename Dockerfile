# Start from a Python base image
FROM python:3.10-slim

# Install tzdata for timezone support and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set Timezone environment variable (can be overridden)
ENV TZ=UTC

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory to /app
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts into the container
COPY ./fonts /fonts
COPY run_status.py .
COPY main.py .
COPY settings.py .
COPY overlay_generator.py .
COPY validate_settings.py .

# Default command to run the script
CMD ["python3", "run_status.py"]
