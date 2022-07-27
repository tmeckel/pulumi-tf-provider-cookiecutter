module github.com/hashicorp/terraform-provider-time/shim

go 1.16

require (
	github.com/hashicorp/terraform-plugin-sdk/v2 v2.7.0
	{{ cookiecutter.terraform_provider_source }} {{ cookiecutter.terraform_provider_version }}
)
