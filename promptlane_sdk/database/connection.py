"""
Database connection for PromptLane SDK
"""

import uuid
from typing import Optional, List, Dict, Any, Type, Union
from sqlalchemy import create_engine, MetaData, Table, Column, text
from sqlalchemy.orm import sessionmaker, scoped_session, Query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select, insert, update, delete

from ..models.base import BaseModel
from ..models.user import User
from ..models.team import Team


class DatabaseConnection:
    """
    Database connection using SQLAlchemy for direct database access
    
    This class provides methods to interact directly with the PromptLane database.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize a database connection
        
        Args:
            connection_string: SQLAlchemy database connection string
        """
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.session_factory)
        
        # Store table references
        self.tables = {}
        for table_name in self.metadata.tables:
            self.tables[table_name] = self.metadata.tables[table_name]
    
    def close(self):
        """Close the database connection"""
        self.session.remove()
        self.engine.dispose()
    
    def _get_table(self, resource_name: str) -> Table:
        """Get SQLAlchemy Table object for a resource"""
        if resource_name in self.tables:
            return self.tables[resource_name]
        raise ValueError(f"Table {resource_name} not found in database schema")
    
    def _model_to_dict(self, model_obj: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic model to dictionary for DB operations"""
        data = model_obj.dict(exclude_unset=True)
        
        # Convert UUID objects to strings
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)
        
        return data
    
    def _row_to_model(self, row: Dict[str, Any], model_class: Type[BaseModel]) -> BaseModel:
        """Convert database row to Pydantic model"""
        return model_class(**row)
    
    def list(self, resource_name: str, model_class: Type[BaseModel], **filters) -> List[BaseModel]:
        """
        List resources with optional filtering
        
        Args:
            resource_name: Resource/table name
            model_class: Pydantic model class for the resource
            **filters: Filter parameters
            
        Returns:
            List of resources as Pydantic models
        """
        table = self._get_table(resource_name)
        query = select([table])
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(table.c, key):
                query = query.where(getattr(table.c, key) == value)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            rows = [dict(row) for row in result]
        
        return [self._row_to_model(row, model_class) for row in rows]
    
    def get(self, resource_name: str, id_or_key: str, model_class: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Get a single resource by ID or key
        
        Args:
            resource_name: Resource/table name
            id_or_key: Resource ID or key
            model_class: Pydantic model class for the resource
            
        Returns:
            Resource as Pydantic model or None if not found
        """
        table = self._get_table(resource_name)
        
        # Try with ID first
        try:
            uuid_obj = uuid.UUID(id_or_key)
            query = select([table]).where(table.c.id == uuid_obj)
        except ValueError:
            # If not UUID, try with key
            query = select([table]).where(table.c.key == id_or_key)
        
        with self.engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_model(dict(row), model_class)
    
    def create(self, resource_name: str, data: BaseModel, model_class: Type[BaseModel]) -> BaseModel:
        """
        Create a new resource
        
        Args:
            resource_name: Resource/table name
            data: Resource data as Pydantic model
            model_class: Pydantic model class for the result
            
        Returns:
            Created resource as Pydantic model
        """
        table = self._get_table(resource_name)
        
        # Convert model to dict for insert
        values = self._model_to_dict(data)
        
        # Ensure ID is set if not provided
        if "id" not in values or not values["id"]:
            values["id"] = str(uuid.uuid4())
        
        with self.engine.connect() as conn:
            # Run inside transaction
            with conn.begin():
                # Insert the new record
                result = conn.execute(insert(table).values(**values))
                
                # Get the newly created record
                query = select([table]).where(table.c.id == values["id"])
                new_row = conn.execute(query).fetchone()
        
        return self._row_to_model(dict(new_row), model_class)
    
    def update(self, resource_name: str, id_or_key: str, data: BaseModel, model_class: Type[BaseModel]) -> BaseModel:
        """
        Update an existing resource
        
        Args:
            resource_name: Resource/table name
            id_or_key: Resource ID or key
            data: Updated resource data as Pydantic model
            model_class: Pydantic model class for the result
            
        Returns:
            Updated resource as Pydantic model
        """
        table = self._get_table(resource_name)
        
        # Convert model to dict for update
        values = self._model_to_dict(data)
        
        # Try with ID first
        try:
            uuid_obj = uuid.UUID(id_or_key)
            condition = table.c.id == uuid_obj
        except ValueError:
            # If not UUID, try with key
            condition = table.c.key == id_or_key
        
        with self.engine.connect() as conn:
            # Run inside transaction
            with conn.begin():
                # Update the record
                conn.execute(update(table).where(condition).values(**values))
                
                # Get the updated record
                query = select([table]).where(condition)
                updated_row = conn.execute(query).fetchone()
        
        return self._row_to_model(dict(updated_row), model_class)
    
    def delete(self, resource_name: str, id_or_key: str) -> bool:
        """
        Delete a resource
        
        Args:
            resource_name: Resource/table name
            id_or_key: Resource ID or key
            
        Returns:
            True if successful, False otherwise
        """
        table = self._get_table(resource_name)
        
        # Try with ID first
        try:
            uuid_obj = uuid.UUID(id_or_key)
            condition = table.c.id == uuid_obj
        except ValueError:
            # If not UUID, try with key
            condition = table.c.key == id_or_key
        
        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(delete(table).where(condition))
        
        return result.rowcount > 0
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            Query results as list of dictionaries
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(row) for row in result]
    
    # Team-specific methods
    
    def get_team_members(self, team_id: str) -> List[User]:
        """
        Get all members of a team
        
        Args:
            team_id: Team ID
            
        Returns:
            List of team members as User models
        """
        sql = """
        SELECT u.* 
        FROM users u
        JOIN team_members tm ON u.id = tm.user_id
        WHERE tm.team_id = :team_id
        """
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {"team_id": team_id})
            rows = [dict(row) for row in result]
        
        return [User(**row) for row in rows]
    
    def add_team_member(self, team_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """
        Add a user to a team
        
        Args:
            team_id: Team ID
            user_id: User ID
            role: Team role
            
        Returns:
            Created team member record
        """
        members_table = self._get_table("team_members")
        
        values = {
            "id": str(uuid.uuid4()),
            "team_id": team_id,
            "user_id": user_id,
            "role": role,
            "status": "active"  # Default status
        }
        
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(insert(members_table).values(**values))
                
                # Get the newly created record
                query = select([members_table]).where(
                    (members_table.c.team_id == team_id) & 
                    (members_table.c.user_id == user_id)
                )
                new_row = conn.execute(query).fetchone()
        
        return dict(new_row)
    
    def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """
        Remove a user from a team
        
        Args:
            team_id: Team ID
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        members_table = self._get_table("team_members")
        
        condition = (
            (members_table.c.team_id == team_id) & 
            (members_table.c.user_id == user_id)
        )
        
        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(delete(members_table).where(condition))
        
        return result.rowcount > 0
    
    # User-specific methods
    
    def get_user_teams(self, user_id: str) -> List[Team]:
        """
        Get all teams a user belongs to
        
        Args:
            user_id: User ID
            
        Returns:
            List of teams as Team models
        """
        sql = """
        SELECT t.* 
        FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.user_id = :user_id
        """
        
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), {"user_id": user_id})
            rows = [dict(row) for row in result]
        
        return [Team(**row) for row in rows]
    
    def invite_user(self, email: str, full_name: Optional[str] = None) -> User:
        """
        Invite a new user to PromptLane
        
        Args:
            email: User email
            full_name: User full name (optional)
            
        Returns:
            Created user as User model
        """
        users_table = self._get_table("users")
        
        # Generate invitation token
        invitation_token = str(uuid.uuid4())
        
        values = {
            "id": str(uuid.uuid4()),
            "email": email,
            "full_name": full_name,
            "status": "invited",
            "invitation_token": invitation_token,
            "is_active": False
        }
        
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(insert(users_table).values(**values))
                
                # Get the newly created record
                query = select([users_table]).where(users_table.c.email == email)
                new_row = conn.execute(query).fetchone()
        
        return User(**dict(new_row)) 