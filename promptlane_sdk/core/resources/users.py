"""
Users resource for PromptLane SDK

This module implements the Users resource with write-through API pattern. 
All write operations (create, update, delete) are forced through the API
regardless of connection type to ensure consistent validation and business logic.
"""

from typing import Union, List, Optional, Dict, Any
import uuid
import logging

from .base import ResourceBase, WriteThruAPIResourceMixin
from ...models.user import User, UserCreate, UserUpdate
from ...models.team import Team
from ...api.exceptions import APIError, NotFoundError
from ..utils.decorators import api_write_only

# Configure logger
logger = logging.getLogger(__name__)


class Users(ResourceBase, WriteThruAPIResourceMixin):
    """
    Client for interacting with PromptLane users
    
    This resource follows a "write-through API" pattern:
    - Read operations may use either database or API
    - Write operations always use the API regardless of connection type
    
    This ensures validation rules and business logic in the API are always applied.
    """
    
    model_class = User
    create_model_class = UserCreate
    update_model_class = UserUpdate
    resource_name = "users"
    
    def get_teams(self, user_id: Union[str, uuid.UUID]) -> List[Team]:
        """
        Get all teams a user belongs to
        
        Args:
            user_id: ID or key of the user
            
        Returns:
            List of teams the user belongs to
            
        Raises:
            NotFoundError: If the user is not found
            APIError: For API-related errors
        """
        user_id = self._get_id_from_arg(user_id)
        
        try:
            if self.db and not self.mixed_mode:
                return self.db.get_user_teams(user_id)
            else:
                return self.api.list(f"{self.resource_name}/{user_id}/teams", Team)
        except NotFoundError:
            logger.error(f"User not found: {user_id}")
            raise NotFoundError(f"User with ID {user_id} not found")
        except Exception as e:
            logger.exception(f"Error getting teams for user {user_id}")
            raise APIError(f"Error retrieving teams for user {user_id}: {str(e)}")
    
    @api_write_only
    def create(self, **kwargs) -> User:
        """
        Create a new user - always through API
        
        Args:
            **kwargs: User properties
            
        Returns:
            Created user
            
        Raises:
            ValidationError: If the provided data is invalid
            AuthenticationError: If not authorized to create users
            APIError: For other API-related errors
        """
        data = self.create_model_class(**kwargs)
        return self.api.create(self.resource_name, data, self.model_class)
    
    @api_write_only
    def update(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> User:
        """
        Update an existing user - always through API
        
        Args:
            id_or_key: User ID or key
            **kwargs: User properties to update
            
        Returns:
            Updated user
            
        Raises:
            NotFoundError: If the user is not found
            ValidationError: If the provided data is invalid
            AuthenticationError: If not authorized to update users
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        data = self.update_model_class(**kwargs)
        return self.api.update(self.resource_name, item_id, data, self.model_class)
    
    @api_write_only
    def delete(self, id_or_key: Union[str, uuid.UUID]) -> bool:
        """
        Delete a user - always through API
        
        Args:
            id_or_key: User ID or key
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If the user is not found
            AuthenticationError: If not authorized to delete users
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        return self.api.delete(self.resource_name, item_id)
    
    @api_write_only
    def invite(self, email: str, full_name: Optional[str] = None) -> User:
        """
        Invite a new user to PromptLane - always through API
        
        Args:
            email: User email
            full_name: User full name (optional)
            
        Returns:
            Created user (in invited state)
            
        Raises:
            ValidationError: If the provided data is invalid
            AuthenticationError: If not authorized to invite users
            APIError: For other API-related errors
        """
        data = {"email": email, "full_name": full_name}
        return self.api.create(f"{self.resource_name}/invite", data, User)
    
    @api_write_only
    def activate(self, id_or_key: Union[str, uuid.UUID]) -> User:
        """
        Activate a user - always through API
        
        Args:
            id_or_key: User ID or key
            
        Returns:
            Updated user
            
        Raises:
            NotFoundError: If the user is not found
            ValidationError: If the user is already active
            AuthenticationError: If not authorized to activate users
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        return self.api.create(f"{self.resource_name}/{item_id}/activate", {}, User)
    
    @api_write_only
    def deactivate(self, id_or_key: Union[str, uuid.UUID]) -> User:
        """
        Deactivate a user - always through API
        
        Args:
            id_or_key: User ID or key
            
        Returns:
            Updated user
            
        Raises:
            NotFoundError: If the user is not found
            ValidationError: If the user is already inactive
            AuthenticationError: If not authorized to deactivate users
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        return self.api.create(f"{self.resource_name}/{item_id}/deactivate", {}, User)
    
    @api_write_only
    def change_password(self, id_or_key: Union[str, uuid.UUID], current_password: str, new_password: str) -> bool:
        """
        Change a user's password - always through API
        
        Args:
            id_or_key: User ID or key
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If the user is not found
            ValidationError: If the passwords don't meet requirements
            AuthenticationError: If current password is incorrect
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        self.api.create(f"{self.resource_name}/{item_id}/change-password", data, Dict)
        return True 