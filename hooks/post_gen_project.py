import os
import shutil
import re
import requests
from dateutil import parser as dateparser

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


def go_mod_add_provider(folder, is_shim=False):
    path = os.path.join(PROJECT_DIRECTORY, folder)
    version = "{{ cookiecutter.terraform_provider_version_or_commit }}"
    is_version = False
    if re.match(r"^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$", version):
        version = "v%s" % version
        is_version = True

    provider_module = "{{ cookiecutter.terraform_provider_module }}"
    versionless_provider_module = provider_module
    idx = provider_module.rfind("/v")
    if idx > -1:
        versionless_provider_module = provider_module[:idx]

    provider_source = "{{ cookiecutter.terraform_provider_source }}@%s" % version
    if versionless_provider_module != "{{ cookiecutter.terraform_provider_source }}":
        if is_version:
            go = Popen(
                [
                    "go",
                    "mod",
                    "edit",
                    "-replace=%s=%s" % (provider_module, provider_source),
                ],
                cwd=path,
            )
            go.wait()

            if is_shim:
                go = Popen(
                    ["go", "mod", "edit", "-module", "%s/shim" % versionless_provider_module],
                    cwd=path,
                )
                go.wait()

            provider_source = "%s@%s" % (versionless_provider_module, version)
        else:
            provider_source = "{{ cookiecutter.terraform_provider_source }}"
            provider_source_elements = provider_source.split("/")
            if len(provider_source_elements) < 3:
                raise ValueError(
                    "terraform_provider_source [%s] has an invalid format"
                    % provider_source
                )

            if provider_source_elements[0].lower() != "github.com":
                raise ValueError(
                    "Only providers hosted on GitHub are currently supported while a Go replace is required"
                )

            api_url = "https://api.github.com/repos/%s/%s/commits/%s" % (
                provider_source_elements[1],
                provider_source_elements[2],
                version,
            )
            resp = requests.get(
                url=api_url, headers={"Accept": "application/vnd.github+json"}
            )

            if not resp.ok:
                resp.raise_for_status()

            json = resp.json()
            commit_date = dateparser.isoparse(json["commit"]["committer"]["date"])
            pseudo_version = "v0.0.0-%s-%s" % (
                commit_date.strftime("%Y%m%d%H%M%S"),
                json["sha"][:12],
            )
            provider_source = "%s@%s" % (provider_source, pseudo_version)
            go = Popen(
                [
                    "go",
                    "mod",
                    "edit",
                    "-replace=%s=%s" % (provider_module, provider_source),
                ],
                cwd=path,
            )
            go.wait()

            if is_shim:
                go = Popen(
                    ["go", "mod", "edit", "-module", "%s/shim" % versionless_provider_module],
                    cwd=path,
                )
                go.wait()

            provider_source = "%s@%s" % (provider_module, pseudo_version)

    go = Popen(["go", "get", provider_source], cwd=path)
    go.wait()


if "{{ cookiecutter.terraform_provider_package_name }}".startswith("internal"):
    path = os.path.join("provider", "shim")
    go_mod_add_provider(path, True)
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

if "{{ cookiecutter.provider_github_organization }}".lower() == "pulumiverse":
    os.remove(os.path.join(PROJECT_DIRECTORY, "CODE-OF-CONDUCT.md"))

init_git()
