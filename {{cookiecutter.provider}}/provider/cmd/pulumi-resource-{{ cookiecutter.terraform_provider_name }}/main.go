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

//go:generate go run ./generate.go

package main

import (
	{% if cookiecutter.terraform_sdk_version == "plugin-framework" %}
	"context"
	{% endif %}
	_ "embed"

	{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
	"github.com/pulumi/pulumi-terraform-bridge/v3/pkg/tfbridge"
	"github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}/provider/pkg/version"
	{% else %}
	"github.com/pulumi/pulumi-terraform-bridge/pf/tfbridge"
	{% endif %}
	{{ cookiecutter.terraform_provider_name }} "github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}/provider"
)

//go:embed schema-embed.json
var pulumiSchema []byte

func main() {
	{% if cookiecutter.terraform_sdk_version != "plugin-framework" %}
	tfbridge.Main("{{ cookiecutter.terraform_provider_name }}", version.Version, {{ cookiecutter.terraform_provider_name }}.Provider(), pulumiSchema)
	{% else %}
	meta := tfbridge.ProviderMetadata{PackageSchema: pulumiSchema}
	tfbridge.Main(context.Background(), "{{ cookiecutter.terraform_provider_name }}", {{ cookiecutter.terraform_provider_name }}.Provider(), meta)
	{% endif %}
}
