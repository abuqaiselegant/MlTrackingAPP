import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import UUID
import math

from app.main import app
from app.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def experiment(client):
    """Create a test experiment"""
    response = client.post(
        "/experiments",
        json={"name": "Test Experiment"}
    )
    return response.json()


class TestMetricLogging:
    """Test metric logging endpoint"""
    
    def test_log_single_metric(self, client, experiment):
        """Test logging a single metric"""
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={
                "step": 0,
                "metric_name": "loss",
                "value": 0.5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 1
        assert "Successfully logged 1 metric" in data["message"]
    
    def test_log_batch_metrics(self, client, experiment):
        """Test logging batch of metrics"""
        metrics = [
            {"step": i, "metric_name": "loss", "value": 1.0 - (i * 0.01)}
            for i in range(100)
        ]
        
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 100
        assert "Successfully logged 100 metric" in data["message"]
    
    def test_log_metrics_max_batch_size(self, client, experiment):
        """Test maximum batch size of 1000"""
        metrics = [
            {"step": i, "metric_name": "loss", "value": 0.5}
            for i in range(1000)
        ]
        
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1000
    
    def test_log_metrics_exceeds_max_batch(self, client, experiment):
        """Test validation for batch size > 1000"""
        metrics = [
            {"step": i, "metric_name": "loss", "value": 0.5}
            for i in range(1001)
        ]
        
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        assert response.status_code == 422
    
    def test_log_metric_negative_step(self, client, experiment):
        """Test validation for negative step"""
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={
                "step": -1,
                "metric_name": "loss",
                "value": 0.5
            }
        )
        assert response.status_code == 422
    
    def test_log_metric_nan_value(self, client, experiment):
        """Test validation for NaN value"""
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={
                "step": 0,
                "metric_name": "loss",
                "value": float('nan')
            }
        )
        assert response.status_code == 422
    
    def test_log_metric_infinity_value(self, client, experiment):
        """Test validation for infinity value"""
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={
                "step": 0,
                "metric_name": "loss",
                "value": float('inf')
            }
        )
        assert response.status_code == 422
    
    def test_log_metric_nonexistent_experiment(self, client):
        """Test 404 for nonexistent experiment"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.post(
            f"/experiments/{fake_uuid}/metrics",
            json={
                "step": 0,
                "metric_name": "loss",
                "value": 0.5
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_log_multiple_metric_types(self, client, experiment):
        """Test logging different metric types"""
        metrics = [
            {"step": 0, "metric_name": "loss", "value": 0.5},
            {"step": 0, "metric_name": "accuracy", "value": 0.85},
            {"step": 0, "metric_name": "f1_score", "value": 0.75},
        ]
        
        response = client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3


class TestMetricRetrieval:
    """Test metric retrieval endpoint"""
    
    def test_get_all_metrics(self, client, experiment):
        """Test getting all metrics"""
        # Log some metrics
        metrics = [
            {"step": i, "metric_name": "loss", "value": 1.0 - (i * 0.01)}
            for i in range(10)
        ]
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        # Get metrics
        response = client.get(f"/experiments/{experiment['id']}/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 10
        assert all("step" in m for m in data)
        assert all("metric_name" in m for m in data)
        assert all("value" in m for m in data)
    
    def test_get_metrics_empty(self, client, experiment):
        """Test getting metrics when none exist"""
        response = client.get(f"/experiments/{experiment['id']}/metrics")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_metrics_filter_by_name(self, client, experiment):
        """Test filtering metrics by name"""
        # Log different metrics
        metrics = [
            {"step": 0, "metric_name": "loss", "value": 0.5},
            {"step": 0, "metric_name": "accuracy", "value": 0.85},
            {"step": 1, "metric_name": "loss", "value": 0.4},
            {"step": 1, "metric_name": "accuracy", "value": 0.87},
        ]
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        # Filter by loss
        response = client.get(
            f"/experiments/{experiment['id']}/metrics?metric_name=loss"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert all(m["metric_name"] == "loss" for m in data)
    
    def test_get_metrics_pagination(self, client, experiment):
        """Test pagination with limit and offset"""
        # Log 50 metrics
        metrics = [
            {"step": i, "metric_name": "loss", "value": 0.5}
            for i in range(50)
        ]
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        # Get first 10
        response = client.get(
            f"/experiments/{experiment['id']}/metrics?limit=10&offset=0"
        )
        assert response.status_code == 200
        assert len(response.json()) == 10
        
        # Get next 10
        response = client.get(
            f"/experiments/{experiment['id']}/metrics?limit=10&offset=10"
        )
        assert response.status_code == 200
        assert len(response.json()) == 10
        
        # Get last 10
        response = client.get(
            f"/experiments/{experiment['id']}/metrics?limit=10&offset=40"
        )
        assert response.status_code == 200
        assert len(response.json()) == 10
    
    def test_get_metrics_default_limit(self, client, experiment):
        """Test default limit of 1000"""
        # Log 1500 metrics
        metrics = [
            {"step": i, "metric_name": "loss", "value": 0.5}
            for i in range(1500)
        ]
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        # Get without limit (should default to 1000)
        response = client.get(f"/experiments/{experiment['id']}/metrics")
        assert response.status_code == 200
        assert len(response.json()) == 1000
    
    def test_get_metrics_ordered_by_step(self, client, experiment):
        """Test metrics are ordered by step"""
        # Log in random order
        metrics = [
            {"step": 5, "metric_name": "loss", "value": 0.5},
            {"step": 1, "metric_name": "loss", "value": 0.9},
            {"step": 3, "metric_name": "loss", "value": 0.7},
        ]
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        response = client.get(f"/experiments/{experiment['id']}/metrics")
        data = response.json()
        
        steps = [m["step"] for m in data]
        assert steps == sorted(steps)
    
    def test_get_metrics_nonexistent_experiment(self, client):
        """Test 404 for nonexistent experiment"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/experiments/{fake_uuid}/metrics")
        assert response.status_code == 404


class TestMetricSummary:
    """Test metric summary endpoint"""
    
    def test_get_metrics_summary(self, client, experiment):
        """Test getting metric summary statistics"""
        # Log metrics with known values
        metrics = [
            {"step": i, "metric_name": "loss", "value": float(i + 1)}
            for i in range(5)
        ]  # Values: 1, 2, 3, 4, 5
        
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        response = client.get(f"/experiments/{experiment['id']}/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        summary = data[0]
        
        assert summary["metric_name"] == "loss"
        assert summary["min"] == 1.0
        assert summary["max"] == 5.0
        assert summary["mean"] == 3.0  # (1+2+3+4+5)/5
        assert summary["latest"] == 5.0  # Last value at step 4
        assert summary["count"] == 5
    
    def test_get_metrics_summary_multiple_metrics(self, client, experiment):
        """Test summary with multiple metric types"""
        metrics = [
            # Loss metrics
            {"step": 0, "metric_name": "loss", "value": 1.0},
            {"step": 1, "metric_name": "loss", "value": 0.5},
            {"step": 2, "metric_name": "loss", "value": 0.3},
            # Accuracy metrics
            {"step": 0, "metric_name": "accuracy", "value": 0.5},
            {"step": 1, "metric_name": "accuracy", "value": 0.7},
            {"step": 2, "metric_name": "accuracy", "value": 0.9},
        ]
        
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        response = client.get(f"/experiments/{experiment['id']}/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        
        # Find loss and accuracy summaries
        loss_summary = next(m for m in data if m["metric_name"] == "loss")
        acc_summary = next(m for m in data if m["metric_name"] == "accuracy")
        
        # Verify loss
        assert loss_summary["min"] == 0.3
        assert loss_summary["max"] == 1.0
        assert loss_summary["latest"] == 0.3
        
        # Verify accuracy
        assert acc_summary["min"] == 0.5
        assert acc_summary["max"] == 0.9
        assert acc_summary["latest"] == 0.9
    
    def test_get_metrics_summary_empty(self, client, experiment):
        """Test summary when no metrics exist"""
        response = client.get(f"/experiments/{experiment['id']}/metrics/summary")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_metrics_summary_nonexistent_experiment(self, client):
        """Test 404 for nonexistent experiment"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/experiments/{fake_uuid}/metrics/summary")
        assert response.status_code == 404
    
    def test_get_metrics_summary_latest_value(self, client, experiment):
        """Test that latest value is from highest step"""
        metrics = [
            {"step": 10, "metric_name": "loss", "value": 0.1},
            {"step": 5, "metric_name": "loss", "value": 0.5},
            {"step": 1, "metric_name": "loss", "value": 0.9},
        ]
        
        client.post(
            f"/experiments/{experiment['id']}/metrics",
            json={"metrics": metrics}
        )
        
        response = client.get(f"/experiments/{experiment['id']}/metrics/summary")
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["latest"] == 0.1  # From step 10


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_complete_training_workflow(self, client, experiment):
        """Test complete training workflow with metrics"""
        exp_id = experiment["id"]
        
        # Log metrics during "training"
        for epoch in range(10):
            metrics = [
                {"step": epoch, "metric_name": "train_loss", "value": 1.0 - (epoch * 0.1)},
                {"step": epoch, "metric_name": "val_loss", "value": 1.0 - (epoch * 0.08)},
                {"step": epoch, "metric_name": "accuracy", "value": 0.5 + (epoch * 0.05)},
            ]
            response = client.post(
                f"/experiments/{exp_id}/metrics",
                json={"metrics": metrics}
            )
            assert response.status_code == 200
        
        # Get summary
        summary_response = client.get(f"/experiments/{exp_id}/metrics/summary")
        assert summary_response.status_code == 200
        summary = summary_response.json()
        
        assert len(summary) == 3
        
        # Verify we have all metric types
        metric_names = {s["metric_name"] for s in summary}
        assert metric_names == {"train_loss", "val_loss", "accuracy"}
        
        # Update experiment status
        client.put(
            f"/experiments/{exp_id}/status",
            json={"status": "completed"}
        )
        
        # Verify experiment is completed
        exp_response = client.get(f"/experiments/{exp_id}")
        assert exp_response.json()["status"] == "completed"
