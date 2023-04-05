module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/provider

go 1.18

replace (
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
	github.com/hashicorp/go-getter v1.5.0 => github.com/hashicorp/go-getter v1.4.0
	{% if cookiecutter.terraform_sdk_version == "2" -%}
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 v2.0.0-20220725190814-23001ad6ec03
	{% endif -%}
	{% endif -%}
	{% if cookiecutter.terraform_provider_package_name.startswith("internal") -%}
	{{ cookiecutter.terraform_provider_module }}/shim => ./shim
	{% endif -%}
)

require (
	{% if not cookiecutter.terraform_provider_package_name.startswith("internal") -%}
	{{ cookiecutter.terraform_provider_module }} {{ cookiecutter.terraform_provider_version_or_commit | go_module_version_tag }}
	{% endif %}
	{% if cookiecutter.terraform_sdk_version == "plugin-framework" -%}
	github.com/pulumi/pulumi-terraform-bridge/pf v0.7.0
	{% endif -%}
	github.com/pulumi/pulumi-terraform-bridge/v3 v3.43.0
	github.com/pulumi/pulumi/sdk/v3 v3.36.0
)
