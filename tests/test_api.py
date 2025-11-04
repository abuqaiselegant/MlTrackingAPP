import pytest
import io
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.main import app
from app.database import Base, get_db
from app.models.experiment import Experiment


# In-memory SQLite for testing
SQLTEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLTEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(test_db, tmp_path):
    """Create test client with temporary artifacts directory."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    # Override settings for testing
    from app.config import settings
    settings.ARTIFACTS_PATH = str(tmp_path / "test_artifacts")
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_experiment(test_db):
    """Create a sample experiment for testing."""
    experiment = Experiment(
        name="Test Experiment",
        description="For testing purposes",
        hyperparameters={"lr": 0.001, "batch_size": 32}
    )
    test_db.add(experiment)
    test_db.commit()
    test_db.refresh(experiment)
    return experiment


# =============================================================================
# HEALTH & INFO TESTS
# =============================================================================

def test_read_root(test_client):
    """Test root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "ML Experiment Tracking Platform API",
        "version": "1.0.0"
    }


def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# =============================================================================
# EXPERIMENT TESTS
# =============================================================================

def test_create_experiment(test_client):
    """Test creating an experiment."""
    response = test_client.post(
        "/experiments",
        json={
            "name": "CNN Training",
            "description": "Image classification model",
            "hyperparameters": {"lr": 0.001, "epochs": 10}
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "CNN Training"
    assert data["description"] == "Image classification model"
    assert data["hyperparameters"]["lr"] == 0.001
    assert data["status"] == "running"
    assert "id" in data
    assert "created_at" in data


def test_list_experiments(test_client, sample_experiment):
    """Test listing experiments."""
    response = test_client.get("/experiments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Experiment"


def test_list_experiments_pagination(test_client, sample_experiment):
    """Test experiments pagination."""
    # Create more experiments
    for i in range(5):
        test_client.post(
            "/experiments",
            json={"name": f"Experiment {i}", "hyperparameters": {}}
        )
    
    # Test pagination
    response = test_client.get("/experiments?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_experiments_filter_by_status(test_client, sample_experiment):
    """Test filtering experiments by status."""
    # Update status
    test_client.put(
        f"/experiments/{sample_experiment.id}/status",
        json={"status": "completed"}
    )
    
    # Filter by completed
    response = test_client.get("/experiments?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(exp["status"] == "completed" for exp in data)


def test_update_status(test_client, sample_experiment):
    """Test updating experiment status."""
    response = test_client.put(
        f"/experiments/{sample_experiment.id}/status",
        json={"status": "completed"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_update_status_invalid(test_client, sample_experiment):
    """Test updating to invalid status."""
    response = test_client.put(
        f"/experiments/{sample_experiment.id}/status",
        json={"status": "invalid_status"}
    )
    assert response.status_code == 422


def test_get_single_experiment(test_client, sample_experiment):
    """Test getting a single experiment."""
    response = test_client.get(f"/experiments/{sample_experiment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_experiment.id)
    assert data["name"] == "Test Experiment"


def test_get_single_experiment_not_found(test_client):
    """Test getting non-existent experiment returns 404."""
    fake_id = uuid4()
    response = test_client.get(f"/experiments/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# =============================================================================
# METRICS TESTS
# =============================================================================

def test_log_single_metric(test_client, sample_experiment):
    """Test logging a single metric."""
    response = test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "step": 0,
            "metric_name": "loss",
            "value": 0.5
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["logged"] == 1


def test_log_batch_metrics(test_client, sample_experiment):
    """Test logging batch of metrics."""
    response = test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "metrics": [
                {"step": 0, "metric_name": "loss", "value": 0.5},
                {"step": 1, "metric_name": "loss", "value": 0.4},
                {"step": 0, "metric_name": "accuracy", "value": 0.8},
                {"step": 1, "metric_name": "accuracy", "value": 0.85}
            ]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["logged"] == 4


def test_log_metric_invalid_value(test_client, sample_experiment):
    """Test logging metric with NaN value fails."""
    response = test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "step": 0,
            "metric_name": "loss",
            "value": float('nan')
        }
    )
    assert response.status_code == 422


def test_query_metrics(test_client, sample_experiment):
    """Test querying metrics."""
    # Log some metrics
    test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "metrics": [
                {"step": 0, "metric_name": "loss", "value": 0.5},
                {"step": 1, "metric_name": "loss", "value": 0.4},
                {"step": 2, "metric_name": "loss", "value": 0.3}
            ]
        }
    )
    
    # Query metrics
    response = test_client.get(f"/experiments/{sample_experiment.id}/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_query_metrics_filter_by_name(test_client, sample_experiment):
    """Test filtering metrics by name."""
    # Log different metrics
    test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "metrics": [
                {"step": 0, "metric_name": "loss", "value": 0.5},
                {"step": 0, "metric_name": "accuracy", "value": 0.8}
            ]
        }
    )
    
    # Filter by name
    response = test_client.get(
        f"/experiments/{sample_experiment.id}/metrics?name=loss"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["metric_name"] == "loss"


def test_get_metrics_summary(test_client, sample_experiment):
    """Test getting metrics summary."""
    # Log metrics
    test_client.post(
        f"/experiments/{sample_experiment.id}/metrics",
        json={
            "metrics": [
                {"step": 0, "metric_name": "loss", "value": 0.5},
                {"step": 1, "metric_name": "loss", "value": 0.3},
                {"step": 2, "metric_name": "loss", "value": 0.4}
            ]
        }
    )
    
    # Get summary
    response = test_client.get(
        f"/experiments/{sample_experiment.id}/metrics/summary"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "loss"
    assert data[0]["min"] == 0.3
    assert data[0]["max"] == 0.5
    assert data[0]["latest_value"] == 0.4
    assert "mean" in data[0]


# =============================================================================
# ARTIFACTS TESTS
# =============================================================================

def test_upload_file(test_client, sample_experiment):
    """Test uploading an artifact file."""
    file_content = b"model weights data"
    files = {
        "file": ("model.pkl", io.BytesIO(file_content), "application/octet-stream")
    }
    
    response = test_client.post(
        f"/artifacts/experiments/{sample_experiment.id}/upload",
        files=files
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "model.pkl"
    assert data["size_bytes"] == len(file_content)
    assert "id" in data
    assert "uploaded_at" in data


def test_upload_file_sanitizes_filename(test_client, sample_experiment):
    """Test that dangerous filenames are sanitized."""
    files = {
        "file": ("../../../etc/passwd", io.BytesIO(b"data"), "text/plain")
    }
    
    response = test_client.post(
        f"/artifacts/experiments/{sample_experiment.id}/upload",
        files=files
    )
    
    assert response.status_code == 201
    data = response.json()
    # Should sanitize away path traversal
    assert ".." not in data["filename"]
    assert "/" not in data["filename"]


def test_list_artifacts(test_client, sample_experiment):
    """Test listing artifacts."""
    # Upload some files
    for i in range(3):
        files = {
            "file": (f"file{i}.txt", io.BytesIO(f"content{i}".encode()), "text/plain")
        }
        test_client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
    
    # List artifacts
    response = test_client.get(f"/artifacts/experiments/{sample_experiment.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_artifacts_pagination(test_client, sample_experiment):
    """Test artifacts pagination."""
    # Upload 5 files
    for i in range(5):
        files = {
            "file": (f"file{i}.txt", io.BytesIO(f"content{i}".encode()), "text/plain")
        }
        test_client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
    
    # Get first 2
    response = test_client.get(
        f"/artifacts/experiments/{sample_experiment.id}?skip=0&limit=2"
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_download_file(test_client, sample_experiment):
    """Test downloading an artifact."""
    file_content = b"model data to download"
    files = {
        "file": ("model.pkl", io.BytesIO(file_content), "application/octet-stream")
    }
    
    # Upload
    upload_response = test_client.post(
        f"/artifacts/experiments/{sample_experiment.id}/upload",
        files=files
    )
    artifact_id = upload_response.json()["id"]
    
    # Download
    download_response = test_client.get(f"/artifacts/{artifact_id}/download")
    assert download_response.status_code == 200
    assert download_response.content == file_content


def test_download_file_not_found(test_client):
    """Test downloading non-existent artifact returns 404."""
    fake_id = uuid4()
    response = test_client.get(f"/artifacts/{fake_id}/download")
    assert response.status_code == 404


def test_delete_artifact(test_client, sample_experiment):
    """Test deleting an artifact."""
    files = {
        "file": ("model.pkl", io.BytesIO(b"data"), "application/octet-stream")
    }
    
    # Upload
    upload_response = test_client.post(
        f"/artifacts/experiments/{sample_experiment.id}/upload",
        files=files
    )
    artifact_id = upload_response.json()["id"]
    
    # Delete
    delete_response = test_client.delete(f"/artifacts/{artifact_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    download_response = test_client.get(f"/artifacts/{artifact_id}/download")
    assert download_response.status_code == 404


def test_delete_artifact_not_found(test_client):
    """Test deleting non-existent artifact returns 404."""
    fake_id = uuid4()
    response = test_client.delete(f"/artifacts/{fake_id}")
    assert response.status_code == 404
