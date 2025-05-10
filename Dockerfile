# Use slim Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies (optional but common)
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (Optional: only if using Django static)
# RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "UserManagement.wsgi:application"]

