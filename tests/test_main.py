import hashlib
import logging
import pathlib
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
    project_dir: Optional[str] = None
    with subtests.test(msg="Creating project"):
        md5 = hashlib.md5(replay_file.encode())
        out_dir = tmp_path_factory.mktemp(md5.hexdigest())

        _logger.debug("Creating project from template %s at %s", replay_file, out_dir)

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
