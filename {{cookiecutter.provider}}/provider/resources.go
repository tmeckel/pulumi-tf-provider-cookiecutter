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

package provider

import (
	_ "embed"
	"fmt"
	"path/filepath"
	"strings"
	"unicode"

	"github.com/ettle/strcase"
	"github.com/pulumi/pulumi/sdk/v3/go/common/tokens"
	"github.com/pulumi/pulumi/sdk/v3/go/common/util/contract"
	"github.com/pulumi/pulumi/sdk/v3/go/common/resource"
	shim "github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfshim"
	"github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfbridge"
{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
	{% if cookiecutter.terraform_sdk_version == "1" %}
	shimv1 "github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfshim/sdk-v1"
	{% else %}
	shimv2 "github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfshim/sdk-v2"
	{% endif %}
{% endif %}
{% if cookiecutter.terraform_provider_package_name.startswith("internal") %}
	shimprovider "{{ cookiecutter.terraform_provider_module }}/shim"
{% else %}
	"{{ cookiecutter.terraform_provider_module }}/{{ cookiecutter.terraform_provider_package_name }}"
{% endif %}
{% if cookiecutter.terraform_sdk_version == "plugin-framework" %}
	pf "github.com/pulumi/pulumi-terraform-bridge/pf/tfbridge"
{% endif %}
	"github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}/provider/pkg/version"
)

{% if cookiecutter.provider_mapping_strategy != "manual" %}
//go:embed cmd/pulumi-resource-{{ cookiecutter.terraform_provider_name }}/bridge-metadata.json
var bridgeMetadata []byte

{% endif %}
// all of the token components used below.
const (
	// This variable controls the default name of the package in the package
	mainMod = "index" // the {{ cookiecutter.terraform_provider_name }} module
)

{% if cookiecutter.provider_naming_strategy != "flat" %}
var module_overrides = map[string]string{}

{% endif %}
func convertName(tfname string) (module string, name string) {
	tfNameItems := strings.Split(tfname, "_")
	contract.Assertf(len(tfNameItems) >= 2, "Invalid snake case name %s", tfname)
	contract.Assertf(tfNameItems[0] == "{{ cookiecutter.terraform_provider_name }}", "Invalid snake case name %s. Does not start with {{ cookiecutter.terraform_provider_name }}", tfname)
	{% if cookiecutter.provider_naming_strategy != "flat" %}
	if len(tfNameItems) == 2 {
		module = mainMod
		name = tfNameItems[1]
	} else {
		{% if cookiecutter.provider_naming_strategy == "singlelevel" %}
		module = strcase.ToPascal(strings.Join(tfNameItems[1:len(tfNameItems)-1], "_"))
		name = tfNameItems[len(tfNameItems)-1]
		{% else %}
		module = strings.Join(tfNameItems[1:len(tfNameItems)-1], "/")
		name = tfNameItems[len(tfNameItems)-1]
		{% endif %}

		if v, ok := module_overrides[module]; ok {
			module = v
		}
	}
	contract.Assertf(!unicode.IsDigit(rune(module[0])), "Pulumi namespace must not start with a digit: %s", name)
	{% else %}
	module = mainMod
	name = strings.Join(tfNameItems[1:], "_")
	{% endif %}
	contract.Assertf(!unicode.IsDigit(rune(name[0])), "Pulumi name must not start with a digit: %s", name)
	name = strcase.ToPascal(name)
	return
}

func makeDataSource(ds string) tokens.ModuleMember {
	mod, name := convertName(ds)
	return tfbridge.MakeDataSource("{{ cookiecutter.terraform_provider_name }}", mod, "get"+name)
}

func makeResource(res string) tokens.Type {
	mod, name := convertName(res)
	return tfbridge.MakeResource("{{ cookiecutter.terraform_provider_name }}", mod, name)
}

{% if cookiecutter.provider_mapping_strategy != "manual" %}
func moduleComputeStrategy() tfbridge.Strategy {
	return tfbridge.Strategy{
		Resource: func(tfToken string, elem *tfbridge.ResourceInfo) error {
			elem.Tok = makeResource(tfToken)
			return nil
		},
		DataSource: func(tfToken string, elem *tfbridge.DataSourceInfo) error {
			elem.Tok = makeDataSource(tfToken)
			return nil
		},
	}
}

{% endif %}
// preConfigureCallback is called before the providerConfigure function of the underlying provider.
// It should validate that the provider can be configured, and provide actionable errors in the case
// it cannot be. Configuration variables can be read from `vars` using the `stringValue` function -
// for example `stringValue(vars, "accessKey")`.
func preConfigureCallback(vars resource.PropertyMap, c shim.ResourceConfig) error {
	return nil
}

// Provider returns additional overlaid schema and metadata associated with the provider..
func Provider() tfbridge.ProviderInfo {
	{% set provider_path = cookiecutter.terraform_provider_package_name.split('/') %}
	// Instantiate the Terraform provider
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
		{% if cookiecutter.terraform_provider_package_name.startswith("internal") %}
			{% if cookiecutter.terraform_sdk_version == "1" %}
	p := shimv1.NewProvider(shimprovider.NewProvider())
			{% else %}
	p := shimv2.NewProvider(shimprovider.NewProvider())
			{% endif %}
		{% else %}
			{% if cookiecutter.terraform_sdk_version == "1" %}
	p := shimv1.NewProvider({{ provider_path | last }}.Provider())
			{% else %}
	p := shimv2.NewProvider({{ provider_path | last }}.Provider())
			{% endif %}
		{% endif %}
	{% else %}
		{% if cookiecutter.terraform_provider_package_name.startswith("internal") %}
	p := pf.ShimProvider(shimprovider.NewProvider())
		{% else %}
	p := pf.ShimProvider({{ provider_path | last }}.NewProvider())
		{% endif %}
	{% endif %}

	// Create a Pulumi provider mapping
	prov := tfbridge.ProviderInfo{
		P:    p,
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
		Version:   version.Version,
		GitHubOrg: "{{ cookiecutter.terraform_provider_org }}",
		{% if cookiecutter.provider_mapping_strategy != "manual" %}
		MetadataInfo: tfbridge.NewProviderMetadata(bridgeMetadata),
		{% endif %}
		TFProviderVersion: "{{ cookiecutter.terraform_provider_version_or_commit }}",
		{% set tf_go_module_version = cookiecutter.terraform_provider_module | go_module_version %}
		{% if tf_go_module_version %}
		TFProviderModuleVersion: "{{ tf_go_module_version.lstrip("/") }}",
		{% endif %}
		{% if cookiecutter.terraform_provider_module != cookiecutter.terraform_provider_source or cookiecutter.terraform_provider_module | go_module_version != cookiecutter.terraform_provider_version_or_commit | go_module_version %}
		UpstreamRepoPath: "./upstream",
		{% endif %}
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
		PreConfigureCallback: preConfigureCallback,
		Resources:            map[string]*tfbridge.ResourceInfo{
			// Map each resource in the Terraform provider to a Pulumi type.
			//
			// "aws_iam_role": {
			//   Tok: makeResource(mainMod, "aws_iam_role"),
		  // },
		},
		DataSources: map[string]*tfbridge.DataSourceInfo{
			// Map each data source in the Terraform provider to a Pulumi function.
			//
			// "aws_ami": {
			//	Tok: makeDataSource(mainMod, "aws_ami"),
			// },
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
				fmt.Sprintf("github.com/{{ cookiecutter.provider_github_organization }}/pulumi-%[1]s/sdk/", "{{ cookiecutter.terraform_provider_name }}"),
				tfbridge.GetModuleMajorVersion(version.Version),
				"go",
				"{{ cookiecutter.terraform_provider_name }}",
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

	{% if cookiecutter.provider_mapping_strategy != "manual" %}
	prov.MustComputeTokens(moduleComputeStrategy())
	{% endif %}
	prov.SetAutonaming(255, "-")

	return prov
}
