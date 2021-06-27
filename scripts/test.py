import enum
import glob
import os
import re
import subprocess
import sys
import typing

# TODO:
# - Support only running certain tests
# - Support choosing an interpreter
# - Add flag for condensed/verbose output

# Assumes cwd is project root.
TEST_PATH: typing.Final = "test/**/*.lox"

EXPECTED_OUTPUT_REGEX: typing.Final = r"// expect: ?(.*)"
EXPECTED_SYNTAX_ERROR_REGEX: typing.Final = (
    r"// (?:\[line (?P<line_number>\d+)\] )?(?P<error>Error.+)"
)
EXPECTED_RUNTIME_ERROR_REGEX: typing.Final = r"// expect runtime error: (.+)"
SYNTAX_ERROR_REGEX: typing.Final = r"^\[line \d+\] Error.+"
STACK_TRACE_REGEX: typing.Final = r"^\[line (\d+)\]"


class OutputExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class RuntimeErrorExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class SyntaxErrorExpectation(typing.NamedTuple):
    expected: str
    line_number: int


Expectation = typing.Union[
    OutputExpectation,
    RuntimeErrorExpectation,
    SyntaxErrorExpectation,
]


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


def verify_output_expectation(
    actual: str, expectation: OutputExpectation
) -> typing.Optional[Failure]:
    if actual == expectation.expected:
        return None
    else:
        message = (
            f"Line {expectation.line_number}: "
            f"expected {expectation.expected}, got {actual}."
        )

        return Failure(message)


def parse_expectation(
    line: str, line_number: int
) -> typing.Optional[Expectation]:
    if match := re.search(EXPECTED_OUTPUT_REGEX, line):
        expected = match.group(1)
        return OutputExpectation(expected=expected, line_number=line_number)

    elif match := re.search(EXPECTED_SYNTAX_ERROR_REGEX, line):
        line_number_match = match.groupdict()["line_number"]
        expected_line_number = (
            int(line_number_match) if line_number_match else line_number
        )
        expected = match.groupdict()["error"]
        return SyntaxErrorExpectation(
            expected=expected, line_number=expected_line_number
        )

    elif match := re.search(EXPECTED_RUNTIME_ERROR_REGEX, line):
        expected = match.group(1)
        return RuntimeErrorExpectation(
            expected=expected, line_number=line_number
        )

    else:
        return None


def validate_expectations(
    output_expectations: list[OutputExpectation],
    runtime_error_expectations: list[RuntimeErrorExpectation],
    syntax_error_expectations: list[SyntaxErrorExpectation],
) -> list[Failure]:
    if syntax_error_expectations and output_expectations:
        return [Failure("Can't expect both syntax errors and output")]
    if syntax_error_expectations and runtime_error_expectations:
        return [Failure("Can't expect both syntax errors and runtime errors.")]
    elif len(runtime_error_expectations) > 1:
        return [Failure("Can't expect more than one runtime error.")]
    else:
        return []


def verify_syntax_error_expectations(
    error_lines: list[str],
    syntax_error_expectations: list[SyntaxErrorExpectation],
) -> list[Failure]:
    expected_errors = {
        f"[line {expectation.line_number}] {expectation.expected}"
        for expectation in syntax_error_expectations
    }

    found_errors: typing.Set[str] = set()

    failures: list[Failure] = []

    for error_line in error_lines:
        if re.search(SYNTAX_ERROR_REGEX, error_line):
            if error_line in expected_errors:
                found_errors.add(error_line)
            else:
                failure = Failure(f"Unexpected syntax error: {error_line}")
                failures.append(failure)
        elif error_line != "":
            # TODO: this fallthrough is confusing since it handles unexpected
            # runtime errors too. Should prob move this up a level.
            failure = Failure(f"Unexpected output on stderr: {error_line}")
            failures.append(failure)

    for expected_error in expected_errors.difference(found_errors):
        failure = Failure(f"Missing expected syntax error: {expected_error}")
        failures.append(failure)

    return failures


def verify_runtime_error_expectations(
    error_lines: list[str],
    # TODO: don't really need to use a list for runtime_error_expectations here
    runtime_error_expectations: list[RuntimeErrorExpectation],
) -> list[Failure]:
    runtime_error_expectation = runtime_error_expectations[0]
    if len(error_lines) < 2:
        message = (
            "Expected runtime error "
            f"'{runtime_error_expectation.expected}' and got none."
        )
        return [Failure(message)]

    failures: list[Failure] = []

    if runtime_error_expectation.expected != error_lines[0]:
        message = (
            "Expected runtime error "
            f"'{runtime_error_expectation.expected}' "
            f"and got '{error_lines[0]}'"
        )
        failures.append(Failure(message))

    stack_trace_lines = error_lines[1:]

    stack_trace_match = next(
        stack_trace_match
        for line in stack_trace_lines
        if (stack_trace_match := re.search(STACK_TRACE_REGEX, line))
    )

    if not stack_trace_match:
        failures.append(
            Failure(f"Expected stack trace and got:\n{stack_trace_lines}")
        )

    actual_stack_trace_line_number = int(stack_trace_match.group(1))
    expected_stack_trace_line_number = runtime_error_expectation.line_number

    if actual_stack_trace_line_number != expected_stack_trace_line_number:
        message = (
            f"Expected runtime error on line {actual_stack_trace_line_number}"
            f" but was on line {expected_stack_trace_line_number}."
        )
        failures.append(Failure(message))

    return failures


def verify_output_expectations(
    output_lines: list[str], output_expectations: list[OutputExpectation]
) -> list[Failure]:
    # TODO: it's possibly confusing that this is here vs in the
    # validate_expectations func
    if len(output_lines) > len(output_expectations):
        return [Failure("Recieved extra output on stdout.")]

    if len(output_expectations) > len(output_lines):
        return [Failure("Missing expected output on stdout.")]

    return [
        failure
        for actual, expectation in zip(output_lines, output_expectations)
        if (failure := verify_output_expectation(actual, expectation))
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


def verify_expectations(
    stdout: str,
    stderr: str,
    exit_code: int,
    expectations: list[Expectation],
) -> list[Failure]:
    output_expectations: list[OutputExpectation] = []
    runtime_error_expectations: list[RuntimeErrorExpectation] = []
    syntax_error_expectations: list[SyntaxErrorExpectation] = []

    for expectation in expectations:
        if type(expectation) is OutputExpectation:
            output_expectations.append(expectation)
        elif type(expectation) is RuntimeErrorExpectation:
            runtime_error_expectations.append(expectation)
        elif type(expectation) is SyntaxErrorExpectation:
            syntax_error_expectations.append(expectation)

    output_lines = stdout.splitlines()
    error_lines = stderr.splitlines()

    validation_failures = validate_expectations(
        output_expectations,
        runtime_error_expectations,
        syntax_error_expectations,
    )

    if validation_failures:
        return validation_failures

    expected_exit_code: int
    if runtime_error_expectations:
        expected_exit_code = 70
    elif syntax_error_expectations:
        expected_exit_code = 65
    else:
        expected_exit_code = 0

    exit_code_failures = verify_exit_code(exit_code, expected_exit_code)

    runtime_error_expectation_failures: list[Failure] = []

    if runtime_error_expectations:
        runtime_error_expectation_failures = verify_runtime_error_expectations(
            error_lines, runtime_error_expectations
        )
    else:
        syntax_error_expectation_failures = verify_syntax_error_expectations(
            error_lines, syntax_error_expectations
        )

        if syntax_error_expectation_failures:
            return syntax_error_expectation_failures + exit_code_failures

    output_expectation_failures = verify_output_expectations(
        output_lines, output_expectations
    )

    return (
        output_expectation_failures
        + runtime_error_expectation_failures
        + exit_code_failures
    )


def run_test(path: str) -> Test:
    with open(path, "r") as reader:
        expectations = [
            expectation
            for line_number, line in enumerate(reader)
            if (expectation := parse_expectation(line, line_number + 1))
        ]

        # Assumes release build of clox (or at least no debug output).
        process = subprocess.run(
            ["./clox", path], capture_output=True, text=True
        )

        failures = verify_expectations(
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
