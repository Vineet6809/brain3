# 🚨 QUICK FIX - Backend Not Running

## Your Issue
✅ Frontend is running  
❌ Backend is NOT running  
❌ Getting "Failed to fetch" errors

## Quick Fix (Copy & Paste in YOUR Codespace)

### Option 1: Simple Backend Start
```bash
# Go to backend directory
cd /workspaces/brain3/backend

# Create .env file
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

# Start MongoDB
sudo mkdir -p /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1

# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Option 2: Use the Helper Script
```bash
cd /workspaces/brain3
git pull origin main
bash fix_and_start_backend.sh
```

### Option 3: Start Everything
```bash
cd /workspaces/brain3
git pull origin main
bash start_all_services.sh
```

---

## Test Backend

After starting, run this in a NEW terminal:
```bash
curl http://localhost:8001/api/
```

Expected response:
```json
{"message":"Hello World"}
```

---

## Your URLs

Based on your Codespace: `solid-succotash-pj9q755wvvrr394j4`

- **Frontend**: https://solid-succotash-pj9q755wvvrr394j4-3000.app.github.dev
- **Backend**: https://solid-succotash-pj9q755wvvrr394j4-8001.app.github.dev
- **API Docs**: https://solid-succotash-pj9q755wvvrr394j4-8001.app.github.dev/docs

---

## Common Issues

### "pip: command not found"
```bash
python3 -m pip install -r requirements.txt
```

### "Port 8001 already in use"
```bash
sudo fuser -k 8001/tcp
```

### "ModuleNotFoundError"
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Backend exits immediately
Check the error:
```bash
cd backend
source .venv/bin/activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

---

## If Python Dependencies Fail

Some ML libraries might fail in Codespaces. That's OK - the app will work without them (basic features only).

The backend will start even if some optional ML dependencies fail.

---

## Verify Everything Works

1. **Backend Test:**
   ```bash
   curl http://localhost:8001/api/
   ```

2. **Open Frontend:**
   Click the globe icon 🌐 next to port 3000 in PORTS tab

3. **Try Upload:**
   Click "Upload Image" - should work now!

---

## Quick Status Check

```bash
# Check what's running
sudo lsof -i :8001  # Backend
sudo lsof -i :3000  # Frontend
pgrep mongod        # MongoDB
```

All should show processes running.

---

## Need Help?

If backend still won't start, share the error:
```bash
cd /workspaces/brain3/backend
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

Copy and share any error messages!
