# GitHub Codespaces Setup & 404 Fix Guide

## 🔧 Issues Fixed

### 1. **404 Not Found Errors**
   - **Problem**: Backend was returning 404 for root path `/` and `/favicon.ico`
   - **Root Cause**: 
     - Backend/Frontend services were STOPPED
     - CUDA/torch dependency issues preventing backend startup
     - Made all ML library imports optional to handle missing CUDA libraries
   - **Solution**: Fixed imports in `enhanced_pipeline.py` and restarted services

### 2. **Comprehensive Logging System Setup**
   - **Problem**: No centralized logging to track application events
   - **Solution**: Implemented multi-level logging system

---

## 📊 Logging System

### Log Files Created

All logs are stored in `/var/log/app/`:

| Log File | Purpose | Max Size |
|----------|---------|----------|
| `app_events.log` | Main application events, startup/shutdown | 10MB |
| `requests.log` | All HTTP requests/responses in JSON format | 10MB |
| `errors.log` | All error messages and exceptions | 10MB |
| `performance.log` | Slow requests (>1 second) | 10MB |

**Note**: Logs auto-rotate when they reach 10MB, keeping 5 backup files.

### What Gets Logged

#### Every HTTP Request:
```json
{
  "type": "request",
  "timestamp": "2025-11-18T17:43:27.628977",
  "method": "GET",
  "url": "http://localhost:8001/api/",
  "path": "/api/",
  "query_params": {},
  "client_host": "127.0.0.1",
  "headers": {...}
}
```

#### Every HTTP Response:
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

#### Error Responses (4xx, 5xx):
- Automatically logged to `errors.log` with full details
- Includes request information and error messages

#### Slow Requests (>1 second):
- Automatically logged to `performance.log`
- Helps identify bottlenecks

---

## 🛠️ Log Viewing Scripts

### 1. View Specific Logs
```bash
bash scripts/view_logs.sh [option] [lines]
```

**Options:**
- `1` - App events log
- `2` - Requests log
- `3` - Errors log
- `4` - Performance log
- `5` - Backend supervisor errors
- `6` - Backend supervisor output
- `7` - Frontend supervisor errors
- `8` - Frontend supervisor output
- `ALL` - Show all logs

**Examples:**
```bash
# View last 50 lines of app events
bash scripts/view_logs.sh 1 50

# View all logs (summary)
bash scripts/view_logs.sh ALL

# View last 100 lines of requests
bash scripts/view_logs.sh 2 100
```

### 2. Real-Time Monitoring
```bash
bash scripts/monitor_logs.sh
```
- Watches all log files in real-time
- Shows new entries as they happen
- Press Ctrl+C to stop

---

## 🚀 Current Status

### Services Running:
```
✅ Backend  - Port 8001 (http://0.0.0.0:8001)
✅ Frontend - Port 3000 (http://localhost:3000)
✅ MongoDB  - Port 27017
```

### API Endpoints:
All backend API endpoints are prefixed with `/api`:

- `GET  /api/` - Health check
- `GET  /api/status` - Get status checks
- `POST /api/status` - Create status check
- `POST /api/ingest` - Upload and process image
- `GET  /api/graph` - Get knowledge graph
- `GET  /api/categories` - Get categories
- `GET  /api/connection-types` - Get connection types
- `GET  /api/stats` - Get statistics
- `GET  /api/search` - Search images
- `POST /api/build-index` - Build search index

---

## 🔍 Testing the Fix

### 1. Test Backend Health:
```bash
curl http://localhost:8001/api/
# Expected: {"message":"Hello World"}
```

### 2. View the Request Log:
```bash
bash scripts/view_logs.sh 2 10
```

### 3. Check Application Events:
```bash
bash scripts/view_logs.sh 1 20
```

### 4. Monitor in Real-Time:
```bash
bash scripts/monitor_logs.sh
# Then in another terminal:
curl http://localhost:8001/api/status
# Watch logs appear in real-time
```

---

## 📝 Understanding the 404 Error

### Why You Saw 404 Errors:

1. **Requests to Root Path (`/`)**:
   - Backend doesn't serve anything at root `/`
   - Only `/api/*` endpoints are valid
   - This is by design - frontend should use `/api/` prefix

2. **Requests to `/favicon.ico`**:
   - Browser automatically requests favicon
   - Backend doesn't serve static files
   - This is expected behavior and can be ignored

3. **Services Were Stopped**:
   - Backend was crashing due to CUDA dependencies
   - Frontend was stopped
   - Now both are running correctly

### Current Routing:

```
Frontend (Port 3000) 
    ↓
    Uses REACT_APP_BACKEND_URL from .env
    ↓
Backend (Port 8001)
    ↓
    All routes under /api/*
```

---

## 🔄 Restart Services

If you need to restart:

```bash
# Restart backend only
sudo supervisorctl restart backend

# Restart frontend only  
sudo supervisorctl restart frontend

# Restart all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status
```

---

## 🐛 Troubleshooting

### Backend Won't Start:
```bash
# Check backend logs
tail -n 50 /var/log/supervisor/backend.err.log

# Or use the script
bash scripts/view_logs.sh 5 50
```

### Frontend Won't Start:
```bash
# Check frontend logs
tail -n 50 /var/log/supervisor/frontend.err.log

# Or use the script
bash scripts/view_logs.sh 7 50
```

### No Logs Appearing:
```bash
# Check log directory permissions
ls -la /var/log/app/

# Should be writable
# If not, run:
sudo chmod 777 /var/log/app
```

### Still Seeing 404 Errors:

1. **Check services are running:**
   ```bash
   sudo supervisorctl status
   ```

2. **Verify correct URL in frontend .env:**
   ```bash
   cat /app/frontend/.env
   ```

3. **Test backend directly:**
   ```bash
   curl http://localhost:8001/api/
   ```

4. **Check logs for errors:**
   ```bash
   bash scripts/view_logs.sh ALL
   ```

---

## 📁 Files Created/Modified

### New Files:
- `/app/backend/logging_middleware.py` - Comprehensive logging middleware
- `/app/scripts/view_logs.sh` - Log viewing utility
- `/app/scripts/monitor_logs.sh` - Real-time log monitoring
- `/app/CODESPACES_FIX_README.md` - This guide

### Modified Files:
- `/app/backend/server.py` - Added logging middleware
- `/app/backend/enhanced_pipeline.py` - Fixed CUDA import errors

---

## 💡 Tips

1. **Always check logs first** when debugging issues:
   ```bash
   bash scripts/view_logs.sh ALL
   ```

2. **Monitor logs during testing**:
   ```bash
   # Terminal 1: Monitor logs
   bash scripts/monitor_logs.sh
   
   # Terminal 2: Test your app
   curl http://localhost:8001/api/...
   ```

3. **Logs are rotated automatically** - No need to clean up manually

4. **All 404s are logged** - Easy to spot routing issues

5. **Performance tracking** - Slow requests (>1s) are automatically flagged

---

## 🎯 Next Steps

1. ✅ Services are running
2. ✅ Logging is enabled
3. ✅ 404 issues understood and fixed
4. ➡️ **Test your application in browser**
5. ➡️ **Monitor logs as you test features**
6. ➡️ **Check error logs if issues occur**

---

## 📞 Quick Reference

```bash
# View all logs summary
bash scripts/view_logs.sh ALL

# Real-time monitoring
bash scripts/monitor_logs.sh

# Restart services
sudo supervisorctl restart all

# Check service status
sudo supervisorctl status

# Test backend
curl http://localhost:8001/api/

# View specific log
bash scripts/view_logs.sh [1-8] [lines]
```

---

**All systems are operational! 🚀**
