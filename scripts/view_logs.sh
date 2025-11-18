#!/bin/bash

# Comprehensive log viewer script
# Shows all application logs in real-time

echo "=========================================="
echo "Application Logs Viewer"
echo "=========================================="
echo ""
echo "Available log files:"
echo "  1. app_events.log     - Main application events"
echo "  2. requests.log       - All HTTP requests/responses"
echo "  3. errors.log         - All errors"
echo "  4. performance.log    - Performance metrics"
echo "  5. backend.err.log    - Backend supervisor errors"
echo "  6. backend.out.log    - Backend supervisor output"
echo "  7. frontend.err.log   - Frontend supervisor errors"
echo "  8. frontend.out.log   - Frontend supervisor output"
echo "  ALL - Show all logs"
echo ""

if [ -z "$1" ]; then
    echo "Usage: bash scripts/view_logs.sh [1-8|ALL] [lines]"
    echo "Example: bash scripts/view_logs.sh 1 50  # Show last 50 lines of app_events.log"
    echo "Example: bash scripts/view_logs.sh ALL   # Show all logs"
    exit 1
fi

LINES=${2:-100}

case $1 in
    1)
        echo "=== APP EVENTS LOG (last $LINES lines) ==="
        tail -n $LINES /var/log/app/app_events.log 2>/dev/null || echo "No logs yet"
        ;;
    2)
        echo "=== REQUESTS LOG (last $LINES lines) ==="
        tail -n $LINES /var/log/app/requests.log 2>/dev/null || echo "No logs yet"
        ;;
    3)
        echo "=== ERRORS LOG (last $LINES lines) ==="
        tail -n $LINES /var/log/app/errors.log 2>/dev/null || echo "No logs yet"
        ;;
    4)
        echo "=== PERFORMANCE LOG (last $LINES lines) ==="
        tail -n $LINES /var/log/app/performance.log 2>/dev/null || echo "No logs yet"
        ;;
    5)
        echo "=== BACKEND ERRORS (last $LINES lines) ==="
        tail -n $LINES /var/log/supervisor/backend.err.log 2>/dev/null || echo "No logs yet"
        ;;
    6)
        echo "=== BACKEND OUTPUT (last $LINES lines) ==="
        tail -n $LINES /var/log/supervisor/backend.out.log 2>/dev/null || echo "No logs yet"
        ;;
    7)
        echo "=== FRONTEND ERRORS (last $LINES lines) ==="
        tail -n $LINES /var/log/supervisor/frontend.err.log 2>/dev/null || echo "No logs yet"
        ;;
    8)
        echo "=== FRONTEND OUTPUT (last $LINES lines) ==="
        tail -n $LINES /var/log/supervisor/frontend.out.log 2>/dev/null || echo "No logs yet"
        ;;
    ALL)
        echo "=== APP EVENTS LOG ==="
        tail -n 30 /var/log/app/app_events.log 2>/dev/null || echo "No logs yet"
        echo ""
        echo "=== RECENT REQUESTS ==="
        tail -n 20 /var/log/app/requests.log 2>/dev/null || echo "No logs yet"
        echo ""
        echo "=== RECENT ERRORS ==="
        tail -n 20 /var/log/app/errors.log 2>/dev/null || echo "No logs yet"
        echo ""
        echo "=== BACKEND STATUS ==="
        tail -n 20 /var/log/supervisor/backend.err.log 2>/dev/null || echo "No logs yet"
        echo ""
        echo "=== FRONTEND STATUS ==="
        tail -n 20 /var/log/supervisor/frontend.err.log 2>/dev/null || echo "No logs yet"
        ;;
    *)
        echo "Invalid option: $1"
        echo "Please use 1-8 or ALL"
        exit 1
        ;;
esac
