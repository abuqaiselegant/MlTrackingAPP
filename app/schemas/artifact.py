from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ArtifactResponse(BaseModel):
    id: UUID
    experiment_id: UUID
    filename: str
    filepath: str
    size_bytes: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
