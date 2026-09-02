"""
Project models.
"""
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional


class ProjectModel(BaseModel):
    project_id: Optional[str] = None
    name: str
    url: Optional[HttpUrl] = None
    creation_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    owner_id: Optional[str] = None
    description: Optional[str] = ""
    analysis_result_ids: List[str] = []
    feedback_ids: List[str] = []
    is_public: bool = False
    tags: List[str] = []

    def dict(self, *args, **kwargs):
        project_dict = super().model_dump(*args, **kwargs)
        project_dict["url"] = str(self.url) if self.url else None
        return project_dict


class ProjectCreate(BaseModel):
    name: str
    url: Optional[HttpUrl] = None
    description: Optional[str] = ""
    is_public: bool = False
    tags: List[str] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
