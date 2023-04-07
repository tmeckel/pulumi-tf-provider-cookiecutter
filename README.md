# Cookiecutter Terraform Bridge Provider Template

This repository contains a
[Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html)
template to create a new Pulumi provider which wraps an existing Terraform
provider.

## Background

This repository is part of the [guide for authoring and publishing a Pulumi Package](https://www.pulumi.com/docs/guides/pulumi-packages/how-to-author).

Learn about the concepts behind [Pulumi Packages](https://www.pulumi.com/docs/guides/pulumi-packages/#pulumi-packages).

## Creating a Pulumi Terraform Bridge Provider

### Prerequisites

* Python version `>= 3.7`

* Cookiecutter version `>= 2.1`

  To create a new Pulumi provider using this template, Cookiecutter must be
  available with a version >= 2.1 because the template utilizes [`local extensions`](https://cookiecutter.readthedocs.io/en/stable/advanced/local_extensions.html)
  which was a new feature in version 2.1.

  You can follow the installation instructions in the [Cookiecutter
  documentation](https://cookiecutter.readthedocs.io/en/stable/installation.html#)
  or you can use a [Python virtual
  environment](https://docs.python.org/3/tutorial/venv.html) to install
  Cookiecutter.

  A virtual environment has the advantage that Cookiecutter will be installed in
  that environment and will not clutter up your local machine with software that
  you might use only once. After done with creating the Pulumi provider the
  virtual environment can safely removed from the local disk.

  Steps to install Cookiecutter in a virtual environment:

  > **Note**: the following steps assume a Unix like operating system. To create
  > a virtual environment on Windows refer to an appropriate documentation. 

  1. `python3 -m venv vcoockiecutter`
  1. `source vcoockiecutter/bin/activate`
  1. `python -m pip install -U pip`
  1. `python -m pip install cookiecutter`

### Creating a new provider

To create a new provider start Cookiecutter with a reference to this GitHub
repository:

```shell
cookiecutter -f gh:tmeckel/pulumi-tf-provider-cookiecutter
```

Cookiecutter will then create a new (sub-)directory at the current location
using the naming scheme: `pulumi-<provider-name>`.

For additional command line options refer to the chapter [Command Line
Options](https://cookiecutter.readthedocs.io/en/stable/cli_options.html) in the
Cookiecutter documentation.

> **Note:** The template only supports Terraform Providers which source code is hosted on GitHub

During execution Cookiecutter will prompt for the following input parameters.
Except for `terraform_provider_name` and `terraform_provider_org` the template
will propose meaningful values for input parameters derived from the context of
conceived input parameters so far. You can accept the proposed value by hitting
`RETURN`.

> **Note:** All input parameters are `required`. If not stated otherwise.

| Parameter                              | Description                                                                                                                                                                                                                                                             |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `terraform_provider_name`              | The name of the Terraform provider to wrap. Only use the suffix after `terraform-provider` <br> **Example**: `terraform-provider-time` `->` Input: `time`                                                                                                               |
| `terraform_provider_org`               | The GitHub organization which hosts the Terraform provider. <br> **Example**: GitHub Url: `https://github.com/hashicorp/terraform-provider-time` `->` Input: `hashicorp`                                                                                                |
| `terraform_provider_source`            | The GitHub Url of the Terraform Provider. Usually, there is no reason not to accept the proposed value.                                                                                                                                                                 |
| `terraform_provider_version_or_commit` | The Version of the Terraform provider to initially wrap as a Pulumi provider. <br> Refer to chapter [terraform_provider_version_or_commit](#terraformproviderversionorcommit) for a detailed explanation and hints how to decide what type of version reference to use. |
| `terraform_provider_module`            | The value of the first line in the top level `go.mod` file from source code of the Terraform provider. <br> **Ensure to change the proposed value if the value do not match with the one from the top level `go.mod` file from the Terraform provider repository.**     |
| `terraform_provider_package_name`      | The Go package path to the `provider.go` file, or to the `.go` file which contains the `func Provider() *schema.Provider` function.                                                                                                                                     |
| `terraform_sdk_version`                | The Terraform SDK version that is in use by the Terraform provider. <br><br>Possible values:<br> - `1` : Terraform SDK Version 1<br> - `2` : Terraform SDK Version 2<br> - `plugin-framework`: Terraform Plugin Framework                                               |
| `provider`                             | The name of the Pulumi provider. <br> It's recommended to keep the proposed value, because it adheres to the Pulumi provider naming scheme.                                                                                                                             |
| `provider_display_name`                | The friendly name of the Pulumi Provider. <br> The display name will be shown as title in the Pulumi for the provider. So it's advisable to keep it short and concise.                                                                                                  |
| `provider_github_organization`         | The GitHub organization to host the Pulumi provider.                                                                                                                                                                                                                    |
| `provider_publisher`                   | The personal/company name, that shall to be shown on Pulumi Registry                                                                                                                                                                                                    |
| `provider_homepage`                    | A web-accessible URL to homepage of the provider.                                                                                                                                                                                                                       |
| `provider_logoUrl`                     | A web-accessible URL to a logo for your package (ideally an SVG)                                                                                                                                                                                                        |
| `provider_description`                 | A concise description of the provider.                                                                                                                                                                                                                                  |
| `provider_category`                    | The category of the provider. <br> Categories ease searching insider the Pulumi registry. <br> Cookiecutter prompts the permitted categories of Pulumi Registry.                                                                                                        |
| `provider_download_url`                | A web-accessible URL that contains the compiled binary plugin associated with the provider                                                                                                                                                                              |
| `provider_javascript_package`          | The name of the Javascript package which will be published to NPMJS                                                                                                                                                                                                     |
| `provider_dotnet_rootnamespace`        | The root namespace of the Dotnet assembly. The complete Namespace will be generated as `<provider_dotnet_rootnamespace>.<provider>`                                                                                                                                     |
| `provider_python_package`              | The name of the Python package published to [pypi.org](https://pypi.org/)                                                                                                                                                                                               |
| `provider_java_base_package`           | The base package name (path) for the  Java SDK                                                                                                                                                                                                                          |
| `create_github_workflows`              | Per default the template will create preconfigured GitHub actions which automatically creates releases for a new provider version. <br> Answer with `no` to disable the create of those actions.                                                                        |
| `skip_go_mod_tidy`                     | Per default the template will execute `go mod tidy` on the new Pulumi Provider package to verify that the Terraform provider can be included as module and to create the required `go.sum` file. <br>  Answer with `no` to suppress the execution of `go mod tidy`      |
| `skip_git_init`                        | Skip the initialization of a Git repository for the new provider. This is **not recommended** because the build process requires a Git repository to derive the semver version tag for the current build. <br>  Answer with `no` to skip the execution of `git init` |

> **Note:** Input parameters starting with `pulumi` reflect the attributes of the [Pulumi package metadata](https://www.pulumi.com/docs/guides/pulumi-packages/schema/#package)

After the Cookiecutter template has created the new directory for the Pulumi
provider, you can change to this directory and use the `make tfgen` command to
check whether the Terraform provider has been referenced correctly.

For guidance how to further develop the newly created Pulumi provider refer to
`README-DEVELOPMENT.md` in the provider directory.

## Parameter details

### `terraform_provider_version_or_commit`

The parameter specifies the initial version of the Terraform provider that
should be wrapped as a Pulumi Provider. You can specify a Semver compatible
version or a Git commit.

Aside the `terraform_provider_source` and the `terraform_provider_module` the
version is a vital part of a module reference in Go. A thorough explanation of
how Go manages dependencies is available at
[`go.dev`](https://go.dev/doc/modules/managing-dependencies).

The following will list a couple of hints when to select a specific version
number or when to use a commit reference as a value for
`terraform_provider_version_or_commit`

- If the Terraform provider repository contains a release `< 2.0.0` use the release version.

- If the Terraform provider repository contains a release `>= 2.0.0` and the
  module name in  top level `go.mod` file ends with the correct version suffix
  that matches the major version of the provider release, use the version
  number.

  **Example:**

  - Repository release `3.5.1`
  - module name in `go.mod`: `github.com/bar/terraform-provider-foo/v3`

- If the Terraform provider repository contains a release `>= 2.0.0` and the
  module name in  top level `go.mod` **does not** end with the correct version
  suffix, use the commit hash of the release version.

- You can always select a commit hash, and the Cookiecutter template will
  automatically create a valid [pseudo-version](https://go.dev/ref/mod#pseudo-versions) and add it to the Pulumi provider
  `go.mod` file.

> **Note**: If values of `terraform_provider_source`,
> `terraform_provider_module` and or the referenced version occur, the
> Cookiecutter template will do it's best to create correct `replace` statements
> in the `go.mod` file of the Pulumi provider, to reference the Terraform
> Provider as a valid Go module.

### `terraform_provider_package_name`

The parameter specifies the package path to the `func Provider()` implementation
which returns the schema of the Terraform Provider. The Cookiecutter template is
smart enough to create a SHIM if the provider implementation is hidden inside an
`internal` package, because `internal/` is a special directory name recognized
by the go tool which will prevent one package from being imported by another
unless both share a common ancestor. Packages within an `internal/` directory
are therefore said to be internal packages.
