package shim

{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
import (
	{% if cookiecutter.terraform_sdk_version == "1" %}
	"github.com/hashicorp/terraform-plugin-sdk/helper/schema"
	{% else %}
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	{% endif %}
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
)

func NewProvider() *schema.Provider {
	{% set provider_path = cookiecutter.terraform_provider_package_name.split('/') %}
	p, _ := {{ provider_path | last }}.New()
	return p
}
{% elif cookiecutter.terraform_sdk_version == "plugin-framework" %}
import (
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
	tf "github.com/hashicorp/terraform-plugin-framework/provider"
)

func NewProvider() tf.Provider {
	{% set provider_path = cookiecutter.terraform_provider_package_name.split('/') %}
	return {{ provider_path | last }}.New()
}
{% endif %}
