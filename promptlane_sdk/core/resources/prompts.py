"""
Prompts resource for PromptLane SDK
"""

from typing import Union, List
import uuid

from .base import ResourceBase, ResourceMixin
from ...models.prompt import Prompt, PromptCreate, PromptUpdate


class Prompts(ResourceBase, ResourceMixin):
    """Client for interacting with PromptLane prompts"""
    
    model_class = Prompt
    create_model_class = PromptCreate
    update_model_class = PromptUpdate
    resource_name = "prompts"
    
    def create_version(self, id_or_key: Union[str, uuid.UUID], **kwargs) -> Prompt:
        """Create a new version of an existing prompt"""
        prompt_id = self._get_id_from_arg(id_or_key)
        data = PromptCreate(**kwargs)
        
        if self.mixed_mode or not self.db:
            return self.api.create(f"{self.resource_name}/{prompt_id}/versions", data, Prompt)
        else:
            # Get parent prompt first
            parent = self.db.get(self.resource_name, prompt_id, Prompt)
            
            # Create new version with parent ID
            data.parent_id = parent.id
            return self.db.create(self.resource_name, data, Prompt)
    
    def get_versions(self, id_or_key: Union[str, uuid.UUID]) -> List[Prompt]:
        """Get all versions of a prompt"""
        prompt_id = self._get_id_from_arg(id_or_key)
        
        if self.db and not self.mixed_mode:
            # Get the root prompt if this is a version
            prompt = self.db.get(self.resource_name, prompt_id, Prompt)
            root_id = prompt.parent_id or prompt.id
            
            # Get all versions with this parent ID
            return self.db.list(self.resource_name, Prompt, parent_id=root_id)
        else:
            return self.api.list(f"{self.resource_name}/{prompt_id}/versions", Prompt) 