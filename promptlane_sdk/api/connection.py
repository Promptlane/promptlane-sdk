"""
API connection for PromptLane SDK
"""

import json
import uuid
from typing import Optional, List, Dict, Any, Type, Union
import requests
from requests.adapters import HTTPAdapter, Retry

from ..models.base import BaseModel
from ..api.exceptions import (
    APIError, 
    AuthenticationError, 
    NotFoundError, 
    ValidationError, 
    RateLimitError
)


class APIConnection:
    """
    API connection for making requests to the PromptLane API
    
    This class provides methods to interact with the PromptLane API.
    """
    
    def __init__(
        self, 
        base_url: str,
        api_key: str,
        api_version: str = "v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize an API connection
        
        Args:
            base_url: Base URL of the PromptLane API
            api_key: API key for authentication
            api_version: API version to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version
        self.timeout = timeout
        
        # Create session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def close(self):
        """Close the API connection"""
        self.session.close()
    
    def _build_url(self, path: str) -> str:
        """Build a complete API URL"""
        # Remove leading slash if present
        path = path.lstrip("/")
        
        # Add API version if not in path
        if not path.startswith(f"{self.api_version}/"):
            path = f"{self.api_version}/{path}"
        
        return f"{self.base_url}/{path}"
    
    def _handle_response(self, response: requests.Response, expected_model_class: Optional[Type[BaseModel]] = None) -> Any:
        """
        Handle API response and convert to appropriate format
        
        Args:
            response: Response object from requests
            expected_model_class: Expected model class for deserialization
            
        Returns:
            Response data, optionally converted to model instance
            
        Raises:
            APIError: For various API errors based on status code
        """
        # Check for HTTP errors
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = response.status_code
            error_detail = None
            
            # Try to extract error details from response
            try:
                error_data = response.json()
                error_detail = error_data.get("detail") or error_data.get("message")
            except (ValueError, json.JSONDecodeError):
                # If response is not valid JSON
                error_detail = response.text
            
            # Raise appropriate error based on status code
            if status_code == 401 or status_code == 403:
                raise AuthenticationError(error_detail or "Authentication failed")
            elif status_code == 404:
                raise NotFoundError(error_detail or f"Resource not found")
            elif status_code == 422:
                raise ValidationError(error_detail or "Validation error")
            elif status_code == 429:
                raise RateLimitError(error_detail or "Rate limit exceeded")
            else:
                raise APIError(f"API error: {status_code} - {error_detail or response.reason}")
        
        # Parse JSON response
        data = response.json()
        
        # If expecting a model and received a list, convert each item
        if expected_model_class and isinstance(data, list):
            return [expected_model_class(**item) for item in data]
        
        # If expecting a model and received a dict, convert it
        if expected_model_class and isinstance(data, dict):
            return expected_model_class(**data)
        
        # Otherwise return raw data
        return data
    
    def _model_to_dict(self, model_obj: Optional[BaseModel]) -> Dict[str, Any]:
        """Convert Pydantic model to dictionary for API requests"""
        if model_obj is None:
            return {}
        
        return model_obj.dict(exclude_unset=True)
    
    def request(
        self,
        method: str,
        path: str,
        model_class: Optional[Type[BaseModel]] = None,
        data: Optional[Union[Dict[str, Any], BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make a request to the PromptLane API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            model_class: Expected model class for response
            data: Request data (dict or Pydantic model)
            params: Query parameters
            
        Returns:
            Response data, optionally converted to model instance
        """
        url = self._build_url(path)
        
        # Convert model to dict if needed
        if isinstance(data, BaseModel):
            data = self._model_to_dict(data)
        
        # Make request
        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            timeout=self.timeout
        )
        
        return self._handle_response(response, model_class)
    
    def list(self, resource_path: str, model_class: Type[BaseModel], **params) -> List[Any]:
        """
        List resources with optional filtering
        
        Args:
            resource_path: API resource path
            model_class: Expected model class for items in the response
            **params: Query parameters for filtering
            
        Returns:
            List of resources, converted to model instances
        """
        return self.request("GET", resource_path, model_class, params=params)
    
    def get(self, resource_path: str, resource_id: str, model_class: Type[BaseModel]) -> Any:
        """
        Get a single resource by ID
        
        Args:
            resource_path: API resource path
            resource_id: Resource ID or key
            model_class: Expected model class for the response
            
        Returns:
            Resource as model instance
        """
        path = f"{resource_path}/{resource_id}"
        return self.request("GET", path, model_class)
    
    def create(self, resource_path: str, data: Union[Dict[str, Any], BaseModel], model_class: Type[BaseModel]) -> Any:
        """
        Create a new resource
        
        Args:
            resource_path: API resource path
            data: Resource data (dict or model)
            model_class: Expected model class for the response
            
        Returns:
            Created resource as model instance
        """
        return self.request("POST", resource_path, model_class, data=data)
    
    def update(
        self,
        resource_path: str,
        resource_id: str,
        data: Union[Dict[str, Any], BaseModel],
        model_class: Type[BaseModel]
    ) -> Any:
        """
        Update an existing resource
        
        Args:
            resource_path: API resource path
            resource_id: Resource ID or key
            data: Updated resource data (dict or model)
            model_class: Expected model class for the response
            
        Returns:
            Updated resource as model instance
        """
        path = f"{resource_path}/{resource_id}"
        return self.request("PUT", path, model_class, data=data)
    
    def delete(self, resource_path: str, resource_id: str) -> bool:
        """
        Delete a resource
        
        Args:
            resource_path: API resource path
            resource_id: Resource ID or key
            
        Returns:
            True if successful
        """
        path = f"{resource_path}/{resource_id}"
        self.request("DELETE", path)
        return True  # If no exception was raised, consider successful 