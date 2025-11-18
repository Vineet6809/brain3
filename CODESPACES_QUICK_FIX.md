# Quick Fix for GitHub Codespaces Issues

## Problem: "Failed to fetch" error in frontend

### Solution

**Step 1: Stop any running processes**
```bash
sudo fuser -k 8001/tcp
sudo fuser -k 3000/tcp
```

**Step 2: Start the application**
```bash
bash scripts/start_codespaces.sh
```

**Step 3: Make ports PUBLIC**
1. Click the **PORTS** tab in VS Code (bottom panel)
2. Find ports **3000** and **8001**
3. Right-click each port → **Port Visibility** → **Public**

**Step 4: Test the backend**
```bash
curl http://localhost:8001/api/
```

You should see: `{"message":"Hello World"}`

**Step 5: Access the frontend**

Open the frontend URL (will be in PORTS tab next to port 3000)

Example: `https://your-codespace-name-3000.app.github.dev`

---

## Still Having Issues?

### Check Backend Logs
```bash
tail -f backend.log
```

### Check Frontend Logs
```bash
tail -f frontend.log
```

### Verify Ports
```bash
sudo netstat -tlnp | grep -E ':(3000|8001)'
```

### Restart MongoDB
```bash
sudo pkill mongod
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
```

### Check Environment Variables
```bash
cat frontend/.env
cat backend/.env
```

The frontend .env should show your Codespace URL:
```
REACT_APP_BACKEND_URL=https://your-codespace-name-8001.app.github.dev
```

---

## Manual Setup (if automatic setup failed)

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend (in new terminal)
```bash
cd frontend
yarn install
PORT=3000 yarn start
```

---

## Common Issues

### 1. "Failed to fetch"
- **Cause**: Backend not running or ports not public
- **Fix**: Run startup script and make ports public

### 2. Backend won't start
- **Cause**: Missing dependencies or port in use
- **Fix**: Check backend.log and kill existing processes

### 3. Frontend shows blank page
- **Cause**: Wrong backend URL in .env
- **Fix**: Check frontend/.env has correct Codespace URL

### 4. MongoDB connection errors
- **Cause**: MongoDB not running
- **Fix**: Restart MongoDB (see commands above)

---

## Need More Help?

Check:
- [CODESPACES_SETUP_GUIDE.md](./CODESPACES_SETUP_GUIDE.md) - Full setup guide
- [CODESPACES_TROUBLESHOOTING.md](./CODESPACES_TROUBLESHOOTING.md) - Detailed troubleshooting
- [README.md](./README.md) - Project documentation
