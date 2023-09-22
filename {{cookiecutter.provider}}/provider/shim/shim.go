package shim

{% if cookiecutter.terraform_sdk_version != "plugin-framework" -%}
import (
	{% if cookiecutter.terraform_sdk_version == "1" -%}
	"github.com/hashicorp/terraform-plugin-sdk/helper/schema"
	{% else -%}
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	{% endif %}
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

func NewProvider() tf.Provider {
		return provider.New()
}
{% endif -%}
