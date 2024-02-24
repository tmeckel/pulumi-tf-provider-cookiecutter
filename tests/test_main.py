import hashlib
import logging
import subprocess
from subprocess import Popen
from typing import List

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
    replay_file: str,
    patches: List[str],
):
    md5 = hashlib.md5(replay_file.encode())
    out_dir = tmp_path_factory.mktemp(md5.hexdigest())

    _logger.info("Creating project from template %s at %s", replay_file, out_dir)

    project_dir = cookiecutter(
        template=".",
        replay=replay_file,
        output_dir=out_dir,
    )

    for patch in patches or []:
        with open(patch) as f:
            _logger.info("Apply patch %s to project in %s", patch, project_dir)
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

    _logger.info("Compiling project in %s", project_dir)

    make = Popen(
        args=["make", "provider"],
        cwd=project_dir,
        stderr=subprocess.PIPE,
    )
    make.wait()
    if make.returncode != 0:
        pytest.fail(make.stderr.read().decode())
