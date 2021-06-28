import glob
import subprocess
import sys
import typing

from tooling.test_runner import expectations
from tooling.test_runner import ui

# TODO:
# - Support only running certain tests
# - Support choosing an interpreter
# - Add flag for condensed/verbose output

# Assumes cwd is project root.
TEST_PATH: typing.Final = "test/**/*.lox"


class Test(typing.NamedTuple):
    path: str
    failures: list[expectations.Failure]


class Summary(typing.NamedTuple):
    failed_count: int
    passed_count: int
    total_count: int


def run_test(path: str) -> Test:
    # Assumes release build of clox (or at least no debug output).
    process = subprocess.run(["./clox", path], capture_output=True, text=True)

    failures = expectations.verify_expectations(
        process.stdout, process.stderr, process.returncode, path
    )

    return Test(path=path, failures=failures)


def summarize(tests: list[Test]) -> Summary:
    total_count = len(tests)
    failed_count = sum([bool(test.failures) for test in tests])
    passed_count = total_count - failed_count

    return Summary(
        passed_count=passed_count,
        failed_count=failed_count,
        total_count=total_count,
    )


def run_tests() -> None:
    tests = [run_test(path) for path in glob.iglob(TEST_PATH, recursive=True)]
    summary = summarize(tests)

    ui.print_results(tests, summary)

    if summary.failed_count:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
