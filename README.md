# 🚀 ML Experiment Tracking Platform

Track your machine learning experiments with ease! A complete platform with a beautiful web interface and dead-simple Python integration.

## ✨ What You Get

- **🎨 Beautiful Dashboard** - See all your experiments in one place
- **📊 Interactive Charts** - Visualize metrics with export to PNG
- **⚡ 4-Line Integration** - Add tracking to any ML project instantly
- **🔍 Search & Filter** - Find experiments by name, ID, or tags
- **📦 Artifact Storage** - Save models, plots, and datasets
- **🌙 Dark Mode** - Easy on the eyes

## 🚀 Quick Start

### 1. Start the Platform

```bash
# Start backend (FastAPI + PostgreSQL)
docker-compose up -d

# Start frontend (Next.js)
cd frontend
npm install
npm run dev
```

**That's it!** 
- Dashboard: http://localhost:3000
- API: http://localhost:8000

### 2. Track Your Experiments

**Option A: Use the Simple Tracker (Recommended)**

1. Download `mltracker.py` from http://localhost:3000/integration
2. Drop it in your ML project
3. Use it:

```python
from mltracker import tracker

tracker.start("My Model", lr=0.001, epochs=100)

for epoch in range(100):
    loss = train_step()  # your training code
    tracker.log("loss", loss, step=epoch)

tracker.save_model("model.pkl")
tracker.finish()
```

**Option B: Use the REST API**

See http://localhost:3000/integration for complete examples in Python, cURL, and Node.js.

## 📚 Documentation

- **Integration Guide**: http://localhost:3000/integration
- **API Docs**: http://localhost:8000/docs
- **Examples**: Check the `/examples` folder

## 🛠️ Tech Stack

**Frontend:**
- Next.js 16 with TypeScript
- Tailwind CSS v4
- shadcn/ui components
- TanStack Query for data fetching
- Recharts for visualizations

**Backend:**
- FastAPI
- PostgreSQL 15
- SQLAlchemy ORM
- Docker & Docker Compose

## 📁 Project Structure

```
MlTrackingAPP/
├── mltracker.py          # Simple Python tracker (use this!)
├── frontend/             # Next.js web interface
├── app/                  # FastAPI backend
├── examples/             # Example integrations
└── docker-compose.yml    # One-command setup
```

## 🎯 Common Tasks

```bash
# Start everything
docker-compose up -d && cd frontend && npm run dev

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Reset database
docker-compose down -v
docker-compose up -d

# Run tests
pytest
```

## 📊 API Endpoints

- `POST /experiments` - Create experiment
- `GET /experiments` - List all experiments
- `GET /experiments/{id}` - Get experiment details
- `PUT /experiments/{id}/status` - Update status
- `PUT /experiments/{id}/tags` - Update tags
- `DELETE /experiments/{id}` - Delete experiment
- `POST /experiments/{id}/metrics` - Log metrics
- `GET /experiments/{id}/metrics` - Get metrics
- `POST /experiments/{id}/artifacts` - Upload artifact
- `GET /experiments/{id}/artifacts` - List artifacts

**Full interactive docs**: http://localhost:8000/docs

## 🚢 Deployment

Ready to go live? Check out **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete guides:

- **Vercel + Railway** (Easiest - Free tier, ~15 min setup)
- **Render** (All-in-one platform)
- **AWS/DigitalOcean** (Full control with Docker)
- **Heroku** (Classic deployment)

Quick start:
```bash
# Deploy frontend to Vercel
cd frontend && vercel

# Deploy backend to Railway or Render
# See DEPLOYMENT.md for step-by-step guides
```

## 🤝 Contributing

This is a learning project. Feel free to use it for your experiments!

## 📄 License

MIT License - Use it however you want!

---

**Need help?** Visit http://localhost:3000/integration for examples and documentation.
