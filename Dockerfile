# Use the same base image from your logs
FROM python:3.10-slim

# Set environment variables for clean output and port binding
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    # PATH FIX: This tells Python to treat the server folder as a root package
    PYTHONPATH=/app:/app/server

# Set the working directory to /app
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# EXPOSE the port for documentation/visibility
EXPOSE 7860

# CRITICAL FIX: Point to server/app.py and bind to 0.0.0.0
# We use the folder.file:app syntax because app.py is inside the server directory
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
