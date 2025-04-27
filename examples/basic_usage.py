"""
Basic usage examples for PromptLane SDK
"""

import os
import uuid
from pprint import pprint
from dotenv import load_dotenv

from promptlane_sdk import PromptLaneClient


# Load environment variables
load_dotenv()


def api_connection_example():
    """Example using API connection"""
    print("\n=== API Connection Example ===\n")
    
    # Initialize client with API connection
    client = PromptLaneClient(
        connection_type="api",
        base_url=os.environ.get("PROMPTLANE_API_URL", "http://localhost:8000"),
        api_key=os.environ.get("PROMPTLANE_API_KEY", "your-api-key")
    )
    
    # List all projects
    print("Listing projects...")
    projects = client.projects.list()
    
    if projects:
        # Get the first project
        project = projects[0]
        print(f"Got project: {project.name} (ID: {project.id})")
        
        # List prompts in this project
        print(f"Listing prompts for project {project.key}...")
        prompts = client.projects.get_prompts(project.id)
        
        if prompts:
            # Get the first prompt
            prompt = prompts[0]
            print(f"Got prompt: {prompt.name} (ID: {prompt.id})")
        else:
            # Create a new prompt if none exist
            print("No prompts found, creating a new one...")
            new_prompt = client.prompts.create(
                name="Example Prompt",
                key=f"example-prompt-{uuid.uuid4().hex[:8]}",
                system_prompt="You are a helpful assistant.",
                user_prompt="Answer the following: {{query}}",
                project_id=project.id
            )
            print(f"Created prompt: {new_prompt.name} (ID: {new_prompt.id})")
    else:
        print("No projects found.")
    
    # Clean up
    client.close()


def database_connection_example():
    """Example using direct database connection"""
    print("\n=== Database Connection Example ===\n")
    
    # Initialize client with database connection
    client = PromptLaneClient(
        connection_type="database",
        db_connection_string=os.environ.get(
            "PROMPTLANE_DB_CONNECTION", 
            "postgresql://postgres:postgres@localhost:5432/promptlane"
        )
    )
    
    # List all teams
    print("Listing teams...")
    teams = client.teams.list()
    
    if teams:
        # Get the first team
        team = teams[0]
        print(f"Got team: {team.name} (ID: {team.id})")
        
        # List members of this team
        print(f"Listing members for team {team.name}...")
        members = client.teams.get_members(team.id)
        
        for member in members:
            print(f"- {member.full_name or member.email} ({member.id})")
    else:
        print("No teams found.")
    
    # Clean up
    client.close()


def mixed_connection_example():
    """Example using mixed connection (read from DB, write via API)"""
    print("\n=== Mixed Connection Example ===\n")
    
    # Initialize client with mixed connection
    client = PromptLaneClient(
        connection_type="mixed",
        base_url=os.environ.get("PROMPTLANE_API_URL", "http://localhost:8000"),
        api_key=os.environ.get("PROMPTLANE_API_KEY", "your-api-key"),
        db_connection_string=os.environ.get(
            "PROMPTLANE_DB_CONNECTION", 
            "postgresql://postgres:postgres@localhost:5432/promptlane"
        )
    )
    
    # List all projects (reads from database for better performance)
    print("Listing projects (from database)...")
    projects = client.projects.list()
    
    if projects:
        project = projects[0]
        
        # Update a project (goes through API for validation)
        print(f"Updating project {project.name} (via API)...")
        updated_project = client.projects.update(
            project.id,
            description=f"Updated description at {uuid.uuid4().hex[:8]}"
        )
        
        print(f"Updated project: {updated_project.name}")
        print(f"New description: {updated_project.description}")
    
    # Clean up
    client.close()


if __name__ == "__main__":
    # Run examples
    api_connection_example()
    database_connection_example()
    mixed_connection_example() 