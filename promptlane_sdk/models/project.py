"""
Project models
"""

import uuid
from typing import Optional, List
from pydantic import Field

from .base import BaseModel, BaseCreateModel, BaseUpdateModel


class Project(BaseModel):
    """Project model"""
    
    name: str
    key: str
    description: Optional[str] = None
    team_id: uuid.UUID


class ProjectCreate(BaseCreateModel):
    """Model for creating projects"""
    
    name: str
    key: str
    description: Optional[str] = None
    team_id: uuid.UUID


class ProjectUpdate(BaseUpdateModel):
    """Model for updating projects"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[uuid.UUID] = None 