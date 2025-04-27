"""
Decorator functions for PromptLane SDK resources
"""

import logging
from functools import wraps

from ...api.exceptions import APIError, AuthenticationError, ValidationError, NotFoundError

# Configure logger
logger = logging.getLogger(__name__)


def api_write_only(method):
    """
    Decorator to enforce API-only writes for resource operations.
    
    This decorator enforces that all write operations are performed through 
    the API regardless of connection type, ensuring consistent validation and
    business logic. It also provides standardized error handling for API operations.
    
    Usage:
        @api_write_only
        def create(self, **kwargs):
            data = self.create_model_class(**kwargs)
            return self.api.create(self.resource_name, data, self.model_class)
    
    Args:
        method: The method to decorate
        
    Returns:
        Wrapped method that enforces API-only writes with error handling
        
    Raises:
        ValueError: If no API connection exists
        AuthenticationError: For authentication issues
        ValidationError: For data validation issues
        NotFoundError: When resources aren't found
        APIError: For other API-related errors
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Ensure API connection exists
        if not self.api:
            raise ValueError(
                f"API connection is required for {method.__name__}. "
                "Please initialize the client with an API connection."
            )
        
        try:
            return method(self, *args, **kwargs)
        except AuthenticationError as e:
            logger.error(f"Authentication error in {method.__name__}: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate when performing {method.__name__}: {str(e)}"
            )
        except ValidationError as e:
            logger.error(f"Validation error in {method.__name__}: {str(e)}")
            raise ValidationError(
                f"Invalid data for {method.__name__}: {str(e)}"
            )
        except NotFoundError as e:
            logger.error(f"Not found error in {method.__name__}: {str(e)}")
            raise NotFoundError(
                f"Resource not found in {method.__name__}: {str(e)}"
            )
        except APIError as e:
            logger.error(f"API error in {method.__name__}: {str(e)}")
            raise APIError(
                f"API error occurred during {method.__name__}: {str(e)}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error in {method.__name__}")
            raise APIError(
                f"Unexpected error during {method.__name__}: {str(e)}"
            )
    
    return wrapper 