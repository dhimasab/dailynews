FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy requirements.txt dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file script ke container
COPY . .

# Default command
CMD ["python", "main.py"]
