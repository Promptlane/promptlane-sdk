"""
Activity models
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field

from .base import BaseModel


class Activity(BaseModel):
    """Activity model"""
    
    user_id: uuid.UUID
    activity_type: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None 