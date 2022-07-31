module github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/provider

go 1.16

replace (
	github.com/hashicorp/go-getter v1.5.0 => github.com/hashicorp/go-getter v1.4.0
	github.com/hashicorp/terraform-plugin-sdk/v2 => github.com/pulumi/terraform-plugin-sdk/v2 v2.0.0-20220505215311-795430389fa7
	{% if cookiecutter.create_shim is truthy -%}
	{{ cookiecutter.terraform_provider_source }}/shim => ./shim
	{% endif -%}
)

require (
	{% if cookiecutter.create_shim | lower not in [ 'true', '1', 'yes', 'y' ] -%}
	{{ cookiecutter.terraform_provider_source }} v{{ cookiecutter.terraform_provider_version }}
	{% endif -%}
	github.com/pulumi/pulumi-terraform-bridge/v3 v3.26.0
	github.com/pulumi/pulumi/sdk/v3 v3.36.0
)
