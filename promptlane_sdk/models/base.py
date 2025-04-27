"""
Base models for PromptLane SDK
"""

import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """Base model for all PromptLane models"""
    
    id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    
    class Config:
        """Configuration for all models"""
        orm_mode = True  # Allow population from ORM objects


class BaseCreateModel(PydanticBaseModel):
    """Base model for creating resources"""
    pass


class BaseUpdateModel(PydanticBaseModel):
    """Base model for updating resources"""
    pass 