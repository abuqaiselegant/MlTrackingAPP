import os
import re
from pathlib import Path
from uuid import UUID
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.experiment import Experiment


class ArtifactService:
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal and invalid chars."""
        # Remove path components
        filename = os.path.basename(filename)
        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '_', filename)
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        # Ensure filename is not empty
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        return filename
    
    @staticmethod
    async def save_artifact(
        db: Session,
        experiment_id: UUID,
        file: UploadFile,
        artifacts_path: str
    ) -> Artifact:
        """Save uploaded file and create artifact record."""
        # Check if experiment exists
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Experiment {experiment_id} not found"
            )
        
        # Sanitize filename
        safe_filename = ArtifactService.sanitize_filename(file.filename)
        
        # Create experiment directory
        exp_dir = Path(artifacts_path) / str(experiment_id)
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = exp_dir / safe_filename
        
        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Artifact with filename '{safe_filename}' already exists"
            )
        
        # Write file in chunks and track size
        total_size = 0
        try:
            with open(file_path, "wb") as f:
                while chunk := await file.read(ArtifactService.CHUNK_SIZE):
                    total_size += len(chunk)
                    if total_size > ArtifactService.MAX_FILE_SIZE:
                        f.close()
                        file_path.unlink()  # Delete partial file
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File size exceeds {ArtifactService.MAX_FILE_SIZE / (1024*1024)}MB limit"
                        )
                    f.write(chunk)
        except Exception as e:
            # Clean up partial file on error
            if file_path.exists():
                file_path.unlink()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Create artifact record
        artifact = Artifact(
            experiment_id=experiment_id,
            filename=safe_filename,
            filepath=str(file_path),
            size_bytes=total_size
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        
        return artifact
    
    @staticmethod
    def get_artifact(db: Session, artifact_id: UUID) -> Optional[Artifact]:
        """Get artifact by ID."""
        return db.query(Artifact).filter(Artifact.id == artifact_id).first()
    
    @staticmethod
    def list_artifacts(
        db: Session,
        experiment_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Artifact]:
        """List artifacts for an experiment."""
        return (
            db.query(Artifact)
            .filter(Artifact.experiment_id == experiment_id)
            .order_by(Artifact.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def delete_artifact(db: Session, artifact_id: UUID) -> bool:
        """Delete artifact record and file."""
        artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            return False
        
        # Delete file from disk
        file_path = Path(artifact.filepath)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass  # Continue even if file deletion fails
        
        # Delete database record
        db.delete(artifact)
        db.commit()
        
        return True
