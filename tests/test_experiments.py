import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import UUID

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


class TestExperimentCreation:
    """Test experiment creation endpoint"""
    
    def test_create_experiment_minimal(self, client):
        """Test creating experiment with minimal data"""
        response = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        )
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Test Experiment"
        assert data["status"] == "running"
        assert data["hyperparameters"] == {}
        assert "id" in data
        assert "created_at" in data
        
        # Verify UUID format
        UUID(data["id"])
    
    def test_create_experiment_with_hyperparameters(self, client):
        """Test creating experiment with hyperparameters"""
        response = client.post(
            "/experiments",
            json={
                "name": "CNN Training",
                "hyperparameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 100
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "CNN Training"
        assert data["hyperparameters"]["learning_rate"] == 0.001
        assert data["hyperparameters"]["batch_size"] == 32
        assert data["hyperparameters"]["epochs"] == 100
    
    def test_create_experiment_name_too_long(self, client):
        """Test validation for name length"""
        long_name = "A" * 201
        response = client.post(
            "/experiments",
            json={"name": long_name}
        )
        assert response.status_code == 422
    
    def test_create_experiment_missing_name(self, client):
        """Test validation for missing name"""
        response = client.post(
            "/experiments",
            json={}
        )
        assert response.status_code == 422


class TestExperimentRetrieval:
    """Test experiment retrieval endpoints"""
    
    def test_get_experiment_by_id(self, client):
        """Test getting a single experiment"""
        # Create experiment
        create_response = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        )
        experiment_id = create_response.json()["id"]
        
        # Get experiment
        response = client.get(f"/experiments/{experiment_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == experiment_id
        assert data["name"] == "Test Experiment"
    
    def test_get_nonexistent_experiment(self, client):
        """Test 404 for nonexistent experiment"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/experiments/{fake_uuid}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_experiment_invalid_uuid(self, client):
        """Test 422 for invalid UUID format"""
        response = client.get("/experiments/invalid-uuid")
        assert response.status_code == 422


class TestExperimentListing:
    """Test experiment listing with pagination and filters"""
    
    def test_list_experiments_empty(self, client):
        """Test listing when no experiments exist"""
        response = client.get("/experiments")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_experiments(self, client):
        """Test listing experiments"""
        # Create multiple experiments
        for i in range(3):
            client.post("/experiments", json={"name": f"Experiment {i}"})
        
        response = client.get("/experiments")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 3
        assert all("id" in exp for exp in data)
    
    def test_list_experiments_pagination(self, client):
        """Test pagination"""
        # Create 5 experiments
        for i in range(5):
            client.post("/experiments", json={"name": f"Experiment {i}"})
        
        # Get first page with size 2
        response = client.get("/experiments?page=1&size=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get second page
        response = client.get("/experiments?page=2&size=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get third page
        response = client.get("/experiments?page=3&size=2")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_list_experiments_filter_by_status(self, client):
        """Test filtering by status"""
        # Create experiments
        exp1 = client.post("/experiments", json={"name": "Exp 1"}).json()
        exp2 = client.post("/experiments", json={"name": "Exp 2"}).json()
        
        # Update one to completed
        client.put(
            f"/experiments/{exp1['id']}/status",
            json={"status": "completed"}
        )
        
        # Filter by running
        response = client.get("/experiments?status=running")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "running"
        
        # Filter by completed
        response = client.get("/experiments?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"
    
    def test_list_experiments_invalid_status(self, client):
        """Test validation for invalid status filter"""
        response = client.get("/experiments?status=invalid")
        assert response.status_code == 422
    
    def test_list_experiments_pagination_limits(self, client):
        """Test pagination parameter validation"""
        # Invalid page number
        response = client.get("/experiments?page=0")
        assert response.status_code == 422
        
        # Size too large
        response = client.get("/experiments?size=101")
        assert response.status_code == 422


class TestExperimentStatusUpdate:
    """Test experiment status update endpoint"""
    
    def test_update_status_to_completed(self, client):
        """Test updating status to completed"""
        # Create experiment
        create_response = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        )
        experiment_id = create_response.json()["id"]
        
        # Update status
        response = client.put(
            f"/experiments/{experiment_id}/status",
            json={"status": "completed"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "completed"
        assert data["id"] == experiment_id
    
    def test_update_status_to_failed(self, client):
        """Test updating status to failed"""
        create_response = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        )
        experiment_id = create_response.json()["id"]
        
        response = client.put(
            f"/experiments/{experiment_id}/status",
            json={"status": "failed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
    
    def test_update_status_invalid_value(self, client):
        """Test validation for invalid status"""
        create_response = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        )
        experiment_id = create_response.json()["id"]
        
        response = client.put(
            f"/experiments/{experiment_id}/status",
            json={"status": "invalid"}
        )
        assert response.status_code == 422
    
    def test_update_status_nonexistent_experiment(self, client):
        """Test 404 for updating nonexistent experiment"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.put(
            f"/experiments/{fake_uuid}/status",
            json={"status": "completed"}
        )
        assert response.status_code == 404


class TestExperimentComparison:
    """Test experiment comparison endpoint"""
    
    def test_compare_experiments(self, client):
        """Test comparing multiple experiments"""
        # Create experiments with different hyperparameters
        exp1 = client.post(
            "/experiments",
            json={
                "name": "Experiment 1",
                "hyperparameters": {"learning_rate": 0.001, "batch_size": 32}
            }
        ).json()
        
        exp2 = client.post(
            "/experiments",
            json={
                "name": "Experiment 2",
                "hyperparameters": {"learning_rate": 0.01, "batch_size": 64}
            }
        ).json()
        
        # Compare experiments
        ids = f"{exp1['id']},{exp2['id']}"
        response = client.get(f"/experiments/compare?ids={ids}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert data[0]["hyperparameters"]["learning_rate"] == 0.001
        assert data[1]["hyperparameters"]["learning_rate"] == 0.01
    
    def test_compare_single_experiment(self, client):
        """Test comparing with single ID"""
        exp = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        ).json()
        
        response = client.get(f"/experiments/compare?ids={exp['id']}")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_compare_invalid_uuid(self, client):
        """Test 400 for invalid UUID format"""
        response = client.get("/experiments/compare?ids=invalid-uuid")
        assert response.status_code == 400
        assert "invalid uuid" in response.json()["detail"].lower()
    
    def test_compare_nonexistent_experiments(self, client):
        """Test 404 when no experiments found"""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/experiments/compare?ids={fake_uuid}")
        assert response.status_code == 404
    
    def test_compare_mixed_valid_invalid_ids(self, client):
        """Test with mix of valid and invalid IDs"""
        exp = client.post(
            "/experiments",
            json={"name": "Test Experiment"}
        ).json()
        
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        ids = f"{exp['id']},{fake_uuid}"
        
        response = client.get(f"/experiments/compare?ids={ids}")
        assert response.status_code == 200
        # Should only return the one that exists
        assert len(response.json()) == 1
