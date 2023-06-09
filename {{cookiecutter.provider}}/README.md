# {{ cookiecutter.terraform_provider_name | capitalize }} Resource Provider

The {{ cookiecutter.terraform_provider_name | capitalize }} Resource Provider lets you manage [{{ cookiecutter.terraform_provider_name }}](https://www.pulumi.com/registry/packages/{{ cookiecutter.terraform_provider_name }}/) resources.

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
dotnet add package {{ cookiecutter.provider_dotnet_rootnamespace }}.{{ cookiecutter.terraform_provider_name | capitalize }}
```

## Reference

For detailed reference documentation, please visit [the Pulumi registry](https://www.pulumi.com/registry/packages/{{ cookiecutter.terraform_provider_name }}/api-docs/).
