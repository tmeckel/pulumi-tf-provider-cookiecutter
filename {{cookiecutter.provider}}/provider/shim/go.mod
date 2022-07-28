module {{ cookiecutter.terraform_provider_source }}/shim

go 1.16

require (
	github.com/hashicorp/terraform-plugin-sdk/v2 v2.7.0
	{{ cookiecutter.terraform_provider_source }} v{{ cookiecutter.terraform_provider_version }}
)
