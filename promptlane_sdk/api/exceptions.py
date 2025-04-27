"""
Exceptions for the PromptLane API client
"""


class APIError(Exception):
    """Base exception for all API errors"""
    pass


class AuthenticationError(APIError):
    """Authentication failed or insufficient permissions"""
    pass


class NotFoundError(APIError):
    """Resource not found"""
    pass


class ValidationError(APIError):
    """Invalid request data"""
    pass


class RateLimitError(APIError):
    """API rate limit exceeded"""
    pass


class ConnectionError(APIError):
    """Connection to the API failed"""
    pass 