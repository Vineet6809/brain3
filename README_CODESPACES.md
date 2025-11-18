# 🎯 Quick Start - GitHub Codespaces (RECOMMENDED)

**This application requires 4GB+ RAM. Use GitHub Codespaces instead of Replit.**

---

## 🚀 3-Step Setup

### **1️⃣ Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### **2️⃣ Open in Codespaces**

1. Go to your GitHub repo
2. Click **"Code"** → **"Codespaces"** tab
3. Click **"Create codespace on main"**
4. Wait 5-10 minutes for automatic setup

### **3️⃣ Start the App**

```bash
bash scripts/start_codespaces.sh
```

**Done!** Access your app via the forwarded ports in the PORTS tab.

---

## 📖 Full Documentation

See **[CODESPACES_SETUP_GUIDE.md](./CODESPACES_SETUP_GUIDE.md)** for complete instructions.

---

## 🔧 Configuration Files Created

✅ `.devcontainer/devcontainer.json` - Codespace configuration  
✅ `.devcontainer/setup.sh` - Automatic setup script  
✅ `scripts/start_codespaces.sh` - Application startup script  

---

## ⚡ Why Codespaces?

| Feature | Replit | Codespaces |
|---------|--------|------------|
| RAM | 2GB ❌ | 4-8GB ✅ |
| CPU | 2 cores | 4+ cores |
| ML Models | Fails | Works |
| Free Tier | Limited | 60h/month |

---

## 🆘 Quick Help

**Backend not starting?**
```bash
cd backend && source .venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001
```

**Frontend errors?**
```bash
cd frontend && yarn install && PORT=3000 yarn start
```

**MongoDB issues?**
```bash
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
```

---

## 🎉 What's Fixed

✅ **"Response body is already used" error** - Already fixed in the code!  
✅ **RAM limitations** - Codespaces has 4-8GB  
✅ **ML model loading** - Works perfectly in Codespaces  
✅ **Port forwarding** - Automatic HTTPS URLs  

Enjoy your Image Knowledge Graph! 🖼️📊
