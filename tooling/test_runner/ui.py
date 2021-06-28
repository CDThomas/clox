import os

from tooling.test_runner import test_runner
from tooling.test_runner import terminal


def summary_line(summary: test_runner.Summary) -> str:
    label_text = terminal.bold("Tests:")
    passed_text = terminal.green(f"{summary.passed_count} passed")
    failed_text = terminal.red(f"{summary.failed_count} failed")
    total_text = f"{summary.total_count} total"

    if summary.failed_count:
        return f"{label_text} {passed_text}, {failed_text}, {total_text}"
    else:
        return f"{label_text} {passed_text}, {total_text}"


def test_status_text(test: test_runner.Test) -> str:
    if test.failures:
        return terminal.red_background(" FAIL ")
    else:
        return terminal.green_background(" PASS ")


def print_results(
    tests: list[test_runner.Test], summary: test_runner.Summary
) -> None:
    for test in tests:
        print(f"{test_status_text(test)} {os.path.relpath(test.path)}")

        for failure in test.failures:
            print(f"  {failure.message}\n")

    print()
    print(summary_line(summary))
