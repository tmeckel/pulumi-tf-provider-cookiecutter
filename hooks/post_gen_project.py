import logging
import os
import pathlib
import re
import shutil
import sys
from subprocess import Popen

import requests
from dateutil import parser as dateparser

_logger = logging.getLogger(__name__)

# Get the root project directory
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def _error_exit(msg):
    # exits with status 1 to indicate failure
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


def _get_commit_url_from_tag(tags_url):
    while True:
        _logger.error("Getting tag information from %s", tags_url)

        resp = requests.get(
            url=tags_url,
            headers={"Accept": "application/vnd.github+json"},
        )

        if not resp.ok:
            resp.raise_for_status()

        json = resp.json()
        tags_url = json["object"]["url"]
        if json["object"]["type"] == "commit":
            return tags_url


def _get_go_pseudo_version(commit_url):
    _logger.error("Getting commit information from %s", commit_url)

    resp = requests.get(
        url=commit_url,
        headers={"Accept": "application/vnd.github+json"},
    )

    if not resp.ok:
        resp.raise_for_status()

    json = resp.json()

    try:
        if "commit" in json:
            commit_date = dateparser.isoparse(json["commit"]["committer"]["date"])
        else:
            commit_date = dateparser.isoparse(json["committer"]["date"])
    except KeyError:
        _logger.exception("%s", json)
        raise

    return "v0.0.0-%s-%s" % (
        commit_date.strftime("%Y%m%d%H%M%S"),
        json["sha"][:12],
    )


def _split_provider_source(provider_source):
    provider_source_elements = provider_source.split("/")
    if len(provider_source_elements) < 3:  # noqa: PLR2004
        raise ValueError(
            "terraform_provider_source [%s] has an invalid format" % provider_source
        )

    if provider_source_elements[0].lower() != "github.com":
        raise ValueError(
            "Only providers hosted on GitHub are currently supported while a Go replace is required"
        )

    return provider_source_elements


def init_git():
    """
    Initializes git on the new project folder
    """

    if not os.path.exists(".git"):
        git_commands = [
            ["git", "init", "-b", "main"],
            ["git", "commit", "--allow-empty", "-m", "Initial Commit."],
        ]

        for command in git_commands:
            git = Popen(command, cwd=PROJECT_DIRECTORY)
            git.wait()


def remove_shim():
    """
    Removes the shim directory if a provider shim is not required
    """
    shutil.rmtree(os.path.join(PROJECT_DIRECTORY, "provider", "shim"))


def remove_github_workflows():
    """
    Removes the .github/workflows directory if a GitHub workflows are not required
    """
    github_dir = os.path.join(PROJECT_DIRECTORY, ".github")
    shutil.rmtree(os.path.join(github_dir, "workflows"))
    if len(os.listdir(github_dir)) == 0:
        shutil.rmtree(github_dir)


def remove_plugin_framework_files():
    """
    Removed all files specific to Pulumi Terraform Bridge Pluginframework
    """
    items_to_remove = []
    if "{{ cookiecutter.provider_mapping_strategy }}" == "manual":  # noqa: PLR0133
        items_to_remove.extend(
            [
                "provider/cmd/pulumi-resource-{{ cookiecutter.terraform_provider_name }}/bridge-metadata.json"
            ]
        )

    for item in items_to_remove:
        path = pathlib.Path(PROJECT_DIRECTORY, item)
        if path.is_dir():
            # we don't use path.rmdir() because the directory must be empty, and we can't ensure this
            shutil.rmtree(path)
        else:
            os.remove(path)


def go_mod_tidy(folder):
    if "{{ cookiecutter.skip_go_mod_tidy }}".lower().strip() not in [
        "true",
        "1",
        "yes",
        "y",
    ]:
        go = Popen(["go", "mod", "tidy"], cwd=os.path.join(PROJECT_DIRECTORY, folder))
        go.wait()


def go_mod_add_provider(folder, is_shim=False):  # noqa: PLR0915
    path = os.path.join(PROJECT_DIRECTORY, folder)

    version = "{{ cookiecutter.terraform_provider_version_or_commit }}".strip()
    major_version = None
    match = re.match(r"^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$", version)
    if match:
        version = "v%s" % version
        major_version = match.group(1)

    provider_source = "{{ cookiecutter.terraform_provider_source }}".strip()
    provider_module = "{{ cookiecutter.terraform_provider_module }}".strip()
    provider_module_version = None
    versionless_provider_module = provider_module

    try:
        i = provider_module.rindex("/v")
        versionless_provider_module = provider_module[:i]
        provider_module_version = provider_module[i + 1 :]
    except ValueError:
        pass

    if not provider_source.startswith(versionless_provider_module):
        _logger.error(
            "Provider module %s diverges from provider source %s",
            provider_module,
            provider_source,
        )

        pseudo_version = None
        if major_version:
            if not provider_module_version and major_version and int(major_version) > 1:
                _logger.error(
                    "Using a versionless module %s with version %s, converting to pseudo-version",
                    versionless_provider_module,
                    version,
                )

                provider_source_elements = _split_provider_source(provider_source)

                tags_url = "https://api.github.com/repos/%s/%s/git/refs/tags/%s" % (
                    provider_source_elements[1],
                    provider_source_elements[2],
                    version,
                )
                pseudo_version = _get_go_pseudo_version(
                    _get_commit_url_from_tag(tags_url)
                )

        else:
            _logger.error(
                "Using a versioned module %s with a commit reference %s, creating pseudo-version",
                provider_module,
                version,
            )

            provider_source_elements = _split_provider_source(provider_source)

            commit_url = "https://api.github.com/repos/%s/%s/commits/%s" % (
                provider_source_elements[1],
                provider_source_elements[2],
                version,
            )
            pseudo_version = _get_go_pseudo_version(commit_url)

        provider_module_version_ref = "%s@%s" % (
            provider_module,
            pseudo_version if pseudo_version else version,
        )
        provider_source_version_ref = "%s@%s" % (
            provider_source,
            pseudo_version if pseudo_version else version,
        )

        go = Popen(
            [
                "go",
                "mod",
                "edit",
                "-replace=%s=%s" % (provider_module, provider_source_version_ref),
            ],
            cwd=path,
        )
        go.wait()

    elif not provider_module_version and major_version and int(major_version) > 1:
        provider_source_elements = _split_provider_source(provider_source)

        if major_version and int(major_version) > 1:
            _logger.error(
                "Using a versionless provider module %s with a version reference %s; converting to pseudo-version",
                provider_source,
                version,
            )

            tags_url = "https://api.github.com/repos/%s/%s/git/refs/tags/%s" % (
                provider_source_elements[1],
                provider_source_elements[2],
                version,
            )
            pseudo_version = _get_go_pseudo_version(_get_commit_url_from_tag(tags_url))

        else:
            _logger.error(
                "Using a versionless provider module %s with a commit reference %s; converting to pseudo-version",
                provider_source,
                version,
            )

            commit_url = "https://api.github.com/repos/%s/%s/commits/%s" % (
                provider_source_elements[1],
                provider_source_elements[2],
                version,
            )
            pseudo_version = _get_go_pseudo_version(commit_url)

        provider_module_version_ref = "%s@%s" % (provider_module, pseudo_version)
    else:
        provider_module_version_ref = "%s@%s" % (provider_module, version)

    if is_shim:
        go = Popen(
            ["go", "mod", "edit", "-module", "%s/shim" % provider_module],
            cwd=path,
        )
        go.wait()

    go = Popen(["go", "mod", "edit", "-require", provider_module_version_ref], cwd=path)
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

if "{{ cookiecutter.terraform_sdk_version }}".lower() != "plugin-framework":
    remove_plugin_framework_files()

if "{{ cookiecutter.provider_github_organization }}".lower() == "pulumiverse":
    os.remove(os.path.join(PROJECT_DIRECTORY, "CODE-OF-CONDUCT.md"))

if "{{ cookiecutter.skip_git_init }}".lower() not in [
    "true",
    "1",
    "yes",
    "y",
]:
    init_git()
