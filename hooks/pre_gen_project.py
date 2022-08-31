import re
import sys

sys.path.append("{{ cookiecutter._repo_dir }}")

from utils.version import Version

def _error_exit(msg):
    # exits with status 1 to indicate failure
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


PROVIDER_NAME_REGEX = r"^[a-zA-Z0-9]+$"
provider_name = "{{ cookiecutter.terraform_provider_name }}"
if re.match(r"terraform-?provider-?", provider_name):
    _error_exit("provider name MUST NOT start with terraform-provider-")
if not re.match(PROVIDER_NAME_REGEX, provider_name):
    _error_exit("%s IS NOT a valid terraform provider name!" % provider_name)


SHA_COMMIT_REGEX = r"^[0-9a-f]{40}$"
terraform_provider_version = "{{ cookiecutter.terraform_provider_version_or_commit | trim }}"
if not Version.isvalid(terraform_provider_version) and not re.match(SHA_COMMIT_REGEX, terraform_provider_version):
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
if not "{{ cookiecutter.provider_category }}" in VALID_CATEGORIES:
    _error_exit(f"provider_category MUST BE one of {VALID_CATEGORIES}")

SDK_VERSION_REGEX = r"^\s*[12]\s*$"
terraform_sdk_version = "{{cookiecutter.terraform_sdk_version | trim }}"
if not re.match(SDK_VERSION_REGEX, terraform_sdk_version):
    _error_exit(
        "%s IS NOT a valid Terrafom SDK version! Only 1 or 2 are allowed as values"
        % terraform_sdk_version
    )

if int(terraform_sdk_version) != 2:
    _error_exit(
        f"Currently only Terraform providers using Terraform SDK V2 are supported"
    )
