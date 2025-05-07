import os
import subprocess
import signal
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import time
import psutil

# Directory constants - using user's home directory
HOME = str(Path.home())
python_dir = os.path.join(HOME, "projects/python")
react_dir = os.path.join(HOME, "projects/react")
nextjs_dir = os.path.join(HOME, "projects/next-js")

class ProjectSetupSchema(BaseModel):
    """Schema for project setup"""
    project_type: Literal["react", "python", "nextjs"] = Field(
        description="Type of project to create (react/python/nextjs)"
    )
    project_name: str = Field(
        default="test",
        description="Name of the project to create"
    )
    with_options: Optional[List[str]] = Field(
        default_factory=list,
        description="Additional options for project creation (e.g., --typescript, --tailwind)"
    )

class FileTools:
    def __init__(self):
        self.project_commands = {
            "nextjs": ["npx", "create-next-app@latest"],
            "react": ["npx", "--yes", "create-react-app@latest"],  # Updated command
            "python": ["python", "-m", "venv"]
        }
        self.project_dirs = {
            "nextjs": nextjs_dir,
            "react": react_dir,
            "python": python_dir
        }
        # Create base project directories
        for directory in self.project_dirs.values():
            os.makedirs(directory, exist_ok=True)
        self.current_process: Optional[subprocess.Popen] = None

    def _cleanup_process(self):
        """Clean up any running process"""
        if self.current_process:
            try:
                # Get the process group
                process = psutil.Process(self.current_process.pid)
                children = process.children(recursive=True)
                
                # Terminate children first
                for child in children:
                    child.terminate()
                
                # Terminate main process
                self.current_process.terminate()
                
                # Wait for processes to terminate
                _, still_alive = psutil.wait_procs(children + [process], timeout=3)
                
                # Force kill if still alive
                for p in still_alive:
                    p.kill()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            finally:
                self.current_process = None

    def setup_project(self, project_type: str, project_name: str = "test", with_options: List[str] = None) -> dict:
        """Set up a new project with specified type and name"""
        max_tries = 2
        current_try = 0
        last_error = None

        while current_try < max_tries:
            try:
                self._cleanup_process()
                
                # Sanitize project name
                project_name = project_name.replace(" ", "-").lower()
                
                base_dir = self.project_dirs.get(project_type)
                if not base_dir:
                    return {
                        "status": "error",
                        "message": f"Unsupported project type: {project_type}"
                    }

                # Ensure base directory exists
                os.makedirs(base_dir, exist_ok=True)
                
                # Build command based on project type
                command = self.project_commands[project_type].copy()
                project_path = os.path.join(base_dir, project_name)

                # Handle different project types
                if project_type == "nextjs":
                    # Next.js specific command structure with all preferences defined
                    command.extend([
                        project_name,
                        "--typescript",
                        "--tailwind",
                        "--eslint",
                        "--app",  # Use App Router
                        "--src-dir",
                        "--import-alias", "@/*",
                        "--use-npm",
                        "--git",
                        "--yes"  # Skip all prompts
                    ])
                
                elif project_type == "react":
                    # React specific command with template and non-interactive mode
                    # First ensure create-react-app is installed globally
                    try:
                        subprocess.run(
                            ["npm", "install", "-g", "create-react-app"],
                            check=True,
                            capture_output=True
                        )
                    except subprocess.CalledProcessError:
                        pass  # Continue even if installation fails

                    command.extend([
                        project_name,
                        "--template", "typescript",
                        "--use-npm",
                        "--skip-git",  # Skip git initialization
                    ])
                    
                elif project_type == "python":
                    # Python specific - create directory first
                    os.makedirs(project_path, exist_ok=True)
                    command.append(project_path)

                print(f"Attempt {current_try + 1}/{max_tries}: Executing command: {' '.join(command)} in {base_dir}")
                
                # Increase timeout to 120 seconds for npm commands
                timeout = 120 if project_type in ["nextjs", "react"] else 30
                
                self.current_process = subprocess.Popen(
                    command,
                    cwd=base_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                try:
                    stdout, stderr = self.current_process.communicate(timeout=timeout)
                    if self.current_process.returncode != 0:
                        raise subprocess.CalledProcessError(
                            self.current_process.returncode, 
                            command,
                            stdout,
                            stderr
                        )
                    
                    # If successful, open in VS Code
                    try:
                        subprocess.run(
                            ["code", project_path],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        return {
                            "status": "success",
                            "message": f"Created {project_type} project: {project_name} and opened in VS Code",
                            "location": project_path,
                            "stdout": stdout
                        }
                    except subprocess.CalledProcessError as vscode_error:
                        return {
                            "status": "partial_success",
                            "message": f"Project created but couldn't open VS Code: {str(vscode_error)}",
                            "location": project_path,
                            "stdout": stdout
                        }
                        
                except subprocess.TimeoutExpired:
                    self._cleanup_process()
                    last_error = f"Process timed out after {timeout} seconds"
                    
            except Exception as e:
                self._cleanup_process()
                last_error = str(e)
            
            current_try += 1
            if current_try < max_tries:
                print(f"Attempt {current_try} failed. Retrying in 2 seconds...")
                time.sleep(2)
        
        return {
            "status": "error",
            "message": f"Failed after {max_tries} attempts. Last error: {last_error}",
            "type": "MaxRetriesExceeded"
        }

    def __del__(self):
        """Cleanup on object destruction"""
        self._cleanup_process()

# Create instance
file_handler = FileTools()

# Define LangChain tools
file_tools = [
    StructuredTool(
        name="setup_project",
        description="Set up a new project (nextjs/react/python) with optional name and configuration. Example: setup_project(project_type='nextjs', project_name='my-app', with_options=['--typescript', '--tailwind'])",
        func=file_handler.setup_project,
        args_schema=ProjectSetupSchema
    )
]