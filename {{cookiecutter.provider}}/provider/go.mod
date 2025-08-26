module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/provider

go {{ cookiecutter.__go_version_major }}.{{ cookiecutter.__go_version_minor }}

replace (
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
	{% if cookiecutter.terraform_sdk_version == "2" %}
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 {{ cookiecutter.__pulumi_terraform_plugin_sdkv2_version }}
	{% endif %}
	{% endif %}
	{% if cookiecutter.terraform_provider_package_name.startswith("internal") %}
	{{ cookiecutter.terraform_provider_module }}/shim => ./shim
	{% endif %}
)

require (
	github.com/ettle/strcase v0.2.0
	github.com/pulumi/pulumi-terraform-bridge/v3 {{ cookiecutter.__pulumi_terraform_bridge_version }}
	{% if cookiecutter.terraform_sdk_version == "plugin-framework" %}
	github.com/pulumi/pulumi-terraform-bridge/pf {{ cookiecutter.__pulumi_terraform_bridge_pf_version }}
	{% endif %}
	github.com/pulumi/pulumi/sdk/v3 {{ cookiecutter.__pulumi_sdk_version }}
)
