module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/provider

go {{ cookiecutter.__go_version_major }}.{{ cookiecutter.__go_version_minor }}

replace (
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
	{% if cookiecutter.terraform_sdk_version == "2" -%}
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 v2.0.0-20230710100801-03a71d0fca3d
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
)
