"""
User models
"""

import uuid
from enum import Enum
from typing import Optional, List
from pydantic import Field, EmailStr

from .base import BaseModel, BaseCreateModel, BaseUpdateModel


class UserStatus(str, Enum):
    """User status enum"""
    ACTIVE = "active"
    INVITED = "invited"
    DISABLED = "disabled"


class User(BaseModel):
    """User model"""
    
    username: Optional[str] = None
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    status: UserStatus = UserStatus.ACTIVE
    invitation_token: Optional[str] = None
    invitation_expiry: Optional[str] = None


class UserCreate(BaseCreateModel):
    """Model for creating users"""
    
    username: Optional[str] = None
    email: str
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


class UserUpdate(BaseUpdateModel):
    """Model for updating users"""
    
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    status: Optional[UserStatus] = None 