from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Union
from uuid import UUID

from app.database import get_db
from app.schemas.metric import (
    MetricCreate,
    MetricBatchCreate,
    MetricResponse,
    MetricLogResponse,
    MetricSummary
)
from app.services.metric_service import MetricService
from app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["metrics"])


@router.post("/{experiment_id}/metrics", response_model=MetricLogResponse)
def log_metrics(
    experiment_id: UUID,
    data: Union[MetricCreate, MetricBatchCreate] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Log single metric or batch of metrics for an experiment.
    
    - **Single metric**: Pass MetricCreate object
    - **Batch metrics**: Pass MetricBatchCreate with list of metrics (max 1000)
    
    Uses efficient bulk insert for batches.
    Returns count of metrics logged.
    """
    # Verify experiment exists
    experiment = ExperimentService.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    # Handle single or batch metrics
    if isinstance(data, MetricBatchCreate):
        metrics = data.metrics
    else:
        metrics = [data]
    
    # Bulk insert
    count = MetricService.log_metrics_bulk(db, experiment_id, metrics)
    
    return MetricLogResponse(
        count=count,
        message=f"Successfully logged {count} metric(s)"
    )


@router.get("/{experiment_id}/metrics", response_model=List[MetricResponse])
def get_experiment_metrics(
    experiment_id: UUID,
    metric_name: str = Query(None, description="Filter by metric name"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    Get all metrics for an experiment.
    
    - **metric_name**: Optional filter by specific metric name
    - **limit**: Maximum results to return (default: 1000, max: 10000)
    - **offset**: Number of results to skip for pagination (default: 0)
    
    Results are ordered by step number.
    """
    # Verify experiment exists
    experiment = ExperimentService.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    metrics = MetricService.get_metrics(
        db, experiment_id, metric_name, limit, offset
    )
    
    return metrics


@router.get("/{experiment_id}/metrics/summary", response_model=List[MetricSummary])
def get_metrics_summary(
    experiment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics for all metrics in an experiment.
    
    Returns per-metric aggregates:
    - **min**: Minimum value
    - **max**: Maximum value
    - **mean**: Average value
    - **latest**: Most recent value (by step)
    - **count**: Number of data points
    
    Uses SQL GROUP BY for efficient aggregation.
    """
    # Verify experiment exists
    experiment = ExperimentService.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with id {experiment_id} not found"
        )
    
    summary = MetricService.get_metrics_summary(db, experiment_id)
    
    return summary
