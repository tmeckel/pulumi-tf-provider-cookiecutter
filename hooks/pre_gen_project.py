import re
import sys

from packaging import version


def _error_exit(msg):
    # exits with status 1 to indicate failure
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


PROVIDER_NAME_REGEX = r"^[a-zA-Z0-9-]+$"
provider_name = "{{ cookiecutter.terraform_provider_name }}"
if re.match(r"terraform-?provider-?", provider_name):
    _error_exit("provider name MUST NOT start with terraform-provider-")
if not re.match(PROVIDER_NAME_REGEX, provider_name):
    _error_exit("%s IS NOT a valid terraform provider name!" % provider_name)


VERSION_SHA_COMMIT_REGEX = r"^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$|[0-9a-f]{40}"
terraform_provider_version = "{{ cookiecutter.terraform_provider_version_or_commit }}"
if not re.match(VERSION_SHA_COMMIT_REGEX, terraform_provider_version):
    _error_exit(
        "%s IS NOT a valid version! Eiter a semver compatible version 0.0.0 or a commit hash must be specified."
        % terraform_provider_version
    )

VALID_CATEGORIES = [
    "cloud",
    "database",
    "infrastructure",
    "monitoring",
    "network",
    "utility",
    "versioncontrol",
]
if "{{ cookiecutter.provider_category }}" not in VALID_CATEGORIES:
    _error_exit(f"provider_category MUST BE one of {VALID_CATEGORIES}")

SDK_VERSION_REGEX = r"^\s*([12]|plugin-framework)\s*$"
terraform_sdk_version = "{{cookiecutter.terraform_sdk_version | trim }}"
if not re.match(SDK_VERSION_REGEX, terraform_sdk_version):
    _error_exit(
        "%s IS NOT a valid Terrafom SDK version! Only 2 or plugin-framework are allowed as values"
        % terraform_sdk_version
    )

if "{{ cookiecutter.provider_logoUrl }}":
    from urllib.parse import urlparse

    url = urlparse("{{ cookiecutter.provider_logoUrl }}")
    if not url.scheme or url.scheme not in ["http", "https"]:
        _error_exit(
            "The provider logo must be an absolute HTTP(s) URL"
            % "{{ cookiecutter.provider_logoUrl }}"
        )

if version.parse("{{ cookiecutter.go_version }}") <= version.parse("1.18"):
    _error_exit(
        "The specified Go version {{ cookiecutter.go_version }} is out of support. Please select a higher version"
    )
