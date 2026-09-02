"""
Analysis models.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class AnalysisResultModel(BaseModel):
    result_id: str
    project_id: str
    user_id: str
    url: str
    status: str = "in progress"
    score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class AnalysisStartResponse(BaseModel):
    message: str
    result_id: str
    queued_at: datetime
