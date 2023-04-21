module {{ cookiecutter.terraform_provider_source }}/shim

go 1.19

require (
{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
	github.com/hashicorp/terraform-plugin-sdk/v2 v2.19.0
{% elif cookiecutter.terraform_sdk_version == "plugin-framework" -%}
	github.com/hashicorp/terraform-plugin-framework v1.1.1
{% endif -%}
)
