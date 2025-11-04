from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List
import math


class MetricCreate(BaseModel):
    step: int = Field(..., ge=0)
    metric_name: str = Field(..., max_length=100)
    value: float
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Value must not be NaN or infinity")
        return v


class MetricBatchCreate(BaseModel):
    metrics: List[MetricCreate] = Field(..., max_length=1000)


class MetricResponse(BaseModel):
    id: int
    experiment_id: UUID
    step: int
    metric_name: str
    value: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MetricLogResponse(BaseModel):
    count: int
    message: str


class MetricSummary(BaseModel):
    metric_name: str
    min: float
    max: float
    mean: float
    latest: float
    count: int
