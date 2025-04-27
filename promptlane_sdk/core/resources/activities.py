"""
Activities resource for PromptLane SDK
"""

from typing import Union, List
import uuid

from .base import ResourceBase, ResourceMixin
from ...models.activity import Activity


class Activities(ResourceBase, ResourceMixin):
    """Client for interacting with PromptLane activities"""
    
    model_class = Activity
    resource_name = "activities"
    
    def list_for_user(self, user_id: Union[str, uuid.UUID], **kwargs) -> List[Activity]:
        """Get all activities for a user"""
        user_id = self._get_id_from_arg(user_id)
        
        if self.db and not self.mixed_mode:
            return self.db.list(self.resource_name, Activity, user_id=user_id, **kwargs)
        else:
            return self.api.list(f"{self.resource_name}?user_id={user_id}", Activity, **kwargs) 