# Complete Replit Setup Guide

## 🚀 Quick Start (You've Already Cloned the Repo)

Since you've already cloned the repository to Replit, follow these steps to get it running:

### Step 1: Configure Replit Files

Make sure these files are in your Replit project root:
- `.replit` (configures how Replit runs your project)
- `replit.nix` (defines system dependencies)
- `scripts/start_replit.sh` (startup script)

These files are already in your repo, so you should be good!

### Step 2: Update Environment Variables

In Replit, you need to set up environment variables. Click on the "Secrets" tab (🔒 icon) in your Replit sidebar and add:

**For Backend:**
- `MONGO_URL` = `mongodb://localhost:27017`
- `DB_NAME` = `image_graph_db`
- `CORS_ORIGINS` = `*`

**Note:** The frontend environment variable `REACT_APP_BACKEND_URL` will be automatically set by the `.replit` file to your Repl's URL.

### Step 3: Update Frontend .env File

You need to update the frontend `.env` file to use the Replit backend URL:

1. In your Replit, open `frontend/.env`
2. Replace the content with:

```env
REACT_APP_BACKEND_URL=https://${REPL_SLUG}.${REPL_OWNER}.repl.co
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

Or if you know your Replit username and project name:
```env
REACT_APP_BACKEND_URL=https://your-repl-name.your-username.repl.co
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### Step 4: Make the Startup Script Executable

In the Replit Shell, run:
```bash
chmod +x scripts/start_replit.sh
```

### Step 5: Click the "Run" Button

Just click the big green "Run" button at the top of your Replit!

The startup script will automatically:
1. Create necessary data directories
2. Start MongoDB
3. Install Python dependencies (this may take 5-10 minutes first time)
4. Download AI models (~1-2GB, one-time download)
5. Start the FastAPI backend on port 8001
6. Install Node.js dependencies
7. Start the React frontend on port 3000

### Step 6: Access Your Application

Once everything is running, Replit will show you a web preview. The frontend should automatically open.

**Important URLs:**
- Frontend: `https://your-repl-name.your-username.repl.co` (main app)
- Backend API: `https://your-repl-name.your-username.repl.co:8001`
- API Docs: `https://your-repl-name.your-username.repl.co:8001/docs`

---

## 🔧 Troubleshooting

### Issue 1: "Port already in use"
**Solution:** Stop the Repl (click Stop button) and start again. Replit will clear the ports.

### Issue 2: "Module not found" or dependency errors
**Solution:** 
1. Open the Shell in Replit
2. For Python dependencies:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. For Node dependencies:
```bash
cd frontend
yarn install
```

### Issue 3: "MongoDB connection failed"
**Solution:**
1. Make sure MongoDB is running:
```bash
ps aux | grep mongod
```
2. If not running, start it manually:
```bash
mkdir -p /tmp/mongodb
mongod --dbpath /tmp/mongodb --bind_ip 127.0.0.1 --port 27017 &
```

### Issue 4: "Backend not responding" or CORS errors
**Solution:**
1. Check if backend is running on port 8001:
```bash
curl http://localhost:8001/api/
```
2. Make sure `REACT_APP_BACKEND_URL` in `frontend/.env` matches your Replit URL
3. Ensure CORS is enabled (check `backend/.env` has `CORS_ORIGINS=*`)

### Issue 5: "Response body is already used" error (The bug you just fixed!)
**Solution:** This has been fixed in the code. Make sure you:
1. Have the latest version with the JSON response fixes
2. Backend returns proper JSON for all endpoints
3. Frontend has proper error handling with `response.ok` checks

### Issue 6: Heavy ML dependencies failing to install
**Solution:**
The app has optional ML dependencies. If torch/transformers fail:
1. Comment out heavy dependencies in `backend/requirements.txt`:
```
# sentence-transformers>=2.2.0
# transformers>=4.30.0
# torch>=2.0.0
# faiss-cpu>=1.7.4
# easyocr>=1.7.0
```
2. Basic image upload will still work with OCR and basic processing

---

## 📝 Alternative Manual Setup (If Automatic Doesn't Work)

If the automatic startup script doesn't work, you can run services manually:

### Terminal 1 - Start MongoDB:
```bash
mkdir -p /tmp/mongodb
mongod --dbpath /tmp/mongodb --bind_ip 127.0.0.1 --port 27017
```

### Terminal 2 - Start Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Terminal 3 - Start Frontend:
```bash
cd frontend
yarn install
PORT=3000 yarn start
```

---

## ✅ Verification Steps

After setup, verify everything is working:

### 1. Check Backend Health:
```bash
curl http://localhost:8001/api/
```
Should return: `{"status":"ok"}`

### 2. Check MongoDB:
```bash
mongosh --eval "db.version()"
```
Should show MongoDB version

### 3. Check Frontend:
Open the Replit webview - you should see the 3D graph interface

### 4. Test Image Upload:
1. Click "Upload Image" button
2. Select a test image
3. Check if it appears in the graph

---

## 🎯 Key Configuration Files Summary

**`.replit`** - Tells Replit what command to run:
```
run = "bash scripts/start_replit.sh"
```

**`replit.nix`** - System dependencies (Tesseract, MongoDB, Python, Node.js)

**`backend/.env`** - Backend configuration:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
```

**`frontend/.env`** - Frontend configuration:
```
REACT_APP_BACKEND_URL=https://your-repl.repl.co
WDS_SOCKET_PORT=443
```

---

## 💡 Tips for Replit

1. **First run takes 5-10 minutes** - AI models need to download
2. **Free tier has RAM limits** - Process images one at a time
3. **Use the Shell** - Great for debugging and manual commands
4. **Always Awake** - Enable "Always On" (paid feature) for production use
5. **Check Logs** - Use the Console tab to see backend/frontend logs

---

## 🆘 Still Need Help?

1. Check the full documentation: `replitinstruction.md`
2. Review the main README: `README.md`
3. Check backend logs in the Replit Console
4. Verify all files are properly uploaded to Replit

---

## 📚 Quick Reference Commands

```bash
# Check what's running
ps aux | grep -E "mongod|uvicorn|node"

# Check ports
netstat -tulpn | grep LISTEN

# Restart everything
pkill -f mongod; pkill -f uvicorn; pkill -f node
bash scripts/start_replit.sh

# Test backend
curl http://localhost:8001/api/stats

# View backend logs (if running in background)
tail -f nohup.out
```

Good luck! 🚀
