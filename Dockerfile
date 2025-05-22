FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (e.g., sqlite3 CLI)
RUN apt-get update && apt-get install -y sqlite3 bash && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Define volume for uploaded images
VOLUME ["/app/static/image/photo/"]

# Set default command
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8080"]
