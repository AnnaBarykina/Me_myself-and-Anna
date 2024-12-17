# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client and psycopg2-binary
RUN apt-get update && apt-get install -y libpq-dev \
    && pip install psycopg2-binary \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . /app/

# Install PostgreSQL client
# RUN pip install psycopg2-binary
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && pip install psycopg2-binary \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]