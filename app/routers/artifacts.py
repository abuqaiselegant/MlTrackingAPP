from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pathlib import Path

from app.database import get_db
from app.services.artifact_service import ArtifactService
from app.schemas.artifact import ArtifactResponse
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.post(
    "/experiments/{experiment_id}/upload",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_artifact(
    experiment_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a file artifact for an experiment."""
    artifact = await ArtifactService.save_artifact(
        db=db,
        experiment_id=experiment_id,
        file=file,
        artifacts_path=settings.ARTIFACTS_PATH
    )
    return artifact


@router.get("/experiments/{experiment_id}", response_model=List[ArtifactResponse])
def list_artifacts(
    experiment_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all artifacts for an experiment."""
    artifacts = ArtifactService.list_artifacts(
        db=db,
        experiment_id=experiment_id,
        skip=skip,
        limit=limit
    )
    return artifacts


@router.get("/{artifact_id}/download")
async def download_artifact(
    artifact_id: UUID,
    db: Session = Depends(get_db)
):
    """Download an artifact file."""
    artifact = ArtifactService.get_artifact(db=db, artifact_id=artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact {artifact_id} not found"
        )
    
    file_path = Path(artifact.filepath)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact file not found on disk"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=artifact.filename,
        media_type="application/octet-stream"
    )


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(
    artifact_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an artifact."""
    success = ArtifactService.delete_artifact(db=db, artifact_id=artifact_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact {artifact_id} not found"
        )
