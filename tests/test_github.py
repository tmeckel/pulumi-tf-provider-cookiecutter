import logging

_logger = logging.getLogger()

from local_extensions import (  # noqa: E402
    github_download_file,
    github_get_latest_semver_tag,
    parse_go_mod,
)


def test_download_lastest_terraform_bridge_go_mod():
    go_mod = github_download_file(
        repo="pulumi-terraform-bridge",
        file_path="go.mod",
    )
    assert go_mod


def test_parse_go_mod():
    go_mod = github_download_file(
        repo="pulumi-terraform-bridge",
        file_path="go.mod",
    )
    requirements, replacements = parse_go_mod(contents=go_mod)
    assert requirements

    # __pulumi_sdk_version
    assert requirements["github.com/pulumi/pulumi/sdk/v3"]
    # __pulumi_terraform_plugin_sdkv2_version
    assert replacements["github.com/hashicorp/terraform-plugin-sdk/v2"][1]


def test_get_latest_terraform_bridge_version():
    result = github_get_latest_semver_tag(
        repo="pulumi-terraform-bridge",
        prefix="v",
    )
    assert result

    tag, version = result

    assert tag
    assert version


def test_get_latest_terraform_bridge_pf_version():
    result = github_get_latest_semver_tag(
        repo="pulumi-terraform-bridge",
        prefix="pf/v",
    )
    assert result

    tag, version = result

    assert tag
    assert version
