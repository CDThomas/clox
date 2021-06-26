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
EXPECTED_SYNTAX_ERROR_REGEX: typing.Final = r"// (Error.*)"
EXPECTED_RUNTIME_ERROR_REGEX: typing.Final = r"// expect runtime error: (.+)"


# Expectation kinds: output, compile error, runtime error
class OutputExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class Failure(typing.NamedTuple):
    message: str


class Test(typing.NamedTuple):
    path: str
    failures: list[Failure]


class Summary(typing.NamedTuple):
    failed_count: int
    passed_count: int
    total_count: int


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


def run_expectation(
    actual: str, expectation: OutputExpectation
) -> typing.Optional[Failure]:
    did_pass = actual == expectation.expected

    if did_pass:
        return None
    else:
        message = (
            f"  Line {expectation.line_number + 1}: "
            f"expected {expectation.expected}, got {actual}\n"
        )

        return Failure(message=message)


def parse_expectation(
    line: str, line_number: int
) -> typing.Optional[OutputExpectation]:
    if match := re.search(EXPECTED_OUTPUT_REGEX, line):
        expected = match.group(1)
        return OutputExpectation(expected=expected, line_number=line_number)
    else:
        return None


def run_output_expectations(
    stdout: str, output_expectations: list[OutputExpectation]
) -> list[Failure]:
    # TODO: handle num expecations not matching num lines in stdout.
    output_lines = stdout.splitlines()

    return [
        failure
        for index, expectation in enumerate(output_expectations)
        if (failure := run_expectation(output_lines[index], expectation))
    ]


def run_expectations(
    stdout: str, stderr: str, expectations: list[OutputExpectation]
) -> list[Failure]:
    output_expectations: list[OutputExpectation] = []

    for expectation in expectations:
        if type(expectation) is OutputExpectation:
            output_expectations.append(expectation)

    failures = run_output_expectations(stdout, output_expectations)

    return failures


def run_test(path: str) -> Test:
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

        failures = run_expectations(
            process.stdout, process.stderr, expectations
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


def summary_line(summary: Summary) -> str:
    label_text = bold("Tests:")
    passed_text = green(f"{summary.passed_count} passed")
    failed_text = red(f"{summary.failed_count} failed")
    total_text = f"{summary.total_count} total"

    if summary.failed_count:
        return f"{label_text} {passed_text}, {failed_text}, {total_text}"
    else:
        return f"{label_text} {passed_text}, {total_text}"


def test_status_text(test: Test) -> str:
    if test.failures:
        return red_background(" FAIL ")
    else:
        return green_background(" PASS ")


def print_results(tests: list[Test], summary: Summary) -> None:
    for test in tests:
        print(f"{test_status_text(test)} {os.path.relpath(test.path)}")

        for failure in test.failures:
            print(failure.message)

    print()
    print(summary_line(summary))


def run_tests() -> None:
    tests = [run_test(path) for path in glob.iglob(TEST_PATH, recursive=True)]
    summary = summarize(tests)

    print_results(tests, summary)

    if summary.failed_count:
        sys.exit(1)


run_tests()
