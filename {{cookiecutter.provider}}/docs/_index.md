---
title: {{ cookiecutter.terraform_provider_name | capitalize }}
meta_desc: Provides an overview of the {{ cookiecutter.terraform_provider_name | capitalize }} Provider for Pulumi.
layout: overview
---

The {{ cookiecutter.terraform_provider_name | capitalize }} provider for Pulumi can be used to provision any of the cloud resources available in {{ cookiecutter.terraform_provider_name | capitalize }}.

{% if cookiecutter.provider_category != "utility" %}
The {{ cookiecutter.terraform_provider_name | capitalize }} provider must be configured with credentials to deploy and update resources in {{ cookiecutter.terraform_provider_name | capitalize }}.
{% endif %}
