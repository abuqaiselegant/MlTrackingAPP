from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    hyperparameters = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True, default=list)  # Store tags as JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    metrics = relationship("Metric", back_populates="experiment", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="experiment", cascade="all, delete-orphan")
