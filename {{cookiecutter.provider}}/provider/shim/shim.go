package shim

import (
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"{{ cookiecutter.terraform_provider_source }}/internal/{{ cookiecutter.terraform_provider_internal_name }}"
)

func NewProvider() *schema.Provider {
	return {{ cookiecutter.terraform_provider_internal_name }}.Provider()
}
