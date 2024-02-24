import re
from subprocess import PIPE, Popen

import requests
from jinja2.environment import Environment
from jinja2.ext import Extension
from packaging import version


def is_truthy(v):
    return v.lower().strip() in ["true", "1", "yes", "y"]


def capitalize(v):
    return v.capitalize()


def is_commit_hash(v):
    return re.match("[0-9a-f]{40}", v)


def go_module_version(v):
    if not v:
        raise ValueError("Value is empty")

    try:
        i = v.rindex("/v")
        v = v[i + 1 :]
    except ValueError:
        pass

    if re.match("[0-9a-f]{40}", v):
        return ""

    if v.lower().startswith("v"):
        v = v[1:]

    if not v[0].isdigit():
        return ""

    version = v.split(".")
    major = int(version[0])
    if major > 1:
        return "/v%s" % major
    else:
        return ""


def go_module_version_tag(v):
    if not v:
        raise ValueError("Value is empty")

    if not re.match("[0-9a-f]{40}", v) and not v.lower().startswith("v"):
        return f"v{v}"

    return v


def go_module_name(v):
    return re.sub("/v[0-9]+$", "", v)


def version_major(v):
    return version.parse(v).major


def version_minor(v):
    return version.parse(v).minor


def get_latest_release(repo, owner="pulumi"):
    release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(release_url)
    data = response.json()

    return data["tag_name"]


def get_latest_release_commit(repo, owner="pulumi"):
    tag = get_latest_release(repo, owner)

    tag_info_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{tag}"
    response = requests.get(tag_info_url)
    tag_info = response.json()

    return tag_info["object"]["sha"]


def get_go_version():
    """
    Returns the Go language version installed on the system as a version.Version object.

    This function executes the 'go env GOVERSION' command using Popen and parses the version string
    into a `packaging.version.Version` object.

    Returns:
        version.Version: The Go version as a `packaging.version.Version` object.

    Raises:
        Exception: If the command fails to execute or returns an error.
    """
    process = Popen(
        ["go", "env", "GOVERSION"],
        stdout=PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        go_version_str = stdout.strip().lstrip("go")
        return version.parse(go_version_str)
    else:
        raise Exception(f"Failed to get go version: {stderr}")


class LocalExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.globals["get_latest_release"] = get_latest_release
        environment.globals["get_latest_release_commit"] = get_latest_release_commit
        environment.globals["get_go_version"] = get_go_version
        environment.filters["truthy"] = is_truthy
        environment.filters["capitalize"] = capitalize
        environment.filters["go_module_version"] = go_module_version
        environment.filters["go_module_name"] = go_module_name
        environment.filters["go_module_version_tag"] = go_module_version_tag
        environment.filters["version_major"] = version_major
        environment.filters["version_minor"] = version_minor
        environment.filters["is_commit_hash"] = is_commit_hash
