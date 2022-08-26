package shim

import (
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
)

func NewProvider() *schema.Provider {
	{% set list = cookiecutter.terraform_provider_package_name.split('/') -%}
	return {{ list[-1] }}.Provider()
}
