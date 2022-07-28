package shim

import (
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"{{ cookiecutter.terraform_provider_source }}/{{ cookiecutter.terraform_provider_internal_package }}"
)

func NewProvider() *schema.Provider {
	{% set list = cookiecutter.terraform_provider_internal_package.split('/') -%}
	return {{ list[-1] }}.Provider()
}
