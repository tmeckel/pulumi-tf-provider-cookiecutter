import re
import sys


def _error_exit(msg):
    # exits with status 1 to indicate failure
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


PROVIDER_NAME_REGEX = r"^[a-zA-Z0-9]+$"
VERION_REGEX = r"^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$"

provider_name = "{{ cookiecutter.terraform_provider_name }}"

if re.match(r"terraform-?provider-?", provider_name):
    _error_exit("provider name MUST NOT start with terraform-provider-")
if not re.match(PROVIDER_NAME_REGEX, provider_name):
    _error_exit("%s IS NOT a valid terraform provider name!" % provider_name)

terraform_provider_version = "{{ cookiecutter.terraform_provider_version }}"

if not re.match(VERION_REGEX, terraform_provider_version):
    _error_exit("%s IS NOT a valid version!" % terraform_provider_version)

if "{{ cookiecutter.create_shim }}".lower() in ["true", "1", "yes", "y"] and not "{{ cookiecutter.terraform_provider_internal_package }}":
    _error_exit("terraform_provider_internal_package MUST BE set if using a SHIM!")
