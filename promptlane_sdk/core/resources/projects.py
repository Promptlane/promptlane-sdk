"""
Projects resource for PromptLane SDK
"""

from typing import Union, List
import uuid

from .base import ResourceBase, ResourceMixin
from ...models.project import Project, ProjectCreate, ProjectUpdate
from ...models.prompt import Prompt


class Projects(ResourceBase, ResourceMixin):
    """Client for interacting with PromptLane projects"""
    
    model_class = Project
    create_model_class = ProjectCreate
    update_model_class = ProjectUpdate
    resource_name = "projects"
    
    def get_prompts(self, project_id: Union[str, uuid.UUID]) -> List[Prompt]:
        """Get all prompts for a project"""
        project_id = self._get_id_from_arg(project_id)
        
        if self.db and not self.mixed_mode:
            return self.db.list("prompts", Prompt, project_id=project_id)
        else:
            return self.api.list(f"{self.resource_name}/{project_id}/prompts", Prompt) 