"""
Team models
"""

import uuid
from typing import Optional, List
from pydantic import Field

from .base import BaseModel, BaseCreateModel, BaseUpdateModel


class Team(BaseModel):
    """Team model"""
    
    name: str
    description: Optional[str] = None


class TeamCreate(BaseCreateModel):
    """Model for creating teams"""
    
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseUpdateModel):
    """Model for updating teams"""
    
    name: Optional[str] = None
    description: Optional[str] = None 