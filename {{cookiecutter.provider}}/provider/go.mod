module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/provider

go 1.19

replace (
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
	{% if cookiecutter.terraform_sdk_version == "2" -%}
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 v2.0.0-20220725190814-23001ad6ec03
	{% endif -%}
	{% endif -%}
	{% if cookiecutter.terraform_provider_package_name.startswith("internal") -%}
	{{ cookiecutter.terraform_provider_module }}/shim => ./shim
	{% endif -%}
)

require (
	github.com/ettle/strcase v0.1.1
	{% if not cookiecutter.terraform_provider_package_name.startswith("internal") -%}
	{{ cookiecutter.terraform_provider_module }} {{ cookiecutter.terraform_provider_version_or_commit | go_module_version_tag }}
	{% endif %}
	{% if cookiecutter.terraform_sdk_version == "plugin-framework" -%}
	github.com/pulumi/pulumi-terraform-bridge/pf v0.8.0
	github.com/pulumi/pulumi-terraform-bridge/v3 v3.44.4-0.20230420140533-43153340d9bb
	{% else -%}
	github.com/pulumi/pulumi-terraform-bridge/v3 v3.44.3
	{% endif -%}
	github.com/pulumi/pulumi/sdk/v3 v3.64.0
)
