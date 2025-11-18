# 🚀 Quick Start - GitHub Codespaces

## 1️⃣ One-Command Setup (Recommended)

```bash
bash scripts/start_codespaces.sh
```

**This handles everything:**
- ✅ Starts MongoDB
- ✅ Configures correct URLs automatically
- ✅ Installs dependencies
- ✅ Starts backend (port 8001)
- ✅ Starts frontend (port 3000)

---

## 2️⃣ If You See 404 Errors

**Run the URL fix script:**
```bash
bash scripts/fix_codespaces_urls.sh
```

Then restart services manually or run the start script.

---

## 3️⃣ Access Your Application

1. Click **PORTS** tab in VS Code (bottom panel)
2. Find port **3000** (Frontend)
3. Click the **🌐 globe icon** to open in browser

---

## 4️⃣ Check Service Status

```bash
# See what's running
ps aux | grep -E 'mongod|uvicorn|node'

# Check backend API
curl http://localhost:8001/api/

# Should return: {"message":"Hello World"}
```

---

## 🆘 Having Issues?

See full troubleshooting guide: [CODESPACES_TROUBLESHOOTING.md](./CODESPACES_TROUBLESHOOTING.md)

---

## 📌 Key Commands

| Action | Command |
|--------|---------|
| Start everything | `bash scripts/start_codespaces.sh` |
| Fix URLs only | `bash scripts/fix_codespaces_urls.sh` |
| Stop services | `killall node python uvicorn` |
| Start MongoDB | `sudo mongod --fork --logpath /var/log/mongodb.log` |
| Backend only | `cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload` |
| Frontend only | `cd frontend && PORT=3000 yarn start` |

---

## ⚡ First Time Setup

If this is your first time running the application:

```bash
# 1. Install backend dependencies
cd /app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd /app

# 2. Install frontend dependencies
cd /app/frontend
yarn install
cd /app

# 3. Start everything
bash scripts/start_codespaces.sh
```

---

## 🌐 Important URLs

After starting the application, find your URLs in the PORTS tab:

- **Frontend:** `https://{your-codespace}-3000.app.github.dev`
- **Backend API:** `https://{your-codespace}-8001.app.github.dev`
- **API Docs:** `https://{your-codespace}-8001.app.github.dev/docs`

These URLs are automatically configured when you use `start_codespaces.sh`!
