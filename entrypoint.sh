#!/bin/sh

# Generate the crontab file dynamically based on the CRON_SCHEDULE environment variable
echo "$CRON_SCHEDULE python3 /app/app.py >> /var/log/cron.log 2>&1" > /etc/crontabs/root

# Create the log file if it doesn't exist
touch /var/log/cron.log

# Start the cron daemon in the foreground
echo "Starting cron with schedule: $CRON_SCHEDULE"
crond -f -l 2 &
tail -f /var/log/cron.log