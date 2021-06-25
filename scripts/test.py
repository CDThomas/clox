import dataclasses
import enum
import glob
import os
import re
import subprocess
import sys
import typing

# TODO:
# - Support expecting errors
#    - Compilation errors: https://github.com/munificent/craftinginterpreters/blob/master/test/assignment/grouping.lox
#      - Line number is optional https://github.com/munificent/craftinginterpreters/blob/3e5f0fa6636b68eddfe4dc0173af95130403f961/test/unexpected_character.lox
#    - Runtime errors: https://github.com/munificent/craftinginterpreters/blob/master/test/assignment/undefined.lox
#    - can have both runtime error expectations and normal expectations (https://github.com/munificent/craftinginterpreters/blob/3e5f0fa6636b68eddfe4dc0173af95130403f961/test/super/extra_arguments.lox)
#    - can only have one compilation error expectation
# - Support only running certain tests
# - Support choosing an interpreter

# Assumes cwd is project root.
TEST_PATH: typing.Final = "test/**/*.lox"

EXPECTED_OUTPUT_REGEX: typing.Final = r"// expect: ?(.*)"
EXPECTED_COMPILE_ERROR_REGEX: typing.Final = r"// (Error.*)"
EXPECTED_RUNTIME_ERROR_REGEX: typing.Final = r"// expect runtime error: (.+)"


class OutputExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class Test(typing.NamedTuple):
    actual: str
    did_pass: bool
    expectation: OutputExpectation
    failure_message: typing.Optional[str]


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


def run_test(actual: str, expectation: OutputExpectation) -> Test:
    did_pass = actual == expectation.expected

    return Test(
        expectation=expectation,
        actual=actual,
        did_pass=did_pass,
        failure_message=None,
    )


def parse_expectation(
    line: str, line_number: int
) -> typing.Optional[OutputExpectation]:
    if match := re.search(EXPECTED_OUTPUT_REGEX, line):
        expected = match.group(1)
        return OutputExpectation(expected=expected, line_number=line_number)
    else:
        return None


def run_output_tests(
    stdout: str, output_expectations: list[OutputExpectation]
) -> list[Test]:
    # TODO: handle num expecations not matching num lines in stdout.
    output_lines = stdout.splitlines()

    # Compare the results to expectations.
    return [
        run_test(output_lines[index], expectation)
        for index, expectation in enumerate(output_expectations)
    ]


def run_tests(
    stdout: str, stderr: str, expectations: list[OutputExpectation]
) -> list[Test]:
    output_expectations: list[OutputExpectation] = []

    for expectation in expectations:
        if type(expectation) is OutputExpectation:
            output_expectations.append(expectation)

    output_tests = run_output_tests(stdout, output_expectations)

    return output_tests


def run_suite(path: str) -> Suite:
    with open(path, "r") as reader:
        expectations = [
            expectation
            for line_number, line in enumerate(reader)
            if (expectation := parse_expectation(line, line_number))
        ]

        # Assumes release build of clox (or at least no debug output).
        process = subprocess.run(
            ["./clox", path], capture_output=True, text=True
        )

        tests = run_tests(process.stdout, process.stderr, expectations)

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
    suites = [
        run_suite(path) for path in glob.iglob(TEST_PATH, recursive=True)
    ]
    suite_summary, test_summary = summarize(suites)

    print_results(suites, suite_summary, test_summary)

    if suite_summary.failed:
        sys.exit(1)


run_suites()
