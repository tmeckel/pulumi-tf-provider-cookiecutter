import os
import shutil
from subprocess import Popen

# Get the root project directory
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def init_git():
    """
    Initialises git on the new project folder
    """
    GIT_COMMANDS = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-a", "-m", "Initial Commit."],
    ]

    for command in GIT_COMMANDS:
        git = Popen(command, cwd=PROJECT_DIRECTORY)
        git.wait()


def remove_shim():
    """
    Removes the shim directory if a provider shim is not required
    """
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, "provider", "shim"))


def remove_github_workflows():
    """
    Removes the .github/worklfows directory if a GitHub worklfows are not required
    """
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, ".github", "worklfows"))


def go_mod_tidy(folder):
    if "{{ cookiecutter.skip_go_mod_tidy }}".lower() not in ["true", "1", "yes", "y"]:
        go = Popen(["go", "mod", "tidy"], cwd=os.path.join(PROJECT_DIRECTORY, folder))
        go.wait()


go_mod_tidy("provider")
if "{{ cookiecutter.create_shim }}".lower() in ["true", "1", "yes", "y"]:
    go_mod_tidy(os.path.join("provider", "shim"))
else:
    remove_shim()

if "{{ cookiecutter.create_github_workflows }}".lower() not in [
    "true",
    "1",
    "yes",
    "y",
]:
    remove_github_workflows()

init_git()
