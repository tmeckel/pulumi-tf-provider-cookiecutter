// Copyright 2016-2018, Pulumi Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package {{ cookiecutter.terraform_provider_name }}

import (
	"fmt"
	"path/filepath"

{%- if cookiecutter.terraform_sdk_version == "2" %}
	"github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfbridge"
	shim "github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfshim"
	shimv2 "github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfshim/sdk-v2"
	"github.com/pulumi/pulumi/sdk/v3/go/common/resource"
{%- endif %}
{%- if cookiecutter.terraform_provider_package_name.startswith("internal") %}
	shimprovider "{{ cookiecutter.terraform_provider_module }}/shim"
{%- else %}
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
{%- endif %}
{%- if cookiecutter.terraform_sdk_version == "plugin-framework" %}
	pf "github.com/pulumi/pulumi-terraform-bridge/pf/tfbridge"
	"github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfbridge"
{%- endif %}
	"github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}/provider/pkg/version"
)

// all of the token components used below.
const (
	// This variable controls the default name of the package in the package
	// registries for nodejs and python:
	mainPkg = "{{ cookiecutter.terraform_provider_name }}"
	// modules:
	mainMod = "index" // the {{ cookiecutter.terraform_provider_name }} module
)

{% if cookiecutter.terraform_sdk_version == "2" -%}
// preConfigureCallback is called before the providerConfigure function of the underlying provider.
// It should validate that the provider can be configured, and provide actionable errors in the case
// it cannot be. Configuration variables can be read from `vars` using the `stringValue` function -
// for example `stringValue(vars, "accessKey")`.
func preConfigureCallback(vars resource.PropertyMap, c shim.ResourceConfig) error {
	return nil
}
{% endif %}

// Provider returns additional overlaid schema and metadata associated with the provider..
{% if cookiecutter.terraform_sdk_version == "2" -%}
func Provider() tfbridge.ProviderInfo {
{% else -%}
func Provider() pf.ProviderInfo {
{% endif -%}
{% if cookiecutter.terraform_sdk_version == "2" -%}
	// Instantiate the Terraform provider
{% if cookiecutter.terraform_provider_package_name.startswith("internal") -%}
	p := shimv2.NewProvider(shimprovider.NewProvider())
{% else -%}
	p := shimv2.NewProvider({{ cookiecutter.terraform_provider_package_name }}.Provider())
{%- endif -%}
{% endif -%}

	// Create a Pulumi provider mapping
	prov := tfbridge.ProviderInfo{
		{% if cookiecutter.terraform_sdk_version == "2" -%}
		P:    p,
		{% endif -%}
		Name: "{{ cookiecutter.terraform_provider_name }}",
		// DisplayName is a way to be able to change the casing of the provider
		// name when being displayed on the Pulumi registry
		DisplayName: "{{ cookiecutter.provider_display_name }}",
		// The default publisher for all packages is Pulumi.
		// Change this to your personal name (or a company name) that you
		// would like to be shown in the Pulumi Registry if this package is published
		// there.
		Publisher: "{{ cookiecutter.provider_publisher }}",
		// LogoURL is optional but useful to help identify your package in the Pulumi Registry
		// if this package is published there.
		//
		// You may host a logo on a domain you control or add an SVG logo for your package
		// in your repository and use the raw content URL for that file as your logo URL.
		LogoURL: "{{ cookiecutter.provider_logoUrl }}",
		// PluginDownloadURL is an optional URL used to download the Provider
		// for use in Pulumi programs
		// e.g https://github.com/org/pulumi-provider-name/releases/
		PluginDownloadURL: "{{ cookiecutter.provider_download_url }}",
		Description:       "{{ cookiecutter.provider_description }}",
		// category/cloud tag helps with categorizing the package in the Pulumi Registry.
		// For all available categories, see `Keywords` in
		// https://www.pulumi.com/docs/guides/pulumi-packages/schema/#package.
		Keywords:   []string{
			"pulumi",
			"{{ cookiecutter.terraform_provider_name }}",
			"category/{{ cookiecutter.provider_category }}",
		},
		License:    "Apache-2.0",
		Homepage:   "{{ cookiecutter.provider_homepage }}",
		Repository: "https://github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}",
		// The GitHub Org for the provider - defaults to `terraform-providers`. Note that this
		// should match the TF provider module's require directive, not any replace directives.
		GitHubOrg: "{{ cookiecutter.terraform_provider_org }}",
		Config:    map[string]*tfbridge.SchemaInfo{
			// Add any required configuration here, or remove the example below if
			// no additional points are required.
			// "region": {
			// 	Type: tfbridge.MakeType("region", "Region"),
			// 	Default: &tfbridge.DefaultInfo{
			// 		EnvVars: []string{"AWS_REGION", "AWS_DEFAULT_REGION"},
			// 	},
			// },
		},
		{% if cookiecutter.terraform_sdk_version == "2" -%}
		PreConfigureCallback: preConfigureCallback,
		{% endif -%}
		Resources:            map[string]*tfbridge.ResourceInfo{
			// Map each resource in the Terraform provider to a Pulumi type. Two examples
			// are below - the single line form is the common case. The multi-line form is
			// needed only if you wish to override types or other default options.
			//
			// "aws_iam_role": {Tok: tfbridge.MakeResource(mainPkg, mainMod, "IamRole")}
			//
			// "aws_acm_certificate": {
			// 	Tok: tfbridge.MakeResource(mainPkg, mainMod, "Certificate"),
			// 	Fields: map[string]*tfbridge.SchemaInfo{
			// 		"tags": {Type: tfbridge.MakeType(mainPkg, "Tags")},
			// 	},
			// },
		},
		DataSources: map[string]*tfbridge.DataSourceInfo{
			// Map each resource in the Terraform provider to a Pulumi function. An example
			// is below.
			// "aws_ami": {Tok: tfbridge.MakeDataSource(mainPkg, mainMod, "getAmi")},
		},
		JavaScript: &tfbridge.JavaScriptInfo{
			PackageName: "{{ cookiecutter.provider_javascript_package }}",

			// List any npm dependencies and their versions
			Dependencies: map[string]string{
				"@pulumi/pulumi": "^3.0.0",
			},
			DevDependencies: map[string]string{
				"@types/node": "^10.0.0", // so we can access strongly typed node definitions.
				"@types/mime": "^2.0.0",
			},
			// See the documentation for tfbridge.OverlayInfo for how to lay out this
			// section, or refer to the AWS provider. Delete this section if there are
			// no overlay files.
			//Overlay: &tfbridge.OverlayInfo{},
		},
		Python: &tfbridge.PythonInfo{
			PackageName: "{{ cookiecutter.provider_python_package }}",

			// List any Python dependencies and their version ranges
			Requires: map[string]string{
				"pulumi": ">=3.0.0,<4.0.0",
			},
		},
		Golang: &tfbridge.GolangInfo{
			ImportBasePath: filepath.Join(
				fmt.Sprintf("github.com/pulumi/pulumi-%[1]s/sdk/", mainPkg),
				tfbridge.GetModuleMajorVersion(version.Version),
				"go",
				mainPkg,
			),
			GenerateResourceContainerTypes: true,
		},
		CSharp: &tfbridge.CSharpInfo{
			RootNamespace: "{{ cookiecutter.provider_dotnet_rootnamespace }}",

			PackageReferences: map[string]string{
				"Pulumi": "3.*",
			},
		},
		Java: &tfbridge.JavaInfo{
			BasePackage: "{{ cookiecutter.provider_java_base_package }}",
		},
	}

{% if cookiecutter.terraform_sdk_version == "2" %}
	prov.SetAutonaming(255, "-")

	return prov
{% elif cookiecutter.terraform_sdk_version == "plugin-framework" %}
	return pf.ProviderInfo{
		ProviderInfo: prov,
{%- if cookiecutter.terraform_provider_package_name.startswith("internal") %}
		NewProvider:  shimprovider.NewProvider(),
{%- else %}
		{{ cookiecutter.terraform_provider_package_name }}.NewProvider()
{% endif %}
	}
{% endif -%}
}
