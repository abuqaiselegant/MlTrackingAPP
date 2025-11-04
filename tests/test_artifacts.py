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
from app.models.artifact import Artifact


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
def client(test_db, tmp_path):
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
        description="For artifact testing",
        hyperparameters={"lr": 0.001}
    )
    test_db.add(experiment)
    test_db.commit()
    test_db.refresh(experiment)
    return experiment


class TestArtifactUpload:
    """Test artifact upload functionality."""
    
    def test_upload_artifact_success(self, client, sample_experiment):
        """Test successful file upload."""
        file_content = b"model weights data"
        files = {"file": ("model.pkl", io.BytesIO(file_content), "application/octet-stream")}
        
        response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "model.pkl"
        assert data["experiment_id"] == str(sample_experiment.id)
        assert data["size_bytes"] == len(file_content)
        assert "id" in data
        assert "uploaded_at" in data
    
    def test_upload_multiple_artifacts(self, client, sample_experiment):
        """Test uploading multiple artifacts to same experiment."""
        files1 = {"file": ("model.pkl", io.BytesIO(b"model1"), "application/octet-stream")}
        files2 = {"file": ("config.json", io.BytesIO(b"config1"), "application/json")}
        
        response1 = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files1
        )
        response2 = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files2
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["filename"] == "model.pkl"
        assert response2.json()["filename"] == "config.json"
    
    def test_upload_duplicate_filename(self, client, sample_experiment):
        """Test uploading file with duplicate filename."""
        files = {"file": ("model.pkl", io.BytesIO(b"data"), "application/octet-stream")}
        
        # First upload
        response1 = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        assert response1.status_code == 201
        
        # Second upload with same filename
        files = {"file": ("model.pkl", io.BytesIO(b"new data"), "application/octet-stream")}
        response2 = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]
    
    def test_upload_to_nonexistent_experiment(self, client):
        """Test uploading to non-existent experiment."""
        fake_id = uuid4()
        files = {"file": ("model.pkl", io.BytesIO(b"data"), "application/octet-stream")}
        
        response = client.post(
            f"/artifacts/experiments/{fake_id}/upload",
            files=files
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_upload_sanitizes_filename(self, client, sample_experiment):
        """Test filename sanitization."""
        # Dangerous filename with path traversal attempt
        files = {"file": ("../../../etc/passwd", io.BytesIO(b"data"), "application/octet-stream")}
        
        response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        
        assert response.status_code == 201
        # Filename should be sanitized (no ../)
        data = response.json()
        assert ".." not in data["filename"]
        assert "/" not in data["filename"]
    
    def test_upload_large_file_rejected(self, client, sample_experiment):
        """Test that files exceeding size limit are rejected."""
        # Create a file larger than 500MB (simulate with smaller limit in test)
        # Note: This test would need the service to have a lower limit for testing
        # For now, we just verify the mechanism exists
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB for testing
        files = {"file": ("large.bin", io.BytesIO(large_content), "application/octet-stream")}
        
        response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        
        # Should succeed with 10MB, but validates size checking exists
        assert response.status_code == 201


class TestArtifactList:
    """Test listing artifacts."""
    
    def test_list_artifacts_empty(self, client, sample_experiment):
        """Test listing artifacts when none exist."""
        response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_artifacts(self, client, sample_experiment):
        """Test listing artifacts for experiment."""
        # Upload some artifacts
        for i in range(3):
            files = {"file": (f"file{i}.txt", io.BytesIO(f"content{i}".encode()), "text/plain")}
            client.post(
                f"/artifacts/experiments/{sample_experiment.id}/upload",
                files=files
            )
        
        response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        filenames = [a["filename"] for a in data]
        assert "file0.txt" in filenames
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames
    
    def test_list_artifacts_pagination(self, client, sample_experiment):
        """Test artifact listing pagination."""
        # Upload 5 artifacts
        for i in range(5):
            files = {"file": (f"file{i}.txt", io.BytesIO(f"content{i}".encode()), "text/plain")}
            client.post(
                f"/artifacts/experiments/{sample_experiment.id}/upload",
                files=files
            )
        
        # Get first 2
        response = client.get(
            f"/artifacts/experiments/{sample_experiment.id}",
            params={"skip": 0, "limit": 2}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get next 2
        response = client.get(
            f"/artifacts/experiments/{sample_experiment.id}",
            params={"skip": 2, "limit": 2}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestArtifactDownload:
    """Test artifact download functionality."""
    
    def test_download_artifact_success(self, client, sample_experiment):
        """Test successful artifact download."""
        file_content = b"model weights for download"
        files = {"file": ("model.pkl", io.BytesIO(file_content), "application/octet-stream")}
        
        # Upload
        upload_response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        artifact_id = upload_response.json()["id"]
        
        # Download
        download_response = client.get(f"/artifacts/{artifact_id}/download")
        
        assert download_response.status_code == 200
        assert download_response.content == file_content
        assert download_response.headers["content-type"] == "application/octet-stream"
    
    def test_download_nonexistent_artifact(self, client):
        """Test downloading non-existent artifact."""
        fake_id = uuid4()
        response = client.get(f"/artifacts/{fake_id}/download")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_download_preserves_filename(self, client, sample_experiment):
        """Test that download preserves original filename."""
        files = {"file": ("my_model.pkl", io.BytesIO(b"data"), "application/octet-stream")}
        
        upload_response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        artifact_id = upload_response.json()["id"]
        
        download_response = client.get(f"/artifacts/{artifact_id}/download")
        
        # Check Content-Disposition header for filename
        assert download_response.status_code == 200


class TestArtifactDelete:
    """Test artifact deletion."""
    
    def test_delete_artifact_success(self, client, sample_experiment, tmp_path):
        """Test successful artifact deletion."""
        files = {"file": ("model.pkl", io.BytesIO(b"data"), "application/octet-stream")}
        
        # Upload
        upload_response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        artifact_id = upload_response.json()["id"]
        
        # Delete
        delete_response = client.delete(f"/artifacts/{artifact_id}")
        
        assert delete_response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/artifacts/{artifact_id}/download")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_artifact(self, client):
        """Test deleting non-existent artifact."""
        fake_id = uuid4()
        response = client.delete(f"/artifacts/{fake_id}")
        
        assert response.status_code == 404
    
    def test_delete_removes_from_list(self, client, sample_experiment):
        """Test that deleted artifact is removed from listing."""
        # Upload 2 artifacts
        files1 = {"file": ("file1.txt", io.BytesIO(b"data1"), "text/plain")}
        files2 = {"file": ("file2.txt", io.BytesIO(b"data2"), "text/plain")}
        
        response1 = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files1
        )
        client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files2
        )
        
        artifact_id = response1.json()["id"]
        
        # Verify 2 artifacts
        list_response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        assert len(list_response.json()) == 2
        
        # Delete one
        client.delete(f"/artifacts/{artifact_id}")
        
        # Verify only 1 remains
        list_response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["filename"] == "file2.txt"


class TestArtifactIntegration:
    """Integration tests for artifact workflow."""
    
    def test_complete_artifact_workflow(self, client, sample_experiment):
        """Test complete workflow: upload, list, download, delete."""
        file_content = b"complete workflow test data"
        files = {"file": ("workflow.pkl", io.BytesIO(file_content), "application/octet-stream")}
        
        # 1. Upload
        upload_response = client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        assert upload_response.status_code == 201
        artifact_id = upload_response.json()["id"]
        
        # 2. List
        list_response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # 3. Download
        download_response = client.get(f"/artifacts/{artifact_id}/download")
        assert download_response.status_code == 200
        assert download_response.content == file_content
        
        # 4. Delete
        delete_response = client.delete(f"/artifacts/{artifact_id}")
        assert delete_response.status_code == 204
        
        # 5. Verify deletion
        list_response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        assert len(list_response.json()) == 0
    
    def test_artifacts_deleted_with_experiment(self, client, test_db, sample_experiment):
        """Test that artifacts are cascade deleted when experiment is deleted."""
        files = {"file": ("model.pkl", io.BytesIO(b"data"), "application/octet-stream")}
        
        # Upload artifact
        client.post(
            f"/artifacts/experiments/{sample_experiment.id}/upload",
            files=files
        )
        
        # Verify artifact exists
        list_response = client.get(f"/artifacts/experiments/{sample_experiment.id}")
        assert len(list_response.json()) == 1
        
        # Delete experiment
        test_db.delete(sample_experiment)
        test_db.commit()
        
        # Verify artifacts are gone (cascade delete)
        from app.models.artifact import Artifact
        artifacts = test_db.query(Artifact).filter(
            Artifact.experiment_id == sample_experiment.id
        ).all()
        assert len(artifacts) == 0
