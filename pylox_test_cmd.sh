#!/usr/bin/env bash

# This script is the same as ./pylox, but it invokes Python directly instead of
# using Poetry. This is used for running the full test suite for Pylox because
# starting Poetry for each test is slow. This command assumes that the virtualenv
# has already been activated.

set -euo pipefail

project_root=$(dirname "$0")

cd ${project_root}
python -m lox.cli $@
