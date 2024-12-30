FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Create temp directory
RUN mkdir -p temp

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "-u", "bot.py"]
