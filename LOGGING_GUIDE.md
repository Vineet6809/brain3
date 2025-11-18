# 📊 Comprehensive Logging System Guide

## Overview

Your Image Knowledge Graph application now has enterprise-level logging that tracks every request, error, and performance metric. This guide shows you how to use it effectively.

---

## 🎯 Quick Start

### View All Logs at Once
```bash
bash scripts/view_logs.sh ALL
```

### Monitor Logs in Real-Time
```bash
bash scripts/monitor_logs.sh
```
Press Ctrl+C to stop monitoring.

---

## 📁 Log Files Location

All logs are stored in `/var/log/app/`:

```
/var/log/app/
├── app_events.log      # Main application events
├── requests.log        # All HTTP requests/responses  
├── errors.log          # All errors and exceptions
└── performance.log     # Slow requests (>1 second)
```

**Features:**
- ✅ Automatic rotation at 10MB
- ✅ Keeps 5 backup files
- ✅ JSON format for requests
- ✅ Timestamp on every entry

---

## 🔍 Viewing Logs

### Using the View Logs Script

```bash
bash scripts/view_logs.sh [option] [lines]
```

**Options:**

| Option | Log File | Description |
|--------|----------|-------------|
| `1` | app_events.log | Application startup, shutdown, main events |
| `2` | requests.log | All HTTP requests and responses |
| `3` | errors.log | Error messages and exceptions |
| `4` | performance.log | Slow requests (>1 second) |
| `5` | backend.err.log | Backend supervisor errors |
| `6` | backend.out.log | Backend supervisor output |
| `7` | frontend.err.log | Frontend supervisor errors |
| `8` | frontend.out.log | Frontend supervisor output |
| `ALL` | All logs | Summary of all logs |

**Examples:**

```bash
# View last 50 lines of application events
bash scripts/view_logs.sh 1 50

# View last 100 HTTP requests
bash scripts/view_logs.sh 2 100

# View all errors
bash scripts/view_logs.sh 3

# Get summary of everything
bash scripts/view_logs.sh ALL
```

### Using Standard Linux Commands

```bash
# Tail logs
tail -f /var/log/app/app_events.log

# Search for specific errors
grep "error" /var/log/app/errors.log

# Count requests by status code
grep "status_code" /var/log/app/requests.log | grep -o '"status_code":[0-9]*' | sort | uniq -c

# Find slow requests
cat /var/log/app/performance.log
```

---

## 📝 What Gets Logged

### 1. Application Events (`app_events.log`)

**Startup:**
```
2025-11-18 17:42:53 - app - INFO - ================================================================================
2025-11-18 17:42:53 - app - INFO - FastAPI Application Starting
2025-11-18 17:42:53 - app - INFO - Backend URL: Port 8001
2025-11-18 17:42:53 - app - INFO - MongoDB: image_graph_db
2025-11-18 17:42:53 - app - INFO - CORS Origins: *
2025-11-18 17:42:53 - app - INFO - ================================================================================
```

**Each Request:**
```
2025-11-18 17:43:27 - app - INFO - Incoming request: GET /api/
2025-11-18 17:43:27 - app - INFO - Response: GET /api/ - Status: 200 - Duration: 1.59ms
```

**Shutdown:**
```
2025-11-18 17:42:42 - app - INFO - Application shutting down
2025-11-18 17:42:42 - app - INFO - MongoDB connection closed
```

### 2. Request/Response Logs (`requests.log`)

**Request:**
```json
{
  "type": "request",
  "timestamp": "2025-11-18T17:43:27.628977",
  "method": "GET",
  "url": "http://localhost:8001/api/",
  "path": "/api/",
  "query_params": {},
  "client_host": "127.0.0.1",
  "headers": {
    "host": "localhost:8001",
    "user-agent": "curl/7.88.1",
    "accept": "*/*"
  }
}
```

**Response:**
```json
{
  "type": "response",
  "timestamp": "2025-11-18T17:43:27.630678",
  "method": "GET",
  "path": "/api/",
  "status_code": 200,
  "duration_ms": 1.59,
  "client_host": "127.0.0.1"
}
```

### 3. Error Logs (`errors.log`)

**404 Errors:**
```
2025-11-18 17:45:23 - errors - ERROR - Error response: GET /nonexistent - Status: 404 - Client: 127.0.0.1
```

**500 Errors with Stack Trace:**
```
2025-11-18 17:50:00 - errors - ERROR - Exception in request: POST /api/ingest - Error: Database connection failed
Traceback (most recent call last):
  ...
```

### 4. Performance Logs (`performance.log`)

**Slow Requests (>1 second):**
```json
{
  "type": "slow_request",
  "path": "/api/build-index",
  "method": "POST",
  "duration_ms": 1542.35
}
```

---

## 🚀 Common Use Cases

### 1. Debugging 404 Errors

```bash
# View recent errors
bash scripts/view_logs.sh 3 50

# Search for specific path
grep "404" /var/log/app/errors.log

# See what paths are being requested
grep '"path":' /var/log/app/requests.log | tail -20
```

### 2. Monitoring Performance

```bash
# Check for slow requests
cat /var/log/app/performance.log

# Find average response time
grep "duration_ms" /var/log/app/requests.log | tail -100

# Monitor in real-time during testing
bash scripts/monitor_logs.sh
```

### 3. Tracking Down Crashes

```bash
# Check when app last started/stopped
bash scripts/view_logs.sh 1 100 | grep -E "Starting|shutting down"

# View supervisor logs for crash details
bash scripts/view_logs.sh 5 100

# Check for exceptions
bash scripts/view_logs.sh 3 50
```

### 4. Analyzing User Activity

```bash
# Count requests by endpoint
grep '"path":' /var/log/app/requests.log | cut -d'"' -f4 | sort | uniq -c

# Count requests by client IP
grep '"client_host":' /var/log/app/requests.log | cut -d'"' -f4 | sort | uniq -c

# View recent user activity
bash scripts/view_logs.sh 2 50
```

### 5. Testing New Features

**Terminal 1 - Monitor logs:**
```bash
bash scripts/monitor_logs.sh
```

**Terminal 2 - Test your feature:**
```bash
curl -X POST http://localhost:8001/api/your-endpoint
```

Watch the logs appear in real-time in Terminal 1!

---

## 🔧 Advanced Usage

### Parse JSON Logs with jq

```bash
# Pretty print requests
cat /var/log/app/requests.log | jq .

# Filter by status code
cat /var/log/app/requests.log | grep '"type": "response"' | jq 'select(.status_code >= 400)'

# Calculate average response time
cat /var/log/app/requests.log | grep '"type": "response"' | jq '.duration_ms' | awk '{sum+=$1; n++} END {print sum/n "ms"}'
```

### Custom Log Analysis

```bash
# Count errors by type
grep "ERROR" /var/log/app/errors.log | cut -d'-' -f5 | sort | uniq -c

# Find busiest hours
grep "timestamp" /var/log/app/requests.log | cut -d'T' -f2 | cut -d':' -f1 | sort | uniq -c

# Track specific user's requests
grep '"client_host": "192.168.1.100"' /var/log/app/requests.log
```

---

## 📊 Log Rotation

Logs automatically rotate when they reach 10MB. Here's how it works:

```
app_events.log           # Current log
app_events.log.1         # Previous (most recent backup)
app_events.log.2         # 
app_events.log.3         # 
app_events.log.4         # 
app_events.log.5         # Oldest backup
```

When `app_events.log` reaches 10MB:
1. `.5` is deleted
2. `.4` → `.5`, `.3` → `.4`, etc.
3. Current → `.1`
4. New empty log file created

**Total storage per log type:** ~50-60MB (10MB × 6 files)

---

## 🐛 Troubleshooting

### No Logs Appearing

```bash
# Check if log directory exists and is writable
ls -la /var/log/app/

# Should show something like:
# drwxrwxrwx 2 root root 4096 Nov 18 17:42 .

# If not, fix permissions:
sudo mkdir -p /var/log/app
sudo chmod 777 /var/log/app
```

### Logs Not Updating

```bash
# Check if backend is running
sudo supervisorctl status backend

# If not running:
sudo supervisorctl restart backend

# Check for errors
bash scripts/view_logs.sh 5 50
```

### Can't Read Log Files

```bash
# Fix permissions
sudo chmod 666 /var/log/app/*.log
```

---

## 💡 Tips & Best Practices

1. **Always monitor logs during testing**
   ```bash
   bash scripts/monitor_logs.sh
   ```

2. **Check logs first when debugging**
   ```bash
   bash scripts/view_logs.sh ALL
   ```

3. **Use grep for specific issues**
   ```bash
   grep "error\|ERROR\|fail\|FAIL" /var/log/app/*.log
   ```

4. **Archive old logs before major testing**
   ```bash
   tar -czf logs_backup_$(date +%Y%m%d).tar.gz /var/log/app/*.log
   ```

5. **Clear logs if testing from scratch**
   ```bash
   sudo rm /var/log/app/*.log*
   sudo supervisorctl restart backend
   ```

---

## 📞 Quick Reference Card

```bash
# View everything
bash scripts/view_logs.sh ALL

# Monitor real-time
bash scripts/monitor_logs.sh

# View specific log
bash scripts/view_logs.sh [1-8] [lines]

# Check errors only
bash scripts/view_logs.sh 3

# Check performance
bash scripts/view_logs.sh 4

# Restart services
sudo supervisorctl restart all

# Service status
sudo supervisorctl status
```

---

## 🎓 Understanding Log Levels

| Level | Description | Example |
|-------|-------------|---------|
| **INFO** | Normal operations | "Incoming request: GET /api/" |
| **WARNING** | Something unusual but handled | "Slow request detected" |
| **ERROR** | Something failed | "Database connection failed" |

All levels are logged. Use grep to filter:
```bash
grep "ERROR" /var/log/app/*.log
grep "WARNING" /var/log/app/*.log
```

---

## 🎯 Summary

You now have:
- ✅ Complete request/response logging
- ✅ Automatic error tracking
- ✅ Performance monitoring
- ✅ Easy-to-use viewing scripts
- ✅ Real-time monitoring
- ✅ Automatic log rotation
- ✅ JSON format for easy parsing

**Everything you need to debug and monitor your application!** 🚀
