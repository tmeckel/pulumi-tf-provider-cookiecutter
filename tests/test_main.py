import hashlib
import logging
import pathlib
import random
import string
import subprocess
from subprocess import Popen
from typing import List, Optional

import pytest
from cookiecutter.main import cookiecutter

_logger = logging.getLogger()


@pytest.mark.parametrize(
    argnames="replay_file, patches",
    argvalues=[
        (
            "tests/replays/configcat/v1/pulumi-tf-provider-cookiecutter-configcat.json",
            None,
        ),
        (
            "tests/replays/configcat/v4/pulumi-tf-provider-cookiecutter-configcat-v4.json",
            [
                "tests/replays/configcat/v4/shim.go.patch",
            ],
        ),
        (
            "tests/replays/zscaler/zpa/pulumi-tf-provider-cookiecutter-zscaler-zpa.json",
            [
                "tests/replays/zscaler/zpa/resources.go.patch",
            ],
        ),
        (
            "tests/replays/ncloud/v2/pulumi-tf-provider-cookiecutter.json",
            None,
        ),
        (
            "tests/replays/ncloud/commit/pulumi-tf-provider-cookiecutter.json",
            None,
        ),
    ],
    ids=[
        "configcat",
        "configcat-v4",
        "zscaler-zpa",
        "ncloud-v2",
        "ncloud-using-commit",
    ],
)
def test_replay_configuration(
    tmp_path_factory,
    subtests,
    replay_file: str,
    patches: List[str],
):
    with subtests.test(msg="Create project"):
        project_dir: Optional[str] = None
        with subtests.test(msg="Creating project"):
            md5 = hashlib.md5(replay_file.encode())
            out_dir = tmp_path_factory.mktemp(md5.hexdigest())

            _logger.debug(
                "Creating project from template %s at %s", replay_file, out_dir
            )

            project_dir = cookiecutter(
                template=".",
                replay=replay_file,
                output_dir=out_dir,
            )

        assert project_dir

    with subtests.test(msg="Compiling project"):
        _logger.debug("Compiling project in %s", project_dir)

        for patch in patches or []:
            with open(patch) as f:
                _logger.debug("Apply patch %s to project in %s", patch, project_dir)

                git = Popen(
                    args=[
                        "git",
                        "apply",
                        "--ignore-space-change",
                        "--ignore-whitespace",
                    ],
                    cwd=project_dir,
                    stdin=f,
                    stderr=subprocess.PIPE,
                )
                git.wait()
                if git.returncode != 0:
                    pytest.fail(git.stderr.read().decode())

        make = Popen(
            args=["make", "provider"],
            cwd=project_dir,
            stderr=subprocess.PIPE,
        )
        make.wait()
        if make.returncode != 0:
            pytest.fail(make.stderr.read().decode())

    with subtests.test(msg="Validate GitHub workflows"):
        workflows = pathlib.Path(project_dir) / ".github" / "workflows"

        for file in workflows.glob("*.yml"):
            _logger.debug("Validate GitHub workflow at %s", file)

            action_validator = Popen(
                args=[
                    "action-validator",
                    file,
                ],
                cwd=project_dir,
                stderr=subprocess.PIPE,
            )
            action_validator.wait()
            if action_validator.returncode != 0:
                pytest.fail(action_validator.stderr.read().decode())


def test_create_project_dynamic(
    tmp_path_factory,
    subtests,
):
    out_dir = tmp_path_factory.mktemp("".join(random.sample(string.ascii_lowercase, 8)))
    _logger.debug("Creating configcat provider in directory %s", out_dir)

    with subtests.test(msg="Create project"):
        project_dir = cookiecutter(
            template=".",
            output_dir=out_dir,
            no_input=True,
            extra_context={
                "terraform_provider_name": "configcat",
                "terraform_provider_org": "configcat",
                "terraform_provider_source": "github.com/configcat/terraform-provider-configcat",
                "terraform_provider_version_or_commit": "4.0.0",
                "terraform_provider_module": "github.com/configcat/terraform-provider-configcat",
                "terraform_provider_package_name": "internal/configcat",
                "terraform_sdk_version": "plugin-framework",
                "provider": "pulumi-configcat",
                "provider_display_name": "Configcat",
                "provider_github_organization": "pulumiverse",
                "provider_publisher": "pulumiverse",
                "provider_homepage": "https://github.com/pulumiverse/pulumi-configcat",
                "provider_logoUrl": "https://raw.githubusercontent.com/pulumiverse/pulumi-configcat/main/docs/configcat.png",
                "provider_description": "A Pulumi package for creating and managing Configcat resources",
                "provider_category": "cloud",
                "provider_download_url": "github://api.github.com/pulumiverse/pulumi-configcat",
                "provider_javascript_package": "@pulumiverse/configcat",
                "provider_dotnet_rootnamespace": "Pulumiverse",
                "provider_python_package": "pulumiverse_configcat",
                "provider_java_base_package": "com.pulumiverse",
                "provider_mapping_strategy": "automatic",
                "provider_naming_strategy": "singlelevel",
                "go_version": "1.21.7",
                "create_github_workflows": "yes",
                "skip_go_mod_tidy": "no",
                "skip_git_init": "no",
            },
        )

        assert project_dir

    for patch in ["tests/replays/configcat/v4/shim.go.patch"]:
        with open(patch) as f:
            _logger.debug("Apply patch %s to project in %s", patch, project_dir)

            git = Popen(
                args=[
                    "git",
                    "apply",
                    "--ignore-space-change",
                    "--ignore-whitespace",
                ],
                cwd=project_dir,
                stdin=f,
                stderr=subprocess.PIPE,
            )
            git.wait()
            if git.returncode != 0:
                pytest.fail(git.stderr.read().decode())

    with subtests.test(msg="Compile provider"):
        make = Popen(
            args=["make", "provider"],
            cwd=project_dir,
            stderr=subprocess.PIPE,
        )
        make.wait()
        if make.returncode != 0:
            pytest.fail(make.stderr.read().decode())

    with subtests.test(msg="Validate GitHub workflows"):
        workflows = pathlib.Path(project_dir) / ".github" / "workflows"

        for file in workflows.glob("*.yml"):
            _logger.debug("Validate GitHub workflow at %s", file)

            action_validator = Popen(
                args=[
                    "action-validator",
                    file,
                ],
                cwd=project_dir,
                stderr=subprocess.PIPE,
            )
            action_validator.wait()
            if action_validator.returncode != 0:
                pytest.fail(action_validator.stderr.read().decode())
