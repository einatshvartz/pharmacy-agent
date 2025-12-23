# Dockerfile
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /app/app
COPY test_tools.py /app/test_tools.py
COPY README.md /app/README.md
COPY EVALUATION.md /app/EVALUATION.md

# Expose the API port (match your uvicorn port)
EXPOSE 8002

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
