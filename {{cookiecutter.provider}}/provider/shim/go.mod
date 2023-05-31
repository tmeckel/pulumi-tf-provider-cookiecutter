module {{ cookiecutter.terraform_provider_source }}/shim

go {{ cookiecutter.__go_version_major }}.{{ cookiecutter.__go_version_minor }}

require (
{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
	github.com/hashicorp/terraform-plugin-sdk/v2 v2.19.0
{% elif cookiecutter.terraform_sdk_version == "plugin-framework" -%}
	github.com/hashicorp/terraform-plugin-framework v1.1.1
{% endif -%}
)
