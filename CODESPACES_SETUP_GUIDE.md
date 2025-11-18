# 🚀 GitHub Codespaces Setup Guide - Complete Instructions

## Why GitHub Codespaces?

✅ **4-8GB RAM** (vs 2GB in Replit)  
✅ **Better CPU** for ML model processing  
✅ **Free tier**: 60 hours/month (4-core machine)  
✅ **Automatic port forwarding**  
✅ **Native VS Code integration**  
✅ **Perfect for ML applications** like this one

---

## 📋 Prerequisites

1. **GitHub Account** (free)
2. **Your repository pushed to GitHub**
3. That's it! Everything else is automatic.

---

## 🎯 Quick Start (Recommended)

### **Step 1: Push Your Code to GitHub**

If you haven't already pushed your code to GitHub:

```bash
# In your local terminal or Replit shell
cd ~/workspace

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Image Knowledge Graph"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

---

### **Step 2: Open in GitHub Codespaces**

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Click the **green "Code"** button
3. Click the **"Codespaces"** tab
4. Click **"Create codespace on main"**

**That's it!** GitHub will:
- ✅ Create a cloud development environment
- ✅ Install all system dependencies (Tesseract, MongoDB, etc.)
- ✅ Set up Python virtual environment
- ✅ Install all Python packages (including ML models)
- ✅ Install all Node.js dependencies
- ✅ Configure port forwarding
- ✅ Start MongoDB

**Setup time: 5-10 minutes** (one-time setup)

---

### **Step 3: Start the Application**

Once the Codespace is ready and the setup script completes:

```bash
# Make the start script executable
chmod +x scripts/start_codespaces.sh

# Start everything
bash scripts/start_codespaces.sh
```

**Or start services manually:**

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

---

### **Step 4: Access Your Application**

GitHub Codespaces will automatically forward ports and show you notifications:

- **Frontend**: Click the notification for port 3000, or go to the "PORTS" tab
- **Backend API**: Port 8001
- **API Docs**: `https://YOUR-CODESPACE-8001.preview.app.github.dev/docs`

Your application URLs will look like:
```
Frontend:  https://YOUR-CODESPACE-3000.preview.app.github.dev
Backend:   https://YOUR-CODESPACE-8001.preview.app.github.dev
```

---

## 🔧 Configuration Files (Already Created)

I've created the following configuration files for you:

### **`.devcontainer/devcontainer.json`**
Configures the Codespace environment:
- Python 3.11 base image
- Node.js 20
- Automatic port forwarding (3000, 8001, 27017)
- VS Code extensions (Python, ESLint, MongoDB)
- Environment variables

### **`.devcontainer/setup.sh`**
Automatic setup script that runs on Codespace creation:
- Installs system dependencies (Tesseract, MongoDB, etc.)
- Creates Python virtual environment
- Installs all Python packages
- Downloads AI models
- Installs Node.js dependencies
- Configures environment variables

### **`scripts/start_codespaces.sh`**
Convenient startup script to launch all services

---

## 📊 Resource Comparison

| Feature | Replit Free | Codespaces Free | Codespaces Paid |
|---------|-------------|-----------------|-----------------|
| **RAM** | 2GB ❌ | 4GB ✅ | 8-32GB ✅✅ |
| **CPU** | 2 cores | 4 cores | 8-32 cores |
| **Storage** | 10GB | 32GB | 128GB+ |
| **Free Hours** | Always on | 60h/month | Unlimited |
| **ML Models** | Struggles ❌ | Works well ✅ | Excellent ✅✅ |

**Verdict:** GitHub Codespaces is **much better** for this ML-heavy application.

---

## 🎯 Complete Setup Workflow

### **If Starting Fresh:**

1. **Push code to GitHub** (see Step 1 above)
2. **Open in Codespaces** (see Step 2 above)
3. **Wait for automatic setup** (5-10 minutes)
4. **Start the app** with `bash scripts/start_codespaces.sh`
5. **Access frontend** via the forwarded port 3000

### **If Reopening Existing Codespace:**

1. Go to https://github.com/codespaces
2. Click on your existing Codespace
3. Run `bash scripts/start_codespaces.sh`
4. Access your app via the forwarded ports

---

## 🔍 Verify Everything Works

### **1. Check MongoDB:**
```bash
mongosh --eval "db.version()"
```
Should show MongoDB version

### **2. Check Backend:**
```bash
curl http://localhost:8001/api/
```
Should return: `{"status":"ok"}`

### **3. Check Python Environment:**
```bash
cd backend
source .venv/bin/activate
python -c "import sentence_transformers; print('✅ ML models ready')"
```

### **4. Check Frontend:**
Open the forwarded port 3000 - you should see the 3D graph interface

---

## 🐛 Troubleshooting

### **Issue: Setup script didn't run**
**Solution:**
```bash
chmod +x .devcontainer/setup.sh
bash .devcontainer/setup.sh
```

### **Issue: MongoDB not running**
**Solution:**
```bash
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
```

### **Issue: "Module not found" errors**
**Solution:**
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### **Issue: Frontend not connecting to backend**
**Solution:** The environment variable should automatically use Codespace URLs. If not:
```bash
# Get your Codespace name
echo $CODESPACE_NAME

# Update frontend/.env manually
cd frontend
nano .env
```
Update to:
```env
REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}
```

### **Issue: Ports not forwarding**
**Solution:**
1. Open the "PORTS" tab in VS Code
2. Manually add ports: 3000, 8001
3. Right-click each port → "Port Visibility" → "Public"

---

## 💡 Pro Tips for Codespaces

### **1. Persist Your Codespace**
Codespaces auto-delete after 30 days of inactivity. To keep your work:
- Commit and push changes regularly
- Or: Settings → Change retention period

### **2. Prebuilds (Advanced)**
Set up prebuilds to make Codespace creation instant:
- Repository Settings → Codespaces → Set up prebuild

### **3. Machine Type**
Free tier gives you 4-core/8GB. For heavier workloads:
- When creating Codespace, click "..." → "New with options"
- Choose larger machine type (paid)

### **4. Multiple Terminals**
Use VS Code's integrated terminal to run multiple commands:
- Terminal → Split Terminal (or click the + icon)

### **5. Port Forwarding**
All ports are automatically forwarded with HTTPS:
- View in "PORTS" tab
- Make public/private as needed

---

## 🆓 Free Tier Limits

**GitHub Codespaces Free Tier:**
- ✅ 60 hours/month (4-core machine)
- ✅ 15GB storage
- ✅ Perfect for development and testing

**Cost after free tier:**
- ~$0.18/hour for 4-core machine
- Stops charging when Codespace is stopped

---

## 📱 Access from Anywhere

Your Codespace works from:
- ✅ **Web browser** (github.dev)
- ✅ **VS Code Desktop** (click "Open in VS Code Desktop")
- ✅ **VS Code for iPad**
- ✅ **GitHub Mobile app** (view only)

---

## 🔄 Start/Stop Commands

### **Start Application:**
```bash
bash scripts/start_codespaces.sh
```

### **Stop Application:**
```bash
# Press Ctrl+C in the terminal where it's running
# Or kill processes:
pkill -f uvicorn
pkill -f "yarn start"
```

### **Stop Codespace (to save hours):**
- Click your Codespace name → "Stop Codespace"
- Or: Auto-stops after 30 minutes of inactivity

### **Restart Everything:**
```bash
# Stop all services
pkill -f uvicorn; pkill -f "yarn start"; sudo killall mongod

# Start again
bash scripts/start_codespaces.sh
```

---

## 🎓 Learning Resources

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [Codespaces Quickstart](https://docs.github.com/en/codespaces/getting-started/quickstart)
- [Dev Container Spec](https://containers.dev/)

---

## ✅ Ready to Go!

Your application should now be running smoothly in GitHub Codespaces with:
- ✅ **Enough RAM** for ML models
- ✅ **Fast processing** with 4+ cores
- ✅ **Automatic setup** via devcontainer
- ✅ **Proper port forwarding** for frontend/backend
- ✅ **No more "Response body is already used" errors** (already fixed!)

---

## 🚀 Quick Reference Commands

```bash
# Start everything
bash scripts/start_codespaces.sh

# Check status
ps aux | grep -E "mongod|uvicorn|node"

# View logs
cd backend && source .venv/bin/activate && uvicorn server:app --log-level debug

# Test backend
curl http://localhost:8001/api/stats

# Restart MongoDB
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
```

---

Good luck with your Image Knowledge Graph on GitHub Codespaces! 🎉

This setup is **much more reliable** than Replit for ML applications.
