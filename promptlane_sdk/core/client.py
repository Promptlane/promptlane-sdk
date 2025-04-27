"""
PromptLane Client - Core client implementation providing multiple connection types
"""

import os
from enum import Enum
from typing import Optional, Dict, Any, Union

from ..database.connection import DatabaseConnection
from ..api.connection import APIConnection
from .resources import Projects, Prompts, Teams, Users, Activities


class ConnectionType(str, Enum):
    """Connection types supported by the PromptLane SDK"""
    API = "api"
    DATABASE = "database"
    MIXED = "mixed"


class PromptLaneClient:
    """
    Main client for interacting with PromptLane.
    
    Supports multiple connection types:
    - API: All operations performed via HTTP API
    - Database: Direct database access (recommended for advanced use cases)
    - Mixed: Read from database, write via API
    """
    
    def __init__(
        self,
        connection_type: Union[str, ConnectionType] = ConnectionType.API,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        db_connection_string: Optional[str] = None,
        api_version: str = "v1",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new PromptLane client.
        
        Args:
            connection_type: Type of connection to use (api, database, or mixed)
            base_url: Base URL for API connections (required for api and mixed)
            api_key: API key for authentication (required for api and mixed)
            db_connection_string: Database connection string (required for database and mixed)
            api_version: API version to use
            config: Additional configuration options
        """
        self.config = config or {}
        
        # Convert string to enum if needed
        if isinstance(connection_type, str):
            connection_type = ConnectionType(connection_type.lower())
        
        self.connection_type = connection_type
        
        # Set up API connection if needed
        if connection_type in (ConnectionType.API, ConnectionType.MIXED):
            if not base_url:
                base_url = os.environ.get("PROMPTLANE_API_URL")
            
            if not api_key:
                api_key = os.environ.get("PROMPTLANE_API_KEY")
                
            if not base_url or not api_key:
                raise ValueError(
                    "For API or mixed connection types, base_url and api_key must be provided "
                    "either as parameters or as environment variables PROMPTLANE_API_URL and PROMPTLANE_API_KEY"
                )
            
            self.api = APIConnection(base_url=base_url, api_key=api_key, api_version=api_version)
        
        # Set up database connection if needed
        if connection_type in (ConnectionType.DATABASE, ConnectionType.MIXED):
            if not db_connection_string:
                db_connection_string = os.environ.get("PROMPTLANE_DB_CONNECTION")
                
            if not db_connection_string:
                raise ValueError(
                    "For database or mixed connection types, db_connection_string must be provided "
                    "either as a parameter or as the environment variable PROMPTLANE_DB_CONNECTION"
                )
            
            self.db = DatabaseConnection(connection_string=db_connection_string)
        
        # Initialize resource clients
        self._init_resources()
    
    def _init_resources(self):
        """Initialize resource clients based on the connection type"""
        if self.connection_type == ConnectionType.API:
            self.projects = Projects(api=self.api)
            self.prompts = Prompts(api=self.api)
            self.teams = Teams(api=self.api)
            self.users = Users(api=self.api)
            self.activities = Activities(api=self.api)
        
        elif self.connection_type == ConnectionType.DATABASE:
            self.projects = Projects(db=self.db)
            self.prompts = Prompts(db=self.db)
            self.teams = Teams(db=self.db)
            self.users = Users(db=self.db)
            self.activities = Activities(db=self.db)
        
        elif self.connection_type == ConnectionType.MIXED:
            self.projects = Projects(db=self.db, api=self.api)
            self.prompts = Prompts(db=self.db, api=self.api)
            self.teams = Teams(db=self.db, api=self.api)
            self.users = Users(db=self.db, api=self.api)
            self.activities = Activities(db=self.db, api=self.api)
    
    def close(self):
        """Close all connections"""
        if hasattr(self, "db"):
            self.db.close()
        
        if hasattr(self, "api"):
            self.api.close() 