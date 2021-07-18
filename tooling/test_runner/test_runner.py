import glob
import os
import subprocess
import sys
import typing

from tooling.test_runner import expectations
from tooling.test_runner import term_style


class Test(typing.NamedTuple):
    path: str
    failures: list[expectations.Failure]


class Summary(typing.NamedTuple):
    failed_count: int
    passed_count: int
    total_count: int


def run_tests(interpreter_path: str, test_patterns: str) -> None:
    tests: list[Test] = []
    for test_pattern in test_patterns:
        for test_path in glob.iglob(test_pattern, recursive=True):
            test = _run_test(test_path, interpreter_path)
            tests.append(test)

    summary = _summarize(tests)

    _print_results(tests, summary)

    if summary.failed_count:
        sys.exit(1)


def _run_test(test_path: str, interpreter_path: str) -> Test:
    # Assumes release build of clox (or at least no debug output).
    process = subprocess.run(
        [interpreter_path, test_path], capture_output=True, text=True
    )

    failures = expectations.verify_expectations(
        process.stdout, process.stderr, process.returncode, test_path
    )

    return Test(path=test_path, failures=failures)


def _summarize(tests: list[Test]) -> Summary:
    total_count = len(tests)
    failed_count = sum([bool(test.failures) for test in tests])
    passed_count = total_count - failed_count

    return Summary(
        passed_count=passed_count,
        failed_count=failed_count,
        total_count=total_count,
    )


def _summary_text(summary: Summary) -> str:
    label_text = term_style.bold("Tests:")
    passed_text = term_style.green(f"{summary.passed_count} passed")
    failed_text = term_style.red(f"{summary.failed_count} failed")
    total_text = f"{summary.total_count} total"

    if summary.failed_count:
        return f"{label_text} {passed_text}, {failed_text}, {total_text}"
    else:
        return f"{label_text} {passed_text}, {total_text}"


def _print_results(tests: list[Test], summary: Summary) -> None:
    for test in tests:
        if test.failures:
            print(term_style.red("F"), end="")
        else:
            print(term_style.green("."), end="")

    failed_tests = [test for test in tests if test.failures]

    if failed_tests:
        print()
        print()
        print(term_style.bold("Failures:"))
        print()

        for index, failed_test in enumerate(failed_tests):
            print(
                f"{index + 1}) "
                f"{term_style.red(os.path.relpath(failed_test.path))}"
            )

            for failure in failed_test.failures:
                print(f"  {failure.message}")
                print()

    print()
    print(_summary_text(summary))
