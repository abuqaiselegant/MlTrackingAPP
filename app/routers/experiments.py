from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentResponse,
    StatusUpdate,
    TagsUpdate
)
from app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    experiment: ExperimentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new experiment.
    
    - **name**: Experiment name (required, max 200 chars)
    - **hyperparameters**: Dictionary of hyperparameters (default: {})
    - Status is automatically set to "running"
    """
    return ExperimentService.create_experiment(db, experiment)


@router.get("", response_model=List[ExperimentResponse])
def list_experiments(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=50, ge=1, le=100, description="Page size"),
    status: str = Query(
        default=None,
        pattern="^(running|completed|failed)$",
        description="Filter by status"
    ),
    db: Session = Depends(get_db)
):
    """
    List experiments with pagination and optional status filter.
    
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 50, max: 100)
    - **status**: Filter by status (optional: running, completed, failed)
    """
    return ExperimentService.get_experiments(db, page, size, status)


@router.get("/compare", response_model=List[ExperimentResponse])
def compare_experiments(
    ids: str = Query(..., description="Comma-separated experiment IDs"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple experiments by their IDs.
    
    - **ids**: Comma-separated list of experiment UUIDs
    
    Returns list of experiments with their hyperparameters.
    """
    try:
        # Parse comma-separated UUIDs
        experiment_ids = [UUID(id.strip()) for id in ids.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format in ids parameter"
        )
    
    experiments = ExperimentService.get_experiments_by_ids(db, experiment_ids)
    
    if not experiments:
        raise HTTPException(
            status_code=404,
            detail="No experiments found with the provided IDs"
        )
    
    return experiments


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single experiment by ID.
    
    Returns 404 if experiment not found.
    """
    experiment = ExperimentService.get_experiment(db, experiment_id)
    
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    return experiment


@router.put("/{experiment_id}/status", response_model=ExperimentResponse)
def update_experiment_status(
    experiment_id: UUID,
    status_update: StatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update experiment status.
    
    - **status**: New status (running, completed, or failed)
    
    Returns 404 if experiment not found.
    """
    experiment = ExperimentService.update_status(db, experiment_id, status_update)
    
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    return experiment


@router.put("/{experiment_id}/tags", response_model=ExperimentResponse)
def update_experiment_tags(
    experiment_id: UUID,
    tags_update: TagsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update experiment tags.
    
    - **tags**: List of tags for the experiment
    
    Returns 404 if experiment not found.
    """
    experiment = ExperimentService.update_tags(db, experiment_id, tags_update)
    
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    return experiment


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an experiment and all its associated data.
    
    Returns 404 if experiment not found.
    """
    success = ExperimentService.delete_experiment(db, experiment_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
