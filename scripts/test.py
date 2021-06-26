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
EXPECTED_SYNTAX_ERROR_REGEX: typing.Final = (
    r"// (?:\[line (?P<line_number>\d+)\] )?(?P<error>Error.+)"
)
EXPECTED_RUNTIME_ERROR_REGEX: typing.Final = r"// expect runtime error: (.+)"


class OutputExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class SyntaxErrorExpectation(typing.NamedTuple):
    expected: str
    line_number: int


Expectation = typing.Union[OutputExpectation, SyntaxErrorExpectation]


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


def run_output_expectation(
    actual: str, expectation: OutputExpectation
) -> typing.Optional[Failure]:
    if actual == expectation.expected:
        return None
    else:
        message = (
            f"Line {expectation.line_number + 1}: "
            f"expected {expectation.expected}, got {actual}."
        )

        return Failure(message)


def parse_expectation(
    line: str, line_number: int
) -> typing.Optional[Expectation]:
    if match := re.search(EXPECTED_OUTPUT_REGEX, line):
        expected = match.group(1)
        return OutputExpectation(expected=expected, line_number=line_number)
    if match := re.search(EXPECTED_SYNTAX_ERROR_REGEX, line):
        line_number_match = match.groupdict()["line_number"] or line_number
        expected_line_number = (
            int(line_number_match) if line_number_match else line_number
        )
        expected = match.groupdict()["error"]
        return SyntaxErrorExpectation(
            expected=expected, line_number=expected_line_number
        )
    else:
        return None


def validate_expectations(
    output_expectations: list[OutputExpectation],
    syntax_error_expectations: list[SyntaxErrorExpectation],
) -> list[Failure]:
    if syntax_error_expectations and output_expectations:
        return [Failure("Can't expect both syntax errors and output")]
    else:
        return []


def verify_syntax_error_expectations(
    error_lines: list[str],
    syntax_error_expectations: list[SyntaxErrorExpectation],
) -> list[Failure]:
    # TODO: implement
    return []


def verify_output_expectations(
    output_lines: list[str], output_expectations: list[OutputExpectation]
) -> list[Failure]:
    if len(output_lines) > len(output_expectations):
        return [Failure("Recieved extra output on stdout.")]

    if len(output_expectations) > len(output_lines):
        return [Failure("Missing expected output on stdout.")]

    return [
        failure
        for actual, expectation in zip(output_lines, output_expectations)
        if (failure := run_output_expectation(actual, expectation))
    ]


def verify_exit_code(
    actual_exit_code: int, expected_exit_code: int
) -> list[Failure]:
    if actual_exit_code != expected_exit_code:
        message = (
            f"Expected interpreter exit code to be {expected_exit_code} "
            f"but received {actual_exit_code}"
        )
        return [Failure(message)]
    else:
        return []


def run_expectations(
    stdout: str,
    stderr: str,
    exit_code: int,
    expectations: list[Expectation],
) -> list[Failure]:
    output_expectations: list[OutputExpectation] = []
    syntax_error_expectations: list[SyntaxErrorExpectation] = []

    for expectation in expectations:
        if type(expectation) is OutputExpectation:
            output_expectations.append(expectation)
        if type(expectation) is SyntaxErrorExpectation:
            syntax_error_expectations.append(expectation)

    output_lines = stdout.splitlines()
    error_lines = stderr.splitlines()

    validation_failures = validate_expectations(
        output_expectations, syntax_error_expectations
    )

    if validation_failures:
        return validation_failures

    if syntax_error_expectations:
        exit_code_failures = verify_exit_code(exit_code, 65)
        syntax_error_expectation_failures = verify_syntax_error_expectations(
            error_lines, syntax_error_expectations
        )
        return syntax_error_expectation_failures + exit_code_failures

    exit_code_failures = verify_exit_code(exit_code, 0)

    output_expectation_failures = verify_output_expectations(
        output_lines, output_expectations
    )

    return output_expectation_failures + exit_code_failures


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
            process.stdout, process.stderr, process.returncode, expectations
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
            print(f"  {failure.message}\n")

    print()
    print(summary_line(summary))


def run_tests() -> None:
    tests = [run_test(path) for path in glob.iglob(TEST_PATH, recursive=True)]
    summary = summarize(tests)

    print_results(tests, summary)

    if summary.failed_count:
        sys.exit(1)


run_tests()
