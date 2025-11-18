# 🔧 Fix Port Visibility in GitHub Codespaces

## Current Issue

Your frontend is trying to access the backend at:
```
https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev
```

But the port might not be publicly accessible, causing the "Failed to fetch" error you're seeing.

---

## ✅ Solution: Make Port 8001 Public

### **Step 1: Open the PORTS Tab**

In VS Code:
1. Look at the bottom panel
2. Click on the **PORTS** tab (next to TERMINAL, PROBLEMS, etc.)

### **Step 2: Make Port 8001 Public**

1. Find **port 8001** in the list
2. Look at the **Visibility** column
3. If it says **"Private"**, right-click on the port
4. Select **"Port Visibility" → "Public"**

### **Step 3: Verify**

After making it public:
1. Right-click on port 8001 again
2. Select **"Copy Local Address"**
3. Paste it in a new browser tab
4. Add `/api/` to the end
5. You should see: `{"message":"Hello World"}`

---

## 🔄 Alternative: Use setupProxy

If making the port public doesn't work, we can set up a proxy in the frontend so all API calls go through the same domain (port 3000).

### **Create setupProxy.js:**

```bash
cd /app/frontend/src
cat > setupProxy.js << 'EOF'
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );
};
EOF
```

### **Install http-proxy-middleware:**

```bash
cd /app/frontend
yarn add http-proxy-middleware
```

### **Update frontend .env:**

```bash
# Change REACT_APP_BACKEND_URL to empty or remove it
# The proxy will handle /api calls automatically
```

### **Restart frontend:**

```bash
sudo supervisorctl restart frontend
```

Now API calls to `/api/...` will be proxied to `localhost:8001/api/...`

---

## 🧪 Test Your Setup

### **Test 1: Backend accessibility**

```bash
# From your local machine browser:
https://solid-succotash-pj9q755wwr394l4-8001.app.github.dev/api/
```

Should show: `{"message":"Hello World"}`

### **Test 2: Frontend can reach backend**

1. Open: `https://solid-succotash-pj9q755wwr394l4-3000.app.github.dev`
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. You should NOT see "Failed to fetch" errors
5. You should NOT see 404 errors

### **Test 3: Try uploading**

1. Click **"Upload Image"**
2. Select an image
3. Should see upload progress
4. Should NOT see error messages

---

## 🎯 Quick Commands Reference

```bash
# Check what's running
sudo supervisorctl status

# Restart services
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
sudo supervisorctl restart all

# View logs
sudo tail -f /var/log/supervisor/frontend.out.log
sudo tail -f /var/log/supervisor/backend.out.log

# Test backend locally
curl http://localhost:8001/api/

# Check current frontend configuration
cat /app/frontend/.env
```

---

## 📊 Current Status

✅ **Backend:** Running on port 8001
✅ **Frontend:** Running on port 3000
✅ **MongoDB:** Running
✅ **Configuration:** Updated with Codespace URLs
⚠️  **Port Visibility:** Port 8001 might need to be public

---

## 🔍 Troubleshooting

### Issue: "Failed to fetch" in browser

**Cause:** Port 8001 not publicly accessible OR CORS issue

**Fix:**
1. Make port 8001 public (see Step 2 above)
2. OR set up proxy (see Alternative section above)

### Issue: CORS error in browser console

**Example:** `Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy`

**Fix:**
```bash
# Backend is already configured with CORS_ORIGINS=*
# But let's verify:
cat /app/backend/.env

# Should show: CORS_ORIGINS=*
# If not, add it and restart backend
sudo supervisorctl restart backend
```

### Issue: 502 Bad Gateway

**Cause:** Backend not running or not accessible

**Fix:**
```bash
# Check backend status
sudo supervisorctl status backend

# Check backend logs
sudo tail -50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

---

## ✨ Success Checklist

- [ ] Port 8001 is set to "Public" in PORTS tab
- [ ] Port 3000 is set to "Public" in PORTS tab  
- [ ] Can access backend: `https://your-codespace-8001.app.github.dev/api/`
- [ ] Can access frontend: `https://your-codespace-3000.app.github.dev`
- [ ] No "Failed to fetch" errors in browser console
- [ ] No 404 errors when clicking buttons
- [ ] Can upload images without errors

Once all checked, your app should be fully functional! 🎉
