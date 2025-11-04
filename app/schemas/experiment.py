from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ExperimentCreate(BaseModel):
    name: str = Field(..., max_length=200)
    hyperparameters: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class ExperimentResponse(BaseModel):
    id: UUID
    name: str
    status: str
    hyperparameters: dict
    tags: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(running|completed|failed)$")


class TagsUpdate(BaseModel):
    tags: List[str] = Field(..., description="List of tags for the experiment")


class ExperimentQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=100)
    status: Optional[str] = Field(None, pattern="^(running|completed|failed)$")
