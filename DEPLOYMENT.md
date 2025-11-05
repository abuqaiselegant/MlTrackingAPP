# 🚀 Deployment Guide

Complete step-by-step guide to deploy your ML Tracking Platform to production.

## 📋 Deployment Options

### Option 1: **Vercel + Railway** (Easiest - Free Tier Available)
- **Frontend**: Vercel (Free)
- **Backend + Database**: Railway ($5/month)
- **Best for**: Small teams, personal projects
- **Setup time**: ~15 minutes

### Option 2: **Render** (All-in-One - Simple)
- **Everything on Render**: Free tier available
- **Best for**: Single-platform preference
- **Setup time**: ~20 minutes

### Option 3: **AWS/DigitalOcean** (Full Control)
- **Using Docker**: Deploy to any VPS
- **Best for**: Production apps, custom needs
- **Setup time**: ~30-45 minutes

### Option 4: **Heroku** (Classic - Simple)
- **All-in-one platform**: Easy setup
- **Best for**: Quick deployments
- **Setup time**: ~15 minutes

---

## 🎯 Option 1: Vercel + Railway (Recommended)

### **Part A: Deploy Database + Backend on Railway**

#### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign in with GitHub

#### Step 2: Deploy PostgreSQL
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically provision a database
3. Go to your database → **"Variables"** tab
4. Copy these values (you'll need them):
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `DATABASE_URL`

#### Step 3: Deploy Backend (FastAPI)
1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select `MlTrackingAPP` repository
3. Click **"Add variables"** and set:
   ```
   DATABASE_URL=<paste from PostgreSQL service>
   PORT=8000
   ```
4. Go to **"Settings"** → **"Generate Domain"** (this is your API URL)
5. Copy the domain (e.g., `mltracking-production.up.railway.app`)

#### Step 4: Configure Railway for Python
Railway auto-detects Python. If needed, add `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### **Part B: Deploy Frontend on Vercel**

#### Step 1: Prepare Frontend
1. Add environment variable to `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-domain.railway.app
   ```

2. Update `frontend/next.config.ts`:
   ```typescript
   import type { NextConfig } from "next";

   const nextConfig: NextConfig = {
     env: {
       NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
     },
   };

   export default nextConfig;
   ```

#### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository `MlTrackingAPP`
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-domain.railway.app
   ```
6. Click **"Deploy"**

#### Step 3: Done! 🎉
Your app is live:
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-railway-domain.railway.app`

---

## 🎯 Option 2: Render (All-in-One)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Deploy Database
1. Click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `mltracking-db`
   - **Database**: `mltracking`
   - **User**: `mltracking_user`
   - **Region**: Choose closest to you
   - **Plan**: Free (or Starter $7/month)
3. Click **"Create Database"**
4. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Deploy Backend
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo `MlTrackingAPP`
3. Fill in:
   - **Name**: `mltracking-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables**:
   ```
   DATABASE_URL=<paste Internal Database URL>
   PYTHON_VERSION=3.11
   ```
5. Click **"Create Web Service"**
6. Copy your service URL (e.g., `https://mltracking-api.onrender.com`)

### Step 4: Deploy Frontend
1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repo `MlTrackingAPP`
3. Fill in:
   - **Name**: `mltracking-app`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next`
4. Add **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://mltracking-api.onrender.com
   ```
5. Click **"Create Static Site"**

### Step 5: Update API URL in Frontend
Your frontend needs to know where the backend is:

```bash
# In frontend/.env.production
NEXT_PUBLIC_API_URL=https://mltracking-api.onrender.com
```

Commit and push - Render will auto-redeploy!

---

## 🎯 Option 3: AWS/DigitalOcean/Any VPS (Docker)

### Prerequisites
- VPS with Docker installed
- Domain name (optional but recommended)

### Step 1: Prepare Your Server
```bash
# SSH into your server
ssh user@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone Your Repository
```bash
git clone https://github.com/abuqaiselegant/MlTrackingAPP.git
cd MlTrackingAPP
```

### Step 3: Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit with your settings
nano .env
```

Set these values:
```env
POSTGRES_USER=mltracking_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=mltracking
DATABASE_URL=postgresql://mltracking_user:your_secure_password_here@db:5432/mltracking
```

### Step 4: Update Frontend Configuration
```bash
cd frontend
nano .env.production
```

Add:
```env
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
# Or with domain: https://api.yourdomain.com
```

### Step 5: Build and Deploy
```bash
# Build frontend
cd frontend
npm install
npm run build

# Go back to root
cd ..

# Start everything with Docker
docker-compose up -d
```

### Step 6: Set Up Nginx (Reverse Proxy)
```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/mltracking
```

Paste this configuration:
```nginx
# API Server
server {
    listen 80;
    server_name api.yourdomain.com;  # or your-server-ip

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and start:
```bash
sudo ln -s /etc/nginx/sites-available/mltracking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Add SSL with Let's Encrypt (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

### Step 8: Auto-start on Reboot
```bash
# Create systemd service
sudo nano /etc/systemd/system/mltracking.service
```

Paste:
```ini
[Unit]
Description=ML Tracking Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/MlTrackingAPP
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable mltracking
sudo systemctl start mltracking
```

---

## 🎯 Option 4: Heroku

### Step 1: Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from heroku.com/cli
```

### Step 2: Login
```bash
heroku login
```

### Step 3: Create Apps
```bash
# Create backend app
heroku create mltracking-api

# Create frontend app (if needed)
heroku create mltracking-app
```

### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini -a mltracking-api
```

### Step 5: Configure Backend
Create `Procfile` in root:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11.0
```

### Step 6: Deploy Backend
```bash
# Set buildpack
heroku buildpacks:set heroku/python -a mltracking-api

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head -a mltracking-api
```

### Step 7: Deploy Frontend (Vercel)
Heroku doesn't support Next.js 15+ well. Use Vercel for frontend:
- Follow **Option 1, Part B** above
- Use Heroku backend URL as API_URL

---

## 📊 Deployment Comparison

| Feature | Vercel+Railway | Render | VPS/Docker | Heroku |
|---------|----------------|--------|------------|---------|
| **Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Free Tier** | Yes | Yes (limited) | No | No |
| **Cost** | $5/mo | $7/mo | $5-20/mo | $7/mo |
| **Auto-deploy** | Yes | Yes | Manual | Yes |
| **Custom Domain** | Yes | Yes | Yes | Yes |
| **SSL** | Auto | Auto | Manual | Auto |
| **Best For** | Startups | Simple projects | Production | Quick deploy |

---

## 🔧 Post-Deployment Checklist

### 1. Test Your Deployment
```bash
# Test API health
curl https://your-api-url.com/

# Test creating experiment
curl -X POST https://your-api-url.com/experiments \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Deploy","hyperparameters":{"test":true}}'
```

### 2. Update mltracker.py
Users should use your production API:
```python
# In mltracker.py, update API_URL
API_URL = "https://your-production-api-url.com"
```

### 3. Set Up Monitoring
- **Railway/Render**: Built-in logs and metrics
- **VPS**: Use `docker-compose logs -f`
- **Add tools**: Sentry, LogRocket, or Datadog

### 4. Configure CORS
Update `app/main.py` with your frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Backup Database
```bash
# Railway: Automatic backups included
# Render: Automatic on paid plans
# VPS: Set up cron job
0 2 * * * docker exec mltrackingapp_db_1 pg_dump -U mltracking_user mltracking > /backup/db_$(date +\%Y\%m\%d).sql
```

---

## 🆘 Troubleshooting

### Frontend can't connect to API
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify CORS settings in backend
- Check browser console for errors

### Database connection failed
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Check database is running
- Verify network connectivity

### Build failures
- Check Node.js version (frontend needs 18+)
- Check Python version (backend needs 3.9+)
- Clear cache and rebuild

### 502 Bad Gateway (Nginx)
- Check backend is running: `docker ps`
- Check logs: `docker logs mltrackingapp_backend_1`
- Verify port numbers in Nginx config

---

## 🎉 You're Live!

Your ML Tracking Platform is now deployed! Share it with your team:

- **Dashboard**: `https://your-app.vercel.app`
- **API Docs**: `https://your-api.railway.app/docs`
- **GitHub**: `https://github.com/abuqaiselegant/MlTrackingAPP`

Need help? Check the logs or open an issue on GitHub!
