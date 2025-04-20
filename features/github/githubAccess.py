from utils.credentials import GITHUB_PERSONAL_ACCESS_TOKEN
from github import Github, Auth
import sys

def initialize_github():
    try:
        if not GITHUB_PERSONAL_ACCESS_TOKEN:
            raise ValueError("GitHub token is empty or not set")
        
        auth = Auth.Token(GITHUB_PERSONAL_ACCESS_TOKEN)
        return Github(auth=auth)
    except Exception as e:
        print(f"GitHub initialization error: {str(e)}", file=sys.stderr)
        raise
# try:
#     g = initialize_github()
# except Exception as e:
#     print(f"Failed to initialize GitHub client: {str(e)}", file=sys.stderr)
#     sys.exit(1)

def get_repo():
    "this function is used to get list of repo for the user{no need of username} "
    "dosent take in any args, its set for single user"
    "just call this function to get the repo"
    "this function returns a list of repo"
    repo = []
    for re in g.get_user().get_repos():
        repo.append({
            "full_name": re.full_name,
                        "name": re.name,
                        "description": re.description,
                        "url": re.html_url,
        })
    g.close()
    return repo

def get_content_of_repo(repo_name):
    """This function is used to get files(SRC folder files) for a repo name provided by user
       use this function when the user question is related to any specifi repo
    """
    "Takes in repo name as an argument and returns "

    repo = g.get_repo("HemanthGirimath/"+repo_name)
    files = []
    contents = repo.get_contents("")
    for content_file in contents:
        files.append(content_file)
    print(files)
    return files


def create_newRepo(name,description, private=False ,has_issues=True, has_wiki=True, auto_init=True,):
    """
    This function is used to creat a new repo
    This function takes in name,descriptions,private,has_issues,has_wiki,auto_ini as arguments
    name and descriptions is mandatory if the user wants a private repo then
    private should be set to True"""

    user = g.get_user()

    new_repo = user.create_repo(
        name="new-repository-name",
        description="Description of the repository",
        private=False,  # Set to True for private repository
        has_issues=True,
        has_wiki=True,
        auto_init=True  # This creates an initial commit with README
    )
    return (f"Repository created: {new_repo.html_url}")
