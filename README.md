# 🚀 ML Experiment Tracker

Track your machine learning experiments super easily! Beautiful dashboard + simple Python integration.

**Live Demo:** https://ml-tracking-app.vercel.app

## What You Get

- **Dashboard** - View all experiments in one place
- **Charts & Visualizations** - Track metrics in real-time
- **4-Line Integration** - Add to any ML project instantly
- **Save Models** - Upload and download trained models
- **Search Everything** - Find experiments fast

## Quick Start (Local)

```bash
# 1. Start the backend (FastAPI + PostgreSQL)
docker-compose up -d

# 2. Start the frontend (Next.js)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 - Done! 🎉

## Track Your Experiments

### Option 1: Simple Python File (Easiest)

Download `mltracker.py` from the integration page, then:

```python
from mltracker import tracker

# Start tracking
tracker.start("My Cool Model", lr=0.001, epochs=100)

# Log metrics during training
for epoch in range(100):
    loss = train()  # your training code
    tracker.log("loss", loss, step=epoch)

# Save your model
tracker.save_model("model.pkl")

# Done!
tracker.finish()
```

### Option 2: REST API

See full examples at http://localhost:3000/integration

## What's Inside

```
MlTrackingAPP/
├── mltracker.py          # Copy this to your ML project
├── frontend/             # Web dashboard (Next.js)
├── app/                  # Backend API (FastAPI)
├── examples/             # PyTorch, TensorFlow, scikit-learn examples
└── docker-compose.yml    # One command to start everything
```

## Common Commands

```bash
# Start everything
docker-compose up -d && cd frontend && npm run dev

# Stop everything  
docker-compose down

# Reset database (delete all experiments)
docker-compose down -v && docker-compose up -d

# Run tests
pytest
```

## Tech Stack

**Frontend:** Next.js 16, TypeScript, Tailwind CSS, shadcn/ui  
**Backend:** FastAPI, PostgreSQL, Docker  
**Integration:** Single Python file (no dependencies!)

## Deployment

Already deployed! 
- **Frontend:** https://ml-tracking-app.vercel.app
- **Backend:** https://ml-tracking-api.onrender.com

Want to deploy your own? It's on Vercel + Render (free tier).

## API Endpoints

All available at http://localhost:8000/docs

- `POST /experiments` - Create new experiment
- `GET /experiments` - List all experiments  
- `GET /experiments/{id}` - Get one experiment
- `POST /experiments/{id}/metrics` - Log metrics
- `POST /artifacts/experiments/{id}/upload` - Upload model file

## Examples

Check the `/examples` folder:
- `pytorch_example.py` - PyTorch training
- `sklearn_example.py` - Scikit-learn model
- `tensorflow_example.py` - TensorFlow/Keras

## Need Help?

Visit the integration page: http://localhost:3000/integration

## License

MIT - Use it however you want! 

---

Built for ML engineers who want simple experiment tracking without the complexity.
