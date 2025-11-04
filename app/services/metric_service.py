from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.metric import Metric
from app.schemas.metric import MetricCreate


class MetricService:
    """Service for metric database operations"""
    
    @staticmethod
    def log_metrics_bulk(
        db: Session,
        experiment_id: UUID,
        metrics: List[MetricCreate]
    ) -> int:
        """Bulk insert metrics for an experiment"""
        db_metrics = [
            Metric(
                experiment_id=experiment_id,
                step=metric.step,
                metric_name=metric.metric_name,
                value=metric.value
            )
            for metric in metrics
        ]
        
        db.bulk_save_objects(db_metrics)
        db.commit()
        return len(db_metrics)
    
    @staticmethod
    def get_metrics(
        db: Session,
        experiment_id: UUID,
        metric_name: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Metric]:
        """Get metrics for an experiment with optional filtering"""
        query = db.query(Metric).filter(Metric.experiment_id == experiment_id)
        
        if metric_name:
            query = query.filter(Metric.metric_name == metric_name)
        
        return query.order_by(Metric.step).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_metrics_summary(
        db: Session,
        experiment_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get aggregated summary statistics per metric using SQL GROUP BY"""
        # Subquery to get latest value per metric
        latest_subquery = (
            db.query(
                Metric.metric_name,
                Metric.value.label('latest_value')
            )
            .filter(Metric.experiment_id == experiment_id)
            .distinct(Metric.metric_name)
            .order_by(Metric.metric_name, desc(Metric.step))
            .subquery()
        )
        
        # Main query with aggregations
        results = (
            db.query(
                Metric.metric_name,
                func.min(Metric.value).label('min'),
                func.max(Metric.value).label('max'),
                func.avg(Metric.value).label('mean'),
                func.count(Metric.id).label('count'),
                latest_subquery.c.latest_value.label('latest')
            )
            .filter(Metric.experiment_id == experiment_id)
            .outerjoin(
                latest_subquery,
                Metric.metric_name == latest_subquery.c.metric_name
            )
            .group_by(
                Metric.metric_name,
                latest_subquery.c.latest_value
            )
            .all()
        )
        
        return [
            {
                'metric_name': r.metric_name,
                'min': float(r.min),
                'max': float(r.max),
                'mean': float(r.mean),
                'latest': float(r.latest),
                'count': r.count
            }
            for r in results
        ]
