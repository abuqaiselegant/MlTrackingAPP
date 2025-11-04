from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, StatusUpdate, TagsUpdate


class ExperimentService:
    """Service for experiment database operations"""
    
    @staticmethod
    def create_experiment(db: Session, experiment: ExperimentCreate) -> Experiment:
        """Create a new experiment with status 'running'"""
        db_experiment = Experiment(
            name=experiment.name,
            status="running",
            hyperparameters=experiment.hyperparameters,
            tags=experiment.tags
        )
        db.add(db_experiment)
        db.commit()
        db.refresh(db_experiment)
        return db_experiment
    
    @staticmethod
    def get_experiment(db: Session, experiment_id: UUID) -> Optional[Experiment]:
        """Get a single experiment by ID"""
        return db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    @staticmethod
    def get_experiments(
        db: Session,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None
    ) -> List[Experiment]:
        """Get experiments with pagination and optional status filter"""
        query = db.query(Experiment)
        
        if status:
            query = query.filter(Experiment.status == status)
        
        offset = (page - 1) * size
        return query.offset(offset).limit(size).all()
    
    @staticmethod
    def update_status(
        db: Session,
        experiment_id: UUID,
        status_update: StatusUpdate
    ) -> Optional[Experiment]:
        """Update experiment status"""
        db_experiment = db.query(Experiment).filter(
            Experiment.id == experiment_id
        ).first()
        
        if db_experiment:
            db_experiment.status = status_update.status
            db.commit()
            db.refresh(db_experiment)
        
        return db_experiment
    
    @staticmethod
    def get_experiments_by_ids(db: Session, ids: List[UUID]) -> List[Experiment]:
        """Get multiple experiments by their IDs"""
        return db.query(Experiment).filter(Experiment.id.in_(ids)).all()
    
    @staticmethod
    def update_tags(
        db: Session,
        experiment_id: UUID,
        tags_update: TagsUpdate
    ) -> Optional[Experiment]:
        """Update experiment tags"""
        db_experiment = db.query(Experiment).filter(
            Experiment.id == experiment_id
        ).first()
        
        if db_experiment:
            db_experiment.tags = tags_update.tags
            db.commit()
            db.refresh(db_experiment)
        
        return db_experiment
    
    @staticmethod
    def delete_experiment(db: Session, experiment_id: UUID) -> bool:
        """Delete an experiment and all its associated data"""
        db_experiment = db.query(Experiment).filter(
            Experiment.id == experiment_id
        ).first()
        
        if db_experiment:
            db.delete(db_experiment)
            db.commit()
            return True
        
        return False
