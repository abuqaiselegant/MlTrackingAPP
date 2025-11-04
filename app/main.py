from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import experiments_router, metrics_router, artifacts_router

settings = get_settings()

app = FastAPI(
    title="ML Experiment Tracking Platform",
    description="A simple API for tracking machine learning experiments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments_router)
app.include_router(metrics_router)
app.include_router(artifacts_router)


@app.get("/")
def read_root():
    return {"message": "ML Experiment Tracking Platform API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
