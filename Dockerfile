# 1. Start with a lightweight Linux + Python 3.11 base image
FROM python:3.11-slim

# 2. Set environment variables
# (Python won't create .pyc files, and logs will output immediately)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies (needed for Postgres)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copy the rest of your project code
COPY . /app/