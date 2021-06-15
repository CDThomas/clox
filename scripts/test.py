import dataclasses
import glob
import os
import subprocess
import sys
import typing

# TODO:
# - Handle print statements rather than interpreting each line
# - Support expecting errors
# - Support only running certain tests
# - Support choosing an interpreter

# Constants
TEST_PATH = "test/**/*.lox"
RESET = "\u001b[0m"
REVERSED = "\u001b[7m"
BOLD = "\u001b[1m"
RED = "\u001b[31;1m"
GREEN = "\u001b[32;1m"

# Data structures


class Test(typing.NamedTuple):
    actual: str
    did_pass: bool
    expected: str
    line_number: int


class Suite(typing.NamedTuple):
    path: str
    tests: list[Test]


@dataclasses.dataclass
class Summary:
    failed: int
    passed: int
    total: int


def color(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def green(text: str) -> str:
    return color(text, GREEN)


def red(text: str) -> str:
    return color(text, RED)


def bold(text: str) -> str:
    return color(text, BOLD)


def green_background(text: str) -> str:
    return color(text, GREEN + REVERSED)


def red_background(text: str) -> str:
    return color(text, RED + REVERSED)


def pluralize(word: str, count: int) -> str:
    if count == 1:
        return word
    else:
        return word + "s"


def should_test_line(line: str) -> bool:
    return not line.strip().startswith("//") and "expect:" in line


def run_test(line: str, line_number: int) -> Test:
    # Remove print statements until these are supported by the interpreter
    line = line.replace("print", "")

    # Remove semis until these are supported by the interpreter
    line = line.replace(";", "")

    expected = line.partition("expect:")[2].strip()

    # Interpret each line individually until printing (writing to stdout) is
    # supported in interpreter. Later, this can passs the filename to `subprocess.run`
    # and compare the parsed expecations to stdout.
    result = subprocess.run(["./clox"], capture_output=True, text=True, input=line)
    actual = result.stdout.split("\n")[-3]

    did_pass = actual == expected

    return Test(
        expected=expected, actual=actual, line_number=line_number, did_pass=did_pass
    )


def run_suite(path: str) -> Suite:
    with open(path, "r") as reader:
        tests = [
            run_test(line, line_number)
            for line_number, line in enumerate(reader)
            if should_test_line(line)
        ]

        return Suite(path=path, tests=tests)


def summarize(suites: list[Suite]) -> tuple[Suite, Suite]:
    suite_summary = Summary(passed=0, failed=0, total=0)
    test_summary = Summary(passed=0, failed=0, total=0)

    for suite in suites:
        results = [test.did_pass for test in suite.tests]

        suite_tests_count = len(results)
        suite_passed_tests_count = results.count(True)

        if suite_tests_count == suite_passed_tests_count:
            suite_summary.passed += 1

        test_summary.total += suite_tests_count
        test_summary.passed += suite_passed_tests_count

    suite_summary.total = len(suites)
    suite_summary.failed = suite_summary.total - suite_summary.passed
    test_summary.failed = test_summary.total - test_summary.passed

    return suite_summary, test_summary


def summary_line(summary: Summary, label: str) -> str:
    label_text = bold(f"{label}:")
    passed_text = green(f"{summary.passed} passed")
    failed_text = red(f"{summary.failed} failed")
    total_text = f"{summary.total} total"

    if summary.failed:
        return f"{label_text} {passed_text}, {failed_text}, {total_text}"
    else:
        return f"{label_text} {passed_text}, {total_text}"


def print_results(
    suites: list[Suite], suite_summary: Summary, test_summary: Summary
) -> None:
    for suite in suites:
        failures = [test for test in suite.tests if not test.did_pass]
        prefix = red_background(" FAIL ") if failures else green_background(" PASS ")

        print(f"{prefix} {os.path.relpath(suite.path)}")

        for failure in failures:
            print(
                f"  Line {failure.line_number + 1}: expected {failure.expected}, got {failure.actual}\n"
            )

    print()
    print(summary_line(suite_summary, "Test Suites"))
    print(summary_line(test_summary, "Tests"))


def run_suites() -> None:
    suites = [run_suite(path) for path in glob.iglob(TEST_PATH)]
    suite_summary, test_summary = summarize(suites)

    print_results(suites, suite_summary, test_summary)

    if suite_summary.failed:
        sys.exit(1)


run_suites()
