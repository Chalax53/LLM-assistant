# Use an official Python runtime as the base image
FROM python:3.13.2-slim

# Set working directory in the container
WORKDIR /app

# Install Tesseract OCR and its dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000 8080

# Command to run the application
CMD ["python", "main.py"]