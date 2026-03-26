# Deployment Guide for Video Downloader

This guide covers deploying your video downloader to various hosting platforms and connecting your domain `fuvideo.site`.

## Table of Contents
1. [Preparation](#preparation)
2. [Railway (Recommended)](#railway)
3. [Render](#render)
4. [PythonAnywhere](#pythonanywhere)
5. [Domain Configuration](#domain-configuration)

---

## Preparation

Before deploying:

1. **Create a GitHub repository** (or use GitLab/Bitbucket)
   ```bash
   cd projects
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```
   This creates the `dist/` folder that the Flask backend will serve.

3. **Verify build works locally**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
   Open http://localhost:5000 to see your React app.

---

## Railway (Recommended)

Railway is the easiest option with a generous free tier.

### Step 1: Sign up and connect GitHub

1. Go to [railway.app](https://railway.app) and sign up
2. Connect your GitHub account
3. Grant access to your repository

### Step 2: Create a new project

1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select your repository

### Step 3: Configure deployment

Railway will auto-detect your Python app. You may need to:

1. Add **Environment Variables** (in Railway dashboard):
   - `PORT` = `5000` (or leave blank, Railway sets it automatically)
   - `FLASK_ENV` = `production`
   - Optional: `SECRET_KEY` = random string

2. Set **Start Command**:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```
   Or simpler:
   ```bash
   python app.py
   ```

3. Ensure **Build Command**:
   ```bash
   cd frontend && npm install && npm run build
   ```

   Railway uses a `railway.json` or `Dockerfile` for customization. You can create:

   **railway.json** (in project root):
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "cd backend && python app.py",
       "healthcheckPath": "/api/health"
     }
   }
   ```

### Step 4: Deploy

1. Click **"Deploy"** button
2. Wait for build (5-10 minutes first time)
3. Your app will be live at a random railway.app subdomain

---

## Render

Render also has a free tier with some limitations.

### Step 1: Sign up

1. Go to [render.com](https://render.com) and sign up
2. Connect GitHub

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Configure:
   - **Name**: `video-downloader`
   - **Environment**: `Python 3`
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn --bind 0.0.0.0:$PORT app:app
     ```
   - Choose **Free** instance type

### Step 3: Environment Variables

Add in Render dashboard:
- `PORT` = `10000` (Render sets this automatically)
- `FLASK_ENV` = `production`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment
3. Your app gets a `onrender.com` subdomain

---

## PythonAnywhere

Good for simple Python hosting, but limited free tier.

### Step 1: Upload files

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Files** → upload your project
3. Upload as ZIP and extract, or upload file by file

### Step 2: Set up virtualenv

In **Consoles** → **Bash**:
```bash
cd /home/yourusername
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build
```

**Note**: PythonAnywhere may not have Node.js on free tier. You can:
- Build frontend locally and upload `dist/` folder
- Or use a separate hosting for frontend (Vercel/Netlify)

### Step 3: Configure WSGI file

1. Go to **Web** tab
2. Click **WSGI configuration file** link
3. Replace contents with:
```python
import sys
path = '/home/yourusername'
if path not in sys.path:
    sys.path.insert(0, path)

from backend.app import app as application  # noqa
```

4. Set **Working directory**: `/home/yourusername`

5. Set **Source code**: `/home/yourusername/backend`

6. Set **Virtualenv**: `/home/yourusername/venv`

7. Set **Port**: `8080` (or leave default)

8. Reload web app

---

## Domain Configuration (fuvideo.site)

Once your app is deployed, connect your domain:

### Point Domain to Your App

1. **Buy/own domain**: `fuvideo.site`
2. Go to your domain registrar (GoDaddy, Namecheap, etc.)
3. Find **DNS Settings**
4. Add/Update records:

| Type | Name/Subdomain | Value/Target | TTL |
|------|----------------|--------------|-----|
| A | @ | Render/Railway IP address | Auto |
| CNAME | www | your-app.onrender.com | Auto |

**For Railway**:
- Go to your project → Settings → Domains
- Add `fuvideo.site` and `www.fuvideo.site`
- Railway provides CNAME target: `your-project.up.railway.app`

**For Render**:
- Go to your service → Settings → Custom Domain
- Add `fuvideo.site`
- Render provides CNAME target: `your-service.onrender.com`

### SSL Certificate

- **Railway**: Automatic HTTPS with SSL
- **Render**: Automatic SSL via Let's Encrypt
- **Manual**: Use Cloudflare (free CDN + SSL)

---

## Recommended Stack for Your Project

**Easiest**: Railway (single deploy, free tier)
1. Push to GitHub
2. Connect Railway → auto-deploy
3. Add custom domain `fuvideo.site`
4. Done!

**Most Reliable**: Render
1. Push to GitHub
2. Connect Render → auto-deploy from main branch
3. Configure domain
4. Good free tier

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'yt_dlp'"
- Ensure `requirements.txt` is in `backend/` folder
- Build command must run `pip install -r requirements.txt`

### "FFmpeg not found"
- Railway/Render don't have FFmpeg by default
- **Solution**: Use Railway's NixPacks to install FFmpeg
  Create `railway.nix`:
  ```nix
  { pkgs }: {
    packages = [ pkgs.ffmpeg ];
  }
  ```
  Or use Dockerfile (see below)

### Frontend not loading, blank page
- Check that frontend is built to `frontend/dist/`
- Flask static folder should point to `../frontend/dist`
- Check browser console for errors

### API returns 404
- Ensure CORS is enabled (it is in our code)
- Check that you're hitting `/api/info` not just `/info`

---

## Advanced: Docker Deployment

If you want more control, create a `Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Production stage
FROM python:3.11-slim
WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ .

# Copy frontend build
COPY --from=builder /app/dist ../frontend/dist

ENV PORT=5000
EXPOSE 5000

CMD ["python", "app.py"]
```

Then deploy Dockerfile to any container host (Railway, Render, DigitalOcean, etc.)

---

## Next Steps

1. Choose your hosting platform
2. Push code to GitHub
3. Follow platform-specific deployment steps
4. Connect domain `fuvideo.site`
5. Test with real video URLs
6. Optionally: Add rate limiting, caching, monitoring

**Questions?** Check your platform's documentation or ask me!