import dataclasses
import enum
import glob
import os
import subprocess
import sys
import typing

# TODO:
# - Support expecting errors
# - Support only running certain tests
# - Support choosing an interpreter

# Assumes cwd is project root.
TEST_PATH: typing.Final = "test/**/*.lox"


class Expectation(typing.NamedTuple):
    expected: str
    line_number: int


class Test(typing.NamedTuple):
    actual: str
    did_pass: bool
    expectation: Expectation


class Suite(typing.NamedTuple):
    path: str
    tests: list[Test]


@dataclasses.dataclass
class Summary:
    failed: int
    passed: int
    total: int


class Ansi_Code(enum.Enum):
    RESET = "\u001b[0m"
    REVERSED = "\u001b[7m"
    BOLD = "\u001b[1m"
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"


def format(text: str, ansi_codes: list[Ansi_Code]) -> str:
    ansi_code_str = "".join([ansi_code.value for ansi_code in ansi_codes])
    return f"{ansi_code_str}{text}{Ansi_Code.RESET.value}"


def green(text: str) -> str:
    return format(text, [Ansi_Code.GREEN])


def red(text: str) -> str:
    return format(text, [Ansi_Code.RED])


def bold(text: str) -> str:
    return format(text, [Ansi_Code.BOLD])


def green_background(text: str) -> str:
    return format(text, [Ansi_Code.GREEN, Ansi_Code.REVERSED])


def red_background(text: str) -> str:
    return format(text, [Ansi_Code.RED, Ansi_Code.REVERSED])


def should_test_line(line: str) -> bool:
    return not line.strip().startswith("//") and "expect:" in line


def run_test(actual: str, expectation: Expectation) -> Test:
    did_pass = actual == expectation.expected

    return Test(
        expectation=expectation,
        actual=actual,
        did_pass=did_pass,
    )


def parse_expectation(line: str, line_number: int) -> Expectation:
    expected = line.partition("expect:")[2].strip()
    return Expectation(expected=expected, line_number=line_number)


def run_suite(path: str) -> Suite:
    with open(path, "r") as reader:
        expectations = [
            parse_expectation(line, line_number)
            for line_number, line in enumerate(reader)
            if "expect:" in line
        ]

        # Assumes release build of clox (or at least no debug output).
        process = subprocess.run(
            ["./clox", path], capture_output=True, text=True
        )

        results = process.stdout.splitlines()

        # TODO: handle num expecations not matching num lines in stdout.

        # Compare the results to expectations.
        tests = [
            run_test(results[index], expectation)
            for index, expectation in enumerate(expectations)
        ]

        return Suite(path=path, tests=tests)


def summarize(suites: list[Suite]) -> tuple[Summary, Summary]:
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


def suite_status_text(failure_count: int) -> str:
    if failure_count:
        return red_background(" FAIL ")
    else:
        return green_background(" PASS ")


def print_results(
    suites: list[Suite], suite_summary: Summary, test_summary: Summary
) -> None:
    for suite in suites:
        failures = [test for test in suite.tests if not test.did_pass]

        print(
            f"{suite_status_text(len(failures))} {os.path.relpath(suite.path)}"
        )

        for failure in failures:
            print(
                f"  Line {failure.expectation.line_number + 1}:",
                f"expected {failure.expectation.expected},",
                f"got {failure.actual}\n",
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
