import re
import requests
from packaging import version

from jinja2.environment import Environment
from jinja2.ext import Extension


def is_truthy(v):
    return v.lower().strip() in ["true", "1", "yes", "y"]


def capitalize(v):
    return v.capitalize()


def go_module_version(v):
    if not v:
        raise ValueError("Value is empty")
    if re.match("[0-9a-f]{40}", v):
        return ""

    if v.lower().startswith("v"):
        v = v[1:]
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

def get_latest_release(repo, owner = "pulumi"):
    release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(release_url)
    data = response.json()

    return data["tag_name"]

def get_latest_release_commit(repo, owner = "pulumi"):
    tag = get_latest_release(repo, owner)

    tag_info_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{tag}"
    response = requests.get(tag_info_url)
    tag_info = response.json()

    return tag_info["object"]["sha"]

class LocalExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.globals["get_latest_release"] = get_latest_release
        environment.globals["get_latest_release_commit"] = get_latest_release_commit
        environment.tests["truthy"] = is_truthy
        environment.filters["capitalize"] = capitalize
        environment.filters["go_module_version"] = go_module_version
        environment.filters["go_module_name"] = go_module_name
        environment.filters["go_module_version_tag"] = go_module_version_tag
        environment.filters["version_major"] = version_major
        environment.filters["version_minor"] = version_minor
