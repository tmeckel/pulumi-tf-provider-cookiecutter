import os
import shutil
import re

from subprocess import Popen

# Get the root project directory
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def init_git():
    """
    Initialises git on the new project folder
    """

    if not os.path.exists(".git"):
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


def go_mod_add_provider(folder):
    version = "{{ cookiecutter.terraform_provider_version_or_commit }}"
    if re.match(r"^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$", version):
        version = "v%s" % version
    provider_source = "{{ cookiecutter.terraform_provider_source }}@%s" % version
    go = Popen(
        ["go", "get", provider_source], cwd=os.path.join(PROJECT_DIRECTORY, folder)
    )
    go.wait()


if "{{ cookiecutter.terraform_provider_package_name }}".startswith("internal"):
    path = os.path.join("provider", "shim")
    go_mod_add_provider(path)
    go_mod_tidy(path)
else:
    go_mod_add_provider("provider")
    remove_shim()

go_mod_tidy("provider")

if "{{ cookiecutter.create_github_workflows }}".lower() not in [
    "true",
    "1",
    "yes",
    "y",
]:
    remove_github_workflows()

init_git()
