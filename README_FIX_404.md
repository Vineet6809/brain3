# 🔥 IMMEDIATE FIX for 404 Errors in Codespaces

## 🎯 Your Problem

You're getting `{"detail":"Not Found"}` errors because:
1. ❌ Frontend `.env` has Emergent platform URL: `https://workspace-solver.preview.emergentagent.com`
2. ❌ This URL doesn't exist in your Codespace
3. ✅ Your services ARE running (as shown in your screenshot)
4. ✅ You just need to fix the URL configuration

---

## ⚡ FASTEST FIX (30 seconds)

### **Option A: Automated (Recommended)**

```bash
# Run this ONE command:
bash scripts/fix_codespaces_urls.sh
```

Then:
- If services are already running → Just refresh your browser
- If not → Run: `bash scripts/start_codespaces.sh`

### **Option B: Manual (If automated fails)**

**Step 1:** Find your backend URL
- Go to **PORTS** tab in VS Code (bottom panel)
- Find port **8001**
- Right-click → **Copy Local Address**
- It will look like: `https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev`

**Step 2:** Update frontend config
```bash
# Edit this file: /app/frontend/.env
# Replace the REACT_APP_BACKEND_URL line with your URL from Step 1

# Quick command:
nano /app/frontend/.env
```

Change:
```
REACT_APP_BACKEND_URL=https://workspace-solver.preview.emergentagent.com
```

To (use YOUR URL from PORTS tab):
```
REACT_APP_BACKEND_URL=https://YOUR-CODESPACE-8001.app.github.dev
```

**Step 3:** Restart frontend
```bash
# Kill and restart
cd /app/frontend
killall node
PORT=3000 yarn start &
```

**Step 4:** Access your app
- Go to **PORTS** tab
- Click the 🌐 globe icon next to port **3000**

---

## 🧪 Verify It's Working

```bash
# Test 1: Check backend directly
# (Replace with your backend URL from PORTS tab)
curl https://YOUR-CODESPACE-8001.app.github.dev/api/

# Should return: {"message":"Hello World"}

# Test 2: Check if frontend can reach backend
# Open frontend in browser and check browser console (F12)
# Should see successful API calls, not 404 errors
```

---

## 🔍 Understanding the Issue

### **What Was Wrong:**

Your `frontend/.env` file had:
```
REACT_APP_BACKEND_URL=https://workspace-solver.preview.emergentagent.com
```

This is an **Emergent platform URL** that only works when running on their infrastructure.

### **What You Need:**

In GitHub Codespaces, each workspace gets unique URLs:
```
Frontend:  https://{CODESPACE_NAME}-3000.{DOMAIN}
Backend:   https://{CODESPACE_NAME}-8001.{DOMAIN}
```

Example:
```
Frontend:  https://solid-succotash-pj9q755wwr394l4-3000.app.github.dev
Backend:   https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev
```

---

## 📊 Check Your Current Status

### **See what's running:**
```bash
ps aux | grep -E 'mongod|uvicorn|node' | grep -v grep
```

You should see:
- ✅ `mongod` (MongoDB)
- ✅ `uvicorn` (Backend)  
- ✅ `node` (Frontend)

### **Check current .env configuration:**
```bash
cat /app/frontend/.env
```

Should show:
```
REACT_APP_BACKEND_URL=https://{YOUR-CODESPACE}-8001.app.github.dev
```

NOT:
```
REACT_APP_BACKEND_URL=https://workspace-solver.preview.emergentagent.com
```

---

## 🎬 Complete Fresh Start

If you want to start completely fresh:

```bash
# 1. Stop everything
killall mongod node python uvicorn 2>/dev/null

# 2. Fix URLs
bash scripts/fix_codespaces_urls.sh

# 3. Install backend dependencies (if needed)
cd /app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd /app

# 4. Start everything
bash scripts/start_codespaces.sh
```

---

## 🆘 Still Not Working?

### **Issue: "Connection refused" or "502 Bad Gateway"**

**Cause:** Backend not running

**Fix:**
```bash
cd /app/backend
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### **Issue: "MongoDB connection failed"**

**Cause:** MongoDB not started

**Fix:**
```bash
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
```

### **Issue: Ports not visible in PORTS tab**

**Fix:**
1. Open a terminal in VS Code
2. Run: `bash scripts/start_codespaces.sh`
3. VS Code will auto-detect and forward ports
4. Check PORTS tab again

### **Issue: Services won't start - "Address already in use"**

**Fix:**
```bash
# Kill everything on those ports
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:27017 | xargs kill -9 2>/dev/null

# Start fresh
bash scripts/start_codespaces.sh
```

---

## 📚 Additional Resources

- **Quick Start:** See [QUICK_START_CODESPACES.md](./QUICK_START_CODESPACES.md)
- **Full Troubleshooting:** See [CODESPACES_TROUBLESHOOTING.md](./CODESPACES_TROUBLESHOOTING.md)
- **Original Setup:** See [CODESPACES_SETUP_GUIDE.md](./CODESPACES_SETUP_GUIDE.md)

---

## ✅ Success Checklist

- [ ] Ran `bash scripts/fix_codespaces_urls.sh`
- [ ] Verified `/app/frontend/.env` has correct Codespace URL
- [ ] Backend is running (check with `ps aux | grep uvicorn`)
- [ ] Frontend is running (check with `ps aux | grep node`)
- [ ] MongoDB is running (check with `ps aux | grep mongod`)
- [ ] Can access backend: `curl http://localhost:8001/api/`
- [ ] Can open frontend from PORTS tab port 3000
- [ ] No 404 errors in browser console (F12)

---

**🎉 Once all checked, your app should be working!**
