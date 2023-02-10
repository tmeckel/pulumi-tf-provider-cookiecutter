package shim

{% if cookiecutter.terraform_sdk_version == "2" -%}
import (
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
)

func NewProvider() *schema.Provider {
	{% set list = cookiecutter.terraform_provider_package_name.split('/') -%}
	p, _ := {{ list[-1] }}.New()
	return p
}
{% elif cookiecutter.terraform_sdk_version == "plugin-framework" -%}
import (
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
	tf "github.com/hashicorp/terraform-plugin-framework/provider"
)

func NewProvider() func() tf.Provider {
	return func() tf.Provider {
		return provider.New()
	}
}
{% endif -%}
