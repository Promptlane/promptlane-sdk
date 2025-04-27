"""
Base resource classes for PromptLane SDK
"""

from typing import Optional, List, Dict, Any, Union, Type
import uuid

from ...api.connection import APIConnection
from ...database.connection import DatabaseConnection
from ...models.base import BaseModel
from ..utils.decorators import api_write_only


class ResourceBase:
    """Base class for all resource clients"""
    
    model_class: Type[BaseModel] = None
    create_model_class: Type[BaseModel] = None
    update_model_class: Type[BaseModel] = None
    resource_name: str = None
    
    def __init__(
        self,
        db: Optional[DatabaseConnection] = None,
        api: Optional[APIConnection] = None,
    ):
        """
        Initialize a resource client.
        
        Args:
            db: Database connection (for database or mixed mode)
            api: API connection (for API or mixed mode)
        """
        self.db = db
        self.api = api
        
        if not db and not api:
            raise ValueError("At least one of db or api must be provided")
        
        self.mixed_mode = bool(db and api)
    
    def _get_id_from_arg(self, id_or_key: Union[str, uuid.UUID]) -> str:
        """Normalize ID or key to string"""
        return str(id_or_key)


class ResourceMixin:
    """
    Common methods for all resources
    
    Methods follow a pattern:
    - If in API mode, use API connection
    - If in DB mode, use DB connection
    - If in mixed mode, use DB for reading and API for writing
    """
    
    def list(self, **kwargs) -> List[Any]:
        """List all resources, with optional filtering"""
        if self.db and not (self.mixed_mode and kwargs.get("force_api", False)):
            return self.db.list(self.resource_name, self.model_class, **kwargs)
        else:
            return self.api.list(self.resource_name, self.model_class, **kwargs)
    
    def get(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> Any:
        """Get a single resource by ID or key"""
        item_id = self._get_id_from_arg(id_or_key)
        
        if self.db and not (self.mixed_mode and kwargs.get("force_api", False)):
            return self.db.get(self.resource_name, item_id, self.model_class)
        else:
            return self.api.get(self.resource_name, item_id, self.model_class)
    
    def create(self, **kwargs) -> Any:
        """Create a new resource"""
        data = self.create_model_class(**kwargs)
        
        if self.mixed_mode or not self.db:
            return self.api.create(self.resource_name, data, self.model_class)
        else:
            return self.db.create(self.resource_name, data, self.model_class)
    
    def update(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> Any:
        """Update an existing resource"""
        item_id = self._get_id_from_arg(id_or_key)
        data = self.update_model_class(**kwargs)
        
        if self.mixed_mode or not self.db:
            return self.api.update(self.resource_name, item_id, data, self.model_class)
        else:
            return self.db.update(self.resource_name, item_id, data, self.model_class)
    
    def delete(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> bool:
        """Delete a resource"""
        item_id = self._get_id_from_arg(id_or_key)
        
        if self.mixed_mode or not self.db:
            return self.api.delete(self.resource_name, item_id)
        else:
            return self.db.delete(self.resource_name, item_id)


class WriteThruAPIResourceMixin:
    """
    Resource mixin that enforces all write operations go through the API
    
    This mixin can be used for resources where all write operations should
    always use the API regardless of connection type. This ensures that 
    validation rules and business logic in the API are always applied.
    
    Examples include sensitive resources like Users, Teams, and Permissions
    that require special validation or security checks.
    
    Usage:
        class Users(ResourceBase, WriteThruAPIResourceMixin):
            model_class = User
            create_model_class = UserCreate
            update_model_class = UserUpdate
            resource_name = "users"
    """
    
    @api_write_only
    def create(self, **kwargs) -> Any:
        """
        Create a new resource - always through API
        
        Args:
            **kwargs: Resource properties
            
        Returns:
            Created resource
        """
        data = self.create_model_class(**kwargs)
        return self.api.create(self.resource_name, data, self.model_class)
    
    @api_write_only
    def update(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> Any:
        """
        Update an existing resource - always through API
        
        Args:
            id_or_key: Resource ID or key
            **kwargs: Properties to update
            
        Returns:
            Updated resource
        """
        item_id = self._get_id_from_arg(id_or_key)
        data = self.update_model_class(**kwargs)
        return self.api.update(self.resource_name, item_id, data, self.model_class)
    
    @api_write_only
    def delete(self, id_or_key: Union[str, uuid.UUID]) -> bool:
        """
        Delete a resource - always through API
        
        Args:
            id_or_key: Resource ID or key
            
        Returns:
            True if successful
        """
        item_id = self._get_id_from_arg(id_or_key)
        return self.api.delete(self.resource_name, item_id) 