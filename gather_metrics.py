#!/usr/bin/env python3
# pipeline-helpers
# Copyright(C) 2021 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This script run in a pipeline task to execute test and gather metrics for a AI model deployed."""

import os
import logging
import json
import subprocess

from thoth.pipeline_helpers import __version__ as __service_version__


_LOGGER = logging.getLogger("thoth.gather_metrics")
_LOGGER.info("Thoth pipeline-helpers task: gather_metrics v%s", __service_version__)

# We use a file for stdout and stderr not to block on pipe.
_EXEC_STDOUT_FILE = os.getenv("PIPELINE_STDOUT_PATH", "script.stdout")
_EXEC_STDERR_FILE = os.getenv("PIPELINE_STDERR_PATH", "script.stderr")

_EXEC_DIR = os.getenv("PIPELINE_EXEC_DIR", ".")
_TEST_PATH = os.getenv("MODEL_TEST_PATH", "src/test.py")
_EXEC_FILE = os.getenv("PIPELINE_EXEC_FILE", os.path.join(_EXEC_DIR, _TEST_PATH))


def gather_metrics() -> None:
    """Gather metrics running a test script created by data scientist."""
    # Execute the supplied script.
    args = ["pipenv", "run", "python3", _EXEC_FILE]
    _LOGGER.info(f"Args to be used in process: {args}")

    with open(os.path.join(_EXEC_DIR, _EXEC_STDOUT_FILE), "w") as stdout_file, open(
        os.path.join(_EXEC_DIR, _EXEC_STDERR_FILE), "w"
    ) as stderr_file:
        process = subprocess.Popen(args, stdout=stdout_file, stderr=stderr_file, universal_newlines=True)

    process.communicate()

    return_code = process.returncode
    if return_code != 0:
        with open(_EXEC_STDERR_FILE, "r") as stderr_file:
            stderr = stderr_file.read()
            _LOGGER.error(f"Error running script in pipeline-helpers: {stderr}")
            return

    # Load stdout.
    with open(_EXEC_STDOUT_FILE, "r") as stdout_file:
        stdout = stdout_file.read()
        try:
            stdout = json.loads(str(stdout))
        except Exception:
            # We were not able to load JSON, pass string as output.
            pass
        _LOGGER.info(f"Metrics collected are {stdout}")


if __name__ == "__main__":
    gather_metrics()
