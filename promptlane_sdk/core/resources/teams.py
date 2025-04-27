"""
Teams resource for PromptLane SDK

This module implements the Teams resource with write-through API pattern.
All write operations (create, update, delete) are forced through the API
regardless of connection type to ensure consistent validation and business logic.
"""

from typing import Union, List, Dict, Any
import uuid
import logging

from .base import ResourceBase, WriteThruAPIResourceMixin
from ...models.team import Team, TeamCreate, TeamUpdate
from ...models.user import User
from ...api.exceptions import APIError, NotFoundError
from ..utils.decorators import api_write_only

# Configure logger
logger = logging.getLogger(__name__)


class Teams(ResourceBase, WriteThruAPIResourceMixin):
    """
    Client for interacting with PromptLane teams
    
    This resource follows a "write-through API" pattern:
    - Read operations may use either database or API
    - Write operations always use the API regardless of connection type
    
    This ensures validation rules and business logic in the API are always applied.
    """
    
    model_class = Team
    create_model_class = TeamCreate
    update_model_class = TeamUpdate
    resource_name = "teams"
    
    def get_members(self, team_id: Union[str, uuid.UUID]) -> List[User]:
        """
        Get all members of a team
        
        Args:
            team_id: ID or key of the team
            
        Returns:
            List of team members
            
        Raises:
            NotFoundError: If the team is not found
            APIError: For API-related errors
        """
        team_id = self._get_id_from_arg(team_id)
        
        try:
            if self.db and not self.mixed_mode:
                return self.db.get_team_members(team_id)
            else:
                return self.api.list(f"{self.resource_name}/{team_id}/members", User)
        except NotFoundError:
            logger.error(f"Team not found: {team_id}")
            raise NotFoundError(f"Team with ID {team_id} not found")
        except Exception as e:
            logger.exception(f"Error getting members for team {team_id}")
            raise APIError(f"Error retrieving members for team {team_id}: {str(e)}")
    
    @api_write_only
    def create(self, **kwargs) -> Team:
        """
        Create a new team - always through API
        
        Args:
            **kwargs: Team properties
            
        Returns:
            Created team
            
        Raises:
            ValidationError: If the provided data is invalid
            AuthenticationError: If not authorized to create teams
            APIError: For other API-related errors
        """
        data = self.create_model_class(**kwargs)
        return self.api.create(self.resource_name, data, self.model_class)
    
    @api_write_only
    def update(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> Team:
        """
        Update an existing team - always through API
        
        Args:
            id_or_key: Team ID or key
            **kwargs: Team properties to update
            
        Returns:
            Updated team
            
        Raises:
            NotFoundError: If the team is not found
            ValidationError: If the provided data is invalid
            AuthenticationError: If not authorized to update teams
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        data = self.update_model_class(**kwargs)
        return self.api.update(self.resource_name, item_id, data, self.model_class)
    
    @api_write_only
    def delete(self, id_or_key: Union[str, uuid.UUID]) -> bool:
        """
        Delete a team - always through API
        
        Args:
            id_or_key: Team ID or key
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If the team is not found
            AuthenticationError: If not authorized to delete teams
            APIError: For other API-related errors
        """
        item_id = self._get_id_from_arg(id_or_key)
        return self.api.delete(self.resource_name, item_id)
    
    @api_write_only
    def add_member(self, team_id: Union[str, uuid.UUID], user_id: Union[str, uuid.UUID], role: str) -> Any:
        """
        Add a user to a team - always through API
        
        Args:
            team_id: Team ID or key
            user_id: User ID or key
            role: Team role for the user
            
        Returns:
            Team membership information
            
        Raises:
            NotFoundError: If the team or user is not found
            ValidationError: If the role is invalid
            AuthenticationError: If not authorized to manage team members
            APIError: For other API-related errors
        """
        team_id = self._get_id_from_arg(team_id)
        user_id = self._get_id_from_arg(user_id)
        
        data = {"user_id": user_id, "role": role}
        return self.api.create(f"{self.resource_name}/{team_id}/members", data, Dict)
    
    @api_write_only
    def remove_member(self, team_id: Union[str, uuid.UUID], user_id: Union[str, uuid.UUID]) -> bool:
        """
        Remove a user from a team - always through API
        
        Args:
            team_id: Team ID or key
            user_id: User ID or key
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If the team member is not found
            AuthenticationError: If not authorized to manage team members
            APIError: For other API-related errors
        """
        team_id = self._get_id_from_arg(team_id)
        user_id = self._get_id_from_arg(user_id)
        
        return self.api.delete(f"{self.resource_name}/{team_id}/members/{user_id}")
    
    @api_write_only
    def update_member_role(self, team_id: Union[str, uuid.UUID], user_id: Union[str, uuid.UUID], role: str) -> Any:
        """
        Update a team member's role - always through API
        
        Args:
            team_id: Team ID or key
            user_id: User ID or key
            role: New team role
            
        Returns:
            Updated team membership information
            
        Raises:
            NotFoundError: If the team member is not found
            ValidationError: If the role is invalid
            AuthenticationError: If not authorized to manage team members
            APIError: For other API-related errors
        """
        team_id = self._get_id_from_arg(team_id)
        user_id = self._get_id_from_arg(user_id)
        
        data = {"role": role}
        return self.api.update(f"{self.resource_name}/{team_id}/members/{user_id}", "", data, Dict) 