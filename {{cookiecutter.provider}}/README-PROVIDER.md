{%- macro sentence_case(text) -%}
    {{ text[0]|upper }}{{ text[1:] }}
{%- endmacro -%}

# {{ sentence_case(cookiecutter.terraform_provider_name) }} Resource Provider

The {{ sentence_case(cookiecutter.terraform_provider_name) }} Resource Provider lets you manage [{{ cookiecutter.terraform_provider_name }}](https://registry.terraform.io/providers/{{ cookiecutter.terraform_provider_org }}/{{ cookiecutter.terraform_provider_name }}) resources.

## Installing

This package is available for several languages/platforms:

### Node.js (JavaScript/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

```bash
npm install {{ cookiecutter.provider_javascript_package }}
```

or `yarn`:

```bash
yarn add {{ cookiecutter.provider_javascript_package }}
```

### Python

To use from Python, install using `pip`:

```bash
pip install {{ cookiecutter.provider_python_package }}
```

### Go

To use from Go, use `go get` to grab the latest version of the library:

```bash
go get github.com/{{ cookiecutter.provider_github_organization }}/pulumi-{{ cookiecutter.terraform_provider_name }}/sdk/go/...
```

### .NET

To use from .NET, install using `dotnet add package`:

```bash
dotnet add package {{ cookiecutter.provider_dotnet_rootnamespace }}.{{ cookiecutter.terraform_provider_name }}
```

## Configuration

The following configuration points are available for the `{{ cookiecutter.terraform_provider_name }}` provider:

- `{{ cookiecutter.terraform_provider_name }}:apiKey` (environment: `{{ cookiecutter.terraform_provider_name }}_API_KEY`) - the API key for `{{ cookiecutter.terraform_provider_name }}`
- `{{ cookiecutter.terraform_provider_name }}:region` (environment: `{{ cookiecutter.terraform_provider_name }}_REGION`) - the region in which to deploy resources

## Reference

For detailed reference documentation, please visit [the Pulumi registry](https://www.pulumi.com/registry/packages/{{ cookiecutter.terraform_provider_name }}/api-docs/).
