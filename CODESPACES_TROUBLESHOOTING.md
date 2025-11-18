# 🔧 GitHub Codespaces Troubleshooting Guide

## Problem: 404 Errors in Codespaces

You're seeing `{"detail":"Not Found"}` errors because the application is still configured for the Emergent platform instead of GitHub Codespaces.

---

## ✅ Quick Fix (Option 1 - Recommended)

### **Use the Automated Startup Script**

```bash
# Stop any currently running services
killall node python uvicorn 2>/dev/null

# Run the Codespaces startup script
bash scripts/start_codespaces.sh
```

This script will:
- ✅ Start MongoDB
- ✅ Auto-detect your Codespace URL
- ✅ Update both frontend and backend `.env` files
- ✅ Start both services with correct configuration

---

## 🔍 Manual Fix (Option 2)

If the automated script doesn't work, follow these steps:

### **Step 1: Get Your Codespace URLs**

In GitHub Codespaces, your forwarded port URLs follow this pattern:
```
https://{CODESPACE_NAME}-{PORT}.{GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}
```

**Find your URLs:**
1. In VS Code, go to the **PORTS** tab (usually bottom panel)
2. You should see ports **3000** (Frontend) and **8001** (Backend)
3. Right-click on port **8001** → **Copy Local Address**

### **Step 2: Update Frontend Configuration**

Edit `/app/frontend/.env`:
```bash
REACT_APP_BACKEND_URL=https://YOUR-CODESPACE-NAME-8001.app.github.dev
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

**Replace** `YOUR-CODESPACE-NAME-8001.app.github.dev` with your actual backend URL from the PORTS tab.

### **Step 3: Update Backend Configuration** (if needed)

Verify `/app/backend/.env` has:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
```

### **Step 4: Restart Services**

```bash
# Kill existing processes
killall node python uvicorn 2>/dev/null

# Start MongoDB
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1

# Start Backend (in background)
cd /app/backend
source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
cd /app

# Wait for backend
sleep 5

# Start Frontend (in background)
cd /app/frontend
yarn install
PORT=3000 yarn start &
cd /app
```

### **Step 5: Access Your Application**

1. Go to **PORTS** tab in VS Code
2. Find port **3000** (Frontend)
3. Click the 🌐 globe icon to open in browser

---

## 🐛 Common Issues

### **Issue 1: "502 Bad Gateway" or "Connection Refused"**
**Cause:** Backend not running or not accessible

**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# Check backend logs
tail -f /app/backend/uvicorn.log

# Restart backend
cd /app/backend
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### **Issue 2: "404 Not Found" for API calls**
**Cause:** Wrong backend URL in frontend

**Solution:**
1. Check your backend URL in PORTS tab
2. Update `/app/frontend/.env` with correct URL
3. Restart frontend: `cd /app/frontend && yarn start`

### **Issue 3: MongoDB Connection Error**
**Cause:** MongoDB not running

**Solution:**
```bash
# Start MongoDB
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1

# Verify MongoDB is running
ps aux | grep mongod
```

### **Issue 4: Port Already in Use**
**Cause:** Previous process still running

**Solution:**
```bash
# Kill all node/python processes
killall node python uvicorn

# Or find and kill specific port
lsof -ti:3000 | xargs kill -9
lsof -ti:8001 | xargs kill -9

# Restart services
bash scripts/start_codespaces.sh
```

---

## 📊 Verify Everything is Working

### **Test Backend (in terminal):**
```bash
# From PORTS tab, copy your backend URL, then:
curl https://YOUR-CODESPACE-NAME-8001.app.github.dev/api/

# Should return: {"message":"Hello World"}
```

### **Test Frontend:**
1. Open frontend URL from PORTS tab (port 3000)
2. You should see "Image Knowledge Graph" interface
3. Try clicking "Build Index" - should not show 404 error

---

## 🔑 Key Differences: Emergent vs Codespaces

| Feature | Emergent Platform | GitHub Codespaces |
|---------|------------------|-------------------|
| Backend URL | Pre-configured external URL | Dynamic per-codespace URL |
| Port Forwarding | Automatic via Kubernetes | Manual via Codespaces |
| MongoDB | Pre-configured | Need to start manually |
| Environment | Production-ready | Development environment |
| `.env` Updates | Not needed | Required for each codespace |

---

## 💡 Best Practice for Codespaces

**Always use the startup script:**
```bash
bash scripts/start_codespaces.sh
```

This ensures all URLs are correctly configured automatically!

---

## Need More Help?

If you're still experiencing issues after following this guide:

1. **Check Service Status:**
   ```bash
   ps aux | grep -E 'mongod|uvicorn|node'
   ```

2. **Check Logs:**
   ```bash
   # MongoDB logs
   tail -f /var/log/mongodb.log
   
   # Backend logs (if running in background)
   tail -f /app/backend/uvicorn.log
   ```

3. **Verify Port Visibility:**
   - In PORTS tab, ensure ports are set to **Public** (not Private)
   - Right-click port → Port Visibility → Public
