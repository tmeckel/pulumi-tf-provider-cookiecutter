import re
from functools import lru_cache
from http import HTTPStatus
from logging import getLogger
from subprocess import PIPE, Popen
from time import sleep, time

import requests
from jinja2.environment import Environment
from jinja2.ext import Extension
from packaging import version

_logger = getLogger(__name__)


def is_truthy(
    v,
):
    return (
        v.lower().strip() in ["true", "1", "yes", "y"] if isinstance(v, str) else False
    )


def capitalize(
    v,
):
    assert isinstance(v, str)
    return v.capitalize()


def is_commit_hash(
    v,
):
    assert isinstance(v, str)
    return re.match("[0-9a-f]{40}", v)


def go_module_version(
    v,
):
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


def go_module_version_tag(
    v,
):
    if not v:
        raise ValueError("Value is empty")

    if not re.match("[0-9a-f]{40}", v) and not v.lower().startswith("v"):
        return f"v{v}"

    return v


def go_module_name(
    v,
):
    assert isinstance(v, str)
    return re.sub("/v[0-9]+$", "", v)


def version_major(
    v,
):
    assert isinstance(v, str)
    return version.parse(v).major


def version_minor(
    v,
):
    assert isinstance(v, str)
    return version.parse(v).minor


def github_call_api(
    url,
    *,
    headers=None,
    call_timeout=60.0,
):
    if headers is None:
        headers = {}

    headers = {
        **headers,
        **{
            "Accept": "application/vnd.github.v3+json",
        },
    }

    attempts = 0
    while True:
        response = requests.get(
            url,
            headers=headers,
            timeout=call_timeout,
        )

        if (
            response.status_code == HTTPStatus.FORBIDDEN
            and "X-RateLimit-Remaining" in response.headers
        ):
            # Check if the rate limit has been exceeded (GitHub-specific)
            remaining = int(response.headers["X-RateLimit-Remaining"])
            if remaining == 0:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                current_time = time()
                wait_time = reset_time - current_time + 5  # Add a buffer of 5 seconds

                _logger.warning(
                    "GitHub overall rate limit exceeded, waiting %d seconds", wait_time
                )
                sleep(wait_time)
                continue

        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            # Handle generic rate limiting with exponential backoff
            attempts += 1
            if "Retry-After" in response.headers:
                wait_time = int(response.headers["Retry-After"])
            else:
                wait_time = min(
                    2**attempts, 60
                )  # Exponential backoff capped at 60 seconds

            _logger.warning("GitHub too many requests, waiting %d seconds", wait_time)
            sleep(wait_time)
            continue

        response.raise_for_status()
        return response.json()


@lru_cache
def github_get_latest_release(
    repo,
    owner="pulumi",
):
    data = github_call_api(
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    )

    return data["tag_name"]


@lru_cache
def github_get_latest_release_commit(
    repo,
    owner="pulumi",
):
    tag = github_get_latest_release(repo, owner)

    tag_info = github_call_api(
        url=f"https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{tag}"
    )

    return tag_info["object"]["sha"]


@lru_cache
def github_download_file(
    repo,
    file_path,
    owner="pulumi",
    tag_name=None,
):
    if not tag_name:
        tag_name = github_get_latest_release(
            repo=repo,
        )

    file_url = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{tag_name}/{file_path}"
    )

    file_response = requests.get(file_url)
    file_response.raise_for_status()

    return file_response.text


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


@lru_cache
def parse_go_mod(
    contents,
):
    requirements = {}
    replacements = {}

    require_pattern = re.compile(r"^\s*require\s*(\(\s*)?$")
    replace_pattern = re.compile(r"^\s*replace\s*(\(\s*)?$")
    module_pattern = re.compile(
        r"^\s*(?P<module>\S+)\s+(?P<version>\S+)(?:\s*//.*)?$"
    )  # Matches and ignores inline comments
    replace_module_pattern = re.compile(
        r"^\s*(?P<module>\S+)\s*=>\s*(?P<replace_module>\S+)(?:\s+(?P<version>\S+))?(?:\s*//.*)?$"
    )  # Matches and ignores inline comments

    in_require_block = False
    in_replace_block = False

    for line in contents.splitlines():
        line = line.strip()  # noqa: PLW2901

        if require_pattern.match(line):
            in_require_block = True
            continue

        if replace_pattern.match(line):
            in_replace_block = True
            continue

        if in_require_block and line == ")":
            in_require_block = False
            continue

        if in_replace_block and line == ")":
            in_replace_block = False
            continue

        if (in_require_block or line.startswith("require")) and not line.startswith(
            "replace"
        ):
            match = module_pattern.match(line.removeprefix("require").strip())
            if match:
                module = match.group("module")
                version = match.group("version")
                requirements[module] = version

        if in_replace_block or line.startswith("replace"):
            match = replace_module_pattern.match(line.removeprefix("replace").strip())
            if match:
                module = match.group("module")
                replace_module = match.group("replace_module")
                version = match.group("version")
                replacements[module] = (replace_module, version)

    return requirements, replacements


@lru_cache
def parse_terraform_brige_go_mod(
    version=None,
):
    go_mod = github_download_file(
        repo="pulumi-terraform-bridge",
        file_path="go.mod",
        tag_name=version,
    )
    return parse_go_mod(contents=go_mod)


@lru_cache
def github_get_latest_semver_tag(
    repo,
    owner="pulumi",
    prefix="",
):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    # Escape the prefix for use in regex
    escaped_prefix = re.escape(prefix)
    semver_pattern = re.compile(rf"^{escaped_prefix}(?P<version>\d+\.\d+\.\d+)$")

    semver_tags = []
    page = 1

    while True:
        url = f"{base_url}?page={page}&per_page=100"
        tags = github_call_api(
            url=url,
        )
        if not tags:
            break

        for tag in tags:
            match = semver_pattern.match(tag["name"])
            if match:
                semver_tags.append((tag["name"], version.parse(match.group("version"))))

        page += 1

    if not semver_tags:
        return None

    # Sort by semantic versioning using the captured version part
    semver_tags.sort(key=lambda t: t[1])

    # The last item will be the latest version
    return semver_tags[-1]


def get_terraform_plugin_sdkv2_version():
    _, replacements = parse_terraform_brige_go_mod(
        version=github_get_latest_release("pulumi-terraform-bridge"),
    )
    return replacements["github.com/hashicorp/terraform-plugin-sdk/v2"][1]


def get_pulumi_sdk_version():
    requirements, _ = parse_terraform_brige_go_mod(
        version=github_get_latest_release("pulumi-terraform-bridge"),
    )
    return requirements["github.com/pulumi/pulumi/sdk/v3"]


def get_terraform_bridge_pf_version():
    result = github_get_latest_semver_tag(
        repo="pulumi-terraform-bridge",
        prefix="pf/v",
    )
    return f"v{result[1]!s}"


class LocalExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        environment.globals["github_get_latest_release"] = github_get_latest_release
        environment.globals[
            "github_get_latest_release_commit"
        ] = github_get_latest_release_commit
        environment.globals["get_go_version"] = get_go_version
        environment.globals[
            "get_terraform_plugin_sdkv2_version"
        ] = get_terraform_plugin_sdkv2_version
        environment.globals[
            "get_terraform_bridge_pf_version"
        ] = get_terraform_bridge_pf_version
        environment.globals["get_pulumi_sdk_version"] = get_pulumi_sdk_version
        environment.filters["truthy"] = is_truthy
        environment.filters["capitalize"] = capitalize
        environment.filters["go_module_version"] = go_module_version
        environment.filters["go_module_name"] = go_module_name
        environment.filters["go_module_version_tag"] = go_module_version_tag
        environment.filters["version_major"] = version_major
        environment.filters["version_minor"] = version_minor
        environment.filters["is_commit_hash"] = is_commit_hash
