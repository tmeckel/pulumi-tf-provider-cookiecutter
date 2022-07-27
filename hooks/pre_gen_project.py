import re
import sys

def _error_exit(msg):
    # exits with status 1 to indicate failure
    sys.stderr.write('ERROR: %s\n' % msg)
    sys.exit(1)

PROVIDER_NAME_REGEX = r'^[a-zA-Z0-9]+$'

provider_name = '{{ cookiecutter.provider_name }}'

if re.match(r'terraform-?provider-?', provider_name):
    _error_exit('provider name MUST NOT start with terraform-provider-')
if not re.match(PROVIDER_NAME_REGEX, provider_name):
    _error_exit('%s IS NOT a valid terraform provider name!' % provider_name)
