---
title: {{ cookiecutter.terraform_provider_name | capitalize }} Installation & Configuration
meta_desc: Information on how to install the {{ cookiecutter.terraform_provider_name | capitalize }} provider.
layout: installation
---

## Installation

The Pulumi {{ cookiecutter.terraform_provider_name | capitalize }} provider is available as a package in all Pulumi languages:

* JavaScript/TypeScript: [`{{ cookiecutter.provider_javascript_package }}`](https://www.npmjs.com/package/{{ cookiecutter.provider_javascript_package }})
* Python: [`{{ cookiecutter.provider_python_package }}`](https://pypi.org/project/{{ cookiecutter.provider_python_package }}/)
* Go: [`github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/sdk/go/{{ cookiecutter.terraform_provider_name }}`](https://pkg.go.dev/github.com/{{ cookiecutter.provider_github_organization }}/{{ cookiecutter.provider }}/sdk/go/{{ cookiecutter.terraform_provider_name }})
* .NET: [`{{ cookiecutter.provider_dotnet_rootnamespace }}.{{ cookiecutter.terraform_provider_name | capitalize }}`](https://www.nuget.org/packages/{{ cookiecutter.provider_dotnet_rootnamespace }}.{{ cookiecutter.terraform_provider_name | capitalize }})


## Configuration

> Note:  
> Replace the following **sample content**, with the configuration options
> of the wrapped Terraform provider and remove this note.

The following configuration points are available for the `{{ cookiecutter.terraform_provider_name }}` provider:

- `{{ cookiecutter.terraform_provider_name }}:apiKey` (environment: `{{ cookiecutter.terraform_provider_name }}_API_KEY`) - the API key for `{{ cookiecutter.terraform_provider_name }}`
- `{{ cookiecutter.terraform_provider_name }}:region` (environment: `{{ cookiecutter.terraform_provider_name }}_REGION`) - the region in which to deploy resources

### Provider Binary

The {{ cookiecutter.terraform_provider_name | capitalize }} provider binary is a third party binary. It can be installed using the `pulumi plugin` command.

```bash
pulumi plugin install resource {{ cookiecutter.terraform_provider_name }} <version>
```

Replace the version string `<version>` with your desired version.
