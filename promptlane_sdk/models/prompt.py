"""
Prompt models
"""

import uuid
from typing import Optional, List
from pydantic import Field

from .base import BaseModel, BaseCreateModel, BaseUpdateModel


class Prompt(BaseModel):
    """Prompt model"""
    
    name: str
    key: str
    description: Optional[str] = None
    system_prompt: str
    user_prompt: str
    is_active: bool = True
    version: int = 1
    project_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None


class PromptCreate(BaseCreateModel):
    """Model for creating prompts"""
    
    name: str
    key: str
    description: Optional[str] = None
    system_prompt: str
    user_prompt: str
    is_active: bool = True
    project_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None


class PromptUpdate(BaseUpdateModel):
    """Model for updating prompts"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    is_active: Optional[bool] = None 