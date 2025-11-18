# GitHub Codespaces Fix Instructions

## Issue Summary
Your application was showing "Failed to fetch" errors because:
1. ❌ Backend URL in frontend/.env had a typo (wrong Codespace name)
2. ❌ Services weren't configured correctly for GitHub Codespaces
3. ❌ Ports may not be set to PUBLIC visibility

## ✅ What's Been Fixed

### 1. Updated Configuration Files
- ✅ `.devcontainer/devcontainer.json` - Corrected paths for brain3 repository
- ✅ `.devcontainer/setup.sh` - Fixed workspace detection and setup process
- ✅ `scripts/start_codespaces.sh` - Enhanced startup script with better environment detection
- ✅ `frontend/.env` - Corrected backend URL to match your Codespace

### 2. Current Status in Test Environment
- ✅ Backend: Running and responding correctly
- ✅ Frontend: Running
- ✅ MongoDB: Running
- ✅ API endpoints tested and working

## 🚀 Next Steps - Apply Fixes to Your Codespace

### Step 1: Commit and Push Changes
In your local terminal or current environment:
```bash
cd /app
git add .
git commit -m "Fix GitHub Codespaces configuration"
git push origin main
```

### Step 2: Restart Your Codespace
In your GitHub Codespace:
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: "Codespaces: Rebuild Container"
3. Select it and wait for rebuild (5-10 minutes)

**OR**

Just pull the latest changes:
```bash
git pull origin main
bash scripts/start_codespaces.sh
```

### Step 3: Make Ports PUBLIC ⚠️ CRITICAL
1. In VS Code, click the **PORTS** tab (bottom panel)
2. Find port **8001** (Backend API)
3. Right-click → **Port Visibility** → **Public**
4. Find port **3000** (Frontend)
5. Right-click → **Port Visibility** → **Public**

**Why?** GitHub Codespaces ports are private by default. Your frontend needs to access the backend via the public URL.

### Step 4: Verify Backend URL
Check that your frontend has the correct backend URL:
```bash
cat frontend/.env
```

Should show:
```
REACT_APP_BACKEND_URL=https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev
```

If the Codespace name is different (if you created a new Codespace), update it:
```bash
# Replace YOUR_CODESPACE_NAME with your actual codespace name from the URL
export CODESPACE_NAME="your-actual-codespace-name"
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=https://\${CODESPACE_NAME}-8001.app.github.dev
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
```

### Step 5: Test the Application

**Test Backend:**
```bash
curl http://localhost:8001/api/
```
Expected output: `{"message":"Hello World"}`

**Test Frontend:**
Open your browser to the frontend URL (in PORTS tab, click the globe icon next to port 3000)

Example: `https://solid-succotash-pj9q755wwr394l4-3000.app.github.dev`

## 📋 Troubleshooting

### Still seeing "Failed to fetch"?

**1. Check Backend is Running:**
```bash
curl http://localhost:8001/api/
```

**2. Check Backend Logs:**
```bash
tail -f /var/log/supervisor/backend.*.log
```

**3. Check Frontend .env:**
```bash
cat frontend/.env
```

**4. Restart Services:**
```bash
bash scripts/start_codespaces.sh
```

### Backend Not Starting?

**Check Error Logs:**
```bash
tail -50 /var/log/supervisor/backend.err.log
```

**Common Issues:**
- Missing Python dependencies: `cd backend && source .venv/bin/activate && pip install -r requirements.txt`
- MongoDB not running: `sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1`

### Frontend Issues?

**Check Frontend Logs:**
```bash
tail -f /var/log/supervisor/frontend.*.log
```

**Reinstall Dependencies:**
```bash
cd frontend
yarn install
```

## 🔧 Manual Startup (Alternative Method)

If the automatic startup doesn't work:

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
PORT=3000 yarn start
```

## ✅ Success Checklist

- [ ] Changes committed and pushed to GitHub
- [ ] Codespace rebuilt or changes pulled
- [ ] Port 8001 set to PUBLIC
- [ ] Port 3000 set to PUBLIC
- [ ] Backend responds to curl test
- [ ] Frontend opens without errors
- [ ] Can upload images without "Failed to fetch" error

## 🎯 What Your Fixed URLs Should Look Like

Based on your Codespace name `solid-succotash-pj9q755wwr394l4`:

- **Frontend:** https://solid-succotash-pj9q755wwr394l4-3000.app.github.dev
- **Backend:** https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev
- **API Docs:** https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev/docs

## 📚 Additional Resources

- [CODESPACES_QUICK_FIX.md](./CODESPACES_QUICK_FIX.md) - Quick troubleshooting steps
- [CODESPACES_SETUP_GUIDE.md](./CODESPACES_SETUP_GUIDE.md) - Complete setup guide
- [CODESPACES_TROUBLESHOOTING.md](./CODESPACES_TROUBLESHOOTING.md) - Detailed troubleshooting

## 🆘 Still Need Help?

If you're still having issues after following these steps:

1. Check that you've made ports PUBLIC (most common issue)
2. Verify the Codespace name matches in frontend/.env
3. Check backend logs for errors
4. Make sure MongoDB is running
5. Try a fresh Codespace rebuild

---

**Note:** The fixes have been tested in the current environment and all APIs are responding correctly. Once you apply these changes to your Codespace and make the ports public, your application should work perfectly!
