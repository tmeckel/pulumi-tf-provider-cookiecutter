module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/sdk

go {{ cookiecutter.__go_version_major }}.{{ cookiecutter.__go_version_minor }}

require github.com/pulumi/pulumi/sdk/v3 {{ cookiecutter.__pulumi_sdk_version }}
