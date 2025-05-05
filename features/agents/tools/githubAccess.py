from utils.credentials import GITHUB_PERSONAL_ACCESS_TOKEN
from github import Github, Auth
import sys
from langchain.tools import StructuredTool
from typing import List, Dict, Optional
from pydantic import BaseModel,Field


class CreateRepoSchema(BaseModel):
    name: str
    description: str
    private: bool = False
    has_issues: bool = True
    has_wiki: bool = True
    auto_init: bool = True

class GetRepoContentsSchema(BaseModel):
    repo_name: str

class GitHubTools:
    def __init__(self):
        self.github = None
        
    def initialize_github(self):
        if self.github is None:
            try:
                if not GITHUB_PERSONAL_ACCESS_TOKEN:
                    raise ValueError("GitHub token is empty or not set")
                auth = Auth.Token(GITHUB_PERSONAL_ACCESS_TOKEN)
                self.github = Github(auth=auth)
            except Exception as e:
                print(f"GitHub initialization error: {str(e)}", file=sys.stderr)
                raise
        return self.github

    def get_repo(self) -> List[Dict]:
        g = self.initialize_github()
        repo = []
        for re in g.get_user().get_repos():
            repo.append({
                "full_name": re.full_name,
                "name": re.name,
                "description": re.description,
                "url": re.html_url,
            })
        return repo

    def get_content_of_repo(self, repo_name: str) -> List:
        g = self.initialize_github()
        repo = g.get_repo(f"HemanthGirimath/{repo_name}")
        files = []
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            files.append({
                "name": file_content.name,
                "path": file_content.path,
                "type": file_content.type,
                "url": file_content.html_url
            })
        return files

    def create_new_repo(self, name: str, description: str, private: bool = False,
                       has_issues: bool = True, has_wiki: bool = True, auto_init: bool = True) -> str:
        g = self.initialize_github()
        user = g.get_user()
        new_repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            has_issues=has_issues,
            has_wiki=has_wiki,
            auto_init=auto_init
        )
        return f"Repository created: {new_repo.html_url}"

class ListReposSchema(BaseModel):
    """Schema for listing repositories (empty as it needs no parameters)"""
    pass

class GetRepoContentsSchema(BaseModel):
    """Schema for getting repository contents"""
    repo_name: str = Field(
        description="Name of the repository to fetch contents from"
    )

class CreateRepoSchema(BaseModel):
    """Schema for creating a new repository"""
    name: str = Field(description="Name of the new repository")
    description: str = Field(description="Description of the repository")
    private: bool = Field(default=False, description="Whether the repository should be private")
    has_issues: bool = Field(default=True, description="Whether to enable issues")
    has_wiki: bool = Field(default=True, description="Whether to enable wiki")
    auto_init: bool = Field(default=True, description="Whether to initialize with README")
    
github_handler = GitHubTools()

# Define LangChain tools with schemas
github_tools = [
    StructuredTool(
        name="list_repositories",
        description="Get a list of all GitHub repositories for the authenticated user",
        func=github_handler.get_repo,
        args_schema=ListReposSchema
    ),
    StructuredTool(
        name="get_repo_contents",
        description="Get the contents of a specific GitHub repository",
        func=github_handler.get_content_of_repo,
        args_schema=GetRepoContentsSchema
    ),
    StructuredTool(
        name="create_repository",
        description="Create a new GitHub repository with specified parameters",
        func=github_handler.create_new_repo,
        args_schema=CreateRepoSchema
    )
]
