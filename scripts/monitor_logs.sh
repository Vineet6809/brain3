#!/bin/bash

# Real-time log monitoring script
# Watches all application logs in real-time

echo "=========================================="
echo "Real-Time Application Log Monitor"
echo "=========================================="
echo "Press Ctrl+C to stop"
echo ""

# Create logs directory if it doesn't exist
mkdir -p /var/log/app

# Touch log files if they don't exist
touch /var/log/app/app_events.log
touch /var/log/app/requests.log
touch /var/log/app/errors.log
touch /var/log/app/performance.log

# Use tail -f to follow multiple log files
tail -f \
    /var/log/app/app_events.log \
    /var/log/app/requests.log \
    /var/log/app/errors.log \
    /var/log/supervisor/backend.err.log \
    /var/log/supervisor/frontend.err.log \
    2>/dev/null
