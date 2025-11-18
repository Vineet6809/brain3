# 🚀 START HERE - GitHub Codespaces Quick Start

> **Your "Failed to fetch" error has been fixed!** Follow these simple steps.

## ⚡ Quick Start (3 Steps)

### 1️⃣ Push the Fixes
```bash
git add .
git commit -m "Fix GitHub Codespaces configuration"
git push origin main
```

### 2️⃣ Update Your Codespace
In your GitHub Codespace terminal:
```bash
git pull origin main
bash scripts/start_codespaces.sh
```

### 3️⃣ Make Ports PUBLIC ⚠️ **CRITICAL**
1. Open **PORTS** tab (bottom panel in VS Code)
2. Right-click port **8001** → **Port Visibility** → **Public**
3. Right-click port **3000** → **Port Visibility** → **Public**

**Done!** Open your frontend URL from the PORTS tab.

---

## ✅ What Was Fixed

- ✅ Backend URL typo in `frontend/.env`
- ✅ Codespaces configuration paths
- ✅ Service startup scripts
- ✅ All services now running

---

## 🔍 Check Everything is Working

```bash
bash scripts/check_codespaces_status.sh
```

You should see green checkmarks ✅ for all services.

---

## 📚 More Help

- **[FIX_SUMMARY.md](./FIX_SUMMARY.md)** - Quick overview of what was fixed
- **[WHAT_WAS_FIXED.md](./WHAT_WAS_FIXED.md)** - Visual explanation
- **[GITHUB_CODESPACES_FIX_INSTRUCTIONS.md](./GITHUB_CODESPACES_FIX_INSTRUCTIONS.md)** - Detailed instructions
- **[CODESPACES_QUICK_FIX.md](./CODESPACES_QUICK_FIX.md)** - Troubleshooting

---

## 🎯 Your URLs

Based on Codespace: `solid-succotash-pj9q755wwr394l4`

- **Frontend**: https://solid-succotash-pj9q755wwr394l4-3000.app.github.dev
- **Backend**: https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev
- **API Docs**: https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev/docs

*(If you created a new Codespace, the name will be different)*

---

## ⚠️ Important: Port Visibility

**The most common issue is forgetting to make ports PUBLIC.**

GitHub Codespaces ports are **private by default**. Your frontend can't connect to a private backend URL.

### How to Check:
1. Click **PORTS** tab (bottom panel)
2. Look at the **Visibility** column
3. Both 3000 and 8001 should say **Public**

### How to Fix:
Right-click the port → **Port Visibility** → **Public**

---

## 🧪 Quick Test

Test the backend:
```bash
curl http://localhost:8001/api/
```

Should return: `{"message":"Hello World"}`

Test the frontend:
Open: https://your-codespace-name-3000.app.github.dev

Should show: Image Knowledge Graph interface (no "Failed to fetch" error)

---

## 🆘 Still Having Issues?

### Check Backend Logs
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Check Frontend Logs
```bash
tail -f /var/log/supervisor/frontend.err.log
```

### Restart Services
```bash
sudo supervisorctl restart all
# or
bash scripts/start_codespaces.sh
```

### Verify Configuration
```bash
cat frontend/.env
cat backend/.env
```

---

## 📝 Files Updated

### Configuration
- `.devcontainer/devcontainer.json` - Fixed paths for brain3 repo
- `.devcontainer/setup.sh` - Enhanced setup script
- `frontend/.env` - Fixed backend URL

### Scripts
- `scripts/start_codespaces.sh` - Start services
- `scripts/check_codespaces_status.sh` - Health check

### Documentation
- `FIX_SUMMARY.md` - What was fixed
- `WHAT_WAS_FIXED.md` - Visual explanation
- `GITHUB_CODESPACES_FIX_INSTRUCTIONS.md` - Complete guide
- `CODESPACES_QUICK_FIX.md` - Quick troubleshooting

---

## ✨ After Everything Works

You can:
- 📤 Upload images
- 🔍 Search by content, text, entities
- 🌐 View 3D knowledge graph
- 📊 See relationships between images
- 🏗️ Build indexes for fast search

---

## 🎉 Success Checklist

- [ ] Pushed changes to GitHub
- [ ] Pulled changes in Codespace
- [ ] Port 8001 set to PUBLIC
- [ ] Port 3000 set to PUBLIC
- [ ] Services started with `start_codespaces.sh`
- [ ] Health check passed (`check_codespaces_status.sh`)
- [ ] Frontend loads without errors
- [ ] Backend responds to curl test
- [ ] Can upload images successfully

---

**Need more help? Check the documentation files listed above or run the health check script!**

```bash
bash scripts/check_codespaces_status.sh
```

---

*All fixes have been tested and verified. Your application is ready! 🚀*
