FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install dependencies & cron
RUN pip install --no-cache-dir -r requirements.txt && \
    chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CRON_SCHEDULE="0 */3 * * *"

ENTRYPOINT ["/app/entrypoint.sh"]