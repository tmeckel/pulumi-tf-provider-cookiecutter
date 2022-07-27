{%- macro sentence_case(text) -%}
    {{ text[0]|upper }}{{ text[1:] }}
{%- endmacro -%}

# {{ sentence_case(cookiecutter.provider_name) }} Resource Provider

The {{ sentence_case(cookiecutter.provider_name) }} Resource Provider lets you manage [{{ cookiecutter.provider_name }}](http://example.com) resources.

## Installing

This package is available for several languages/platforms:

### Node.js (JavaScript/TypeScript)

To use from JavaScript or TypeScript in Node.js, install using either `npm`:

```bash
npm install {{ cookiecutter.javascript_package }}
```

or `yarn`:

```bash
yarn add {{ cookiecutter.javascript_package }}
```

### Python

To use from Python, install using `pip`:

```bash
pip install {{ cookiecutter.python_package }}
```

### Go

To use from Go, use `go get` to grab the latest version of the library:

```bash
go get github.com/{{ cookiecutter.github_organization }}/pulumi-{{ cookiecutter.provider_name }}/sdk/go/...
```

### .NET

To use from .NET, install using `dotnet add package`:

```bash
dotnet add package {{ cookiecutter.dotnet_rootnamespace }}.{{ cookiecutter.provider_name }}
```

## Configuration

The following configuration points are available for the `{{ cookiecutter.provider_name }}` provider:

- `{{ cookiecutter.provider_name }}:apiKey` (environment: `{{ cookiecutter.provider_name }}_API_KEY`) - the API key for `{{ cookiecutter.provider_name }}`
- `{{ cookiecutter.provider_name }}:region` (environment: `{{ cookiecutter.provider_name }}_REGION`) - the region in which to deploy resources

## Reference

For detailed reference documentation, please visit [the Pulumi registry](https://www.pulumi.com/registry/packages/{{ cookiecutter.provider_name }}/api-docs/).
