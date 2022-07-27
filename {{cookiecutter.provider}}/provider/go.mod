module github.com/{{ cookiecutter.github_organization }}/pulumi-{{ cookiecutter.provider_name }}/provider

go 1.18

replace (
	github.com/hashicorp/go-getter v1.5.0 => github.com/hashicorp/go-getter v1.4.0
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 v2.0.0-20220505215311-795430389fa7
	{% if cookiecutter.create_shim | lower in [ 'true', '1', 'yes', 'y' ] -%}
	{{ cookiecutter.terraform_provider_source }}/shim => ./shim
	{%- endif %}
)

require (
	github.com/pulumi/pulumi-terraform-bridge/v3 v3.26.0
	github.com/pulumi/pulumi/sdk/v3 v3.36.0
)
