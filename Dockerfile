# Base Python image
FROM python:3.12-slim as build

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files for the dependencies installation
COPY requirements.txt /app/

# Install dependencies (using the cache to speed up build if requirements.txt doesn't change)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Create a non-root user for security reasons
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Copy the server script explicitly (ensure it's not overwritten unnecessarily)
COPY server.py /app/server.py

# Expose the port your server will run on
EXPOSE 65432

# Run the application
CMD ["python", "/app/server.py"]
