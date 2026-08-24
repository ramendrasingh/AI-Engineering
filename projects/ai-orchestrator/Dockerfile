FROM python:3.12-slim

# Prevent Python from writing .pyc files
# and enable unbuffered logging.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first.
# This allows Docker to cache this layer.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and knowledge base.
COPY app ./app
COPY knowledge ./knowledge

# If your application needs scripts during runtime,
# copy them as well.
COPY scripts ./scripts

# Expose FastAPI port.
EXPOSE 8000

# Start FastAPI.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]