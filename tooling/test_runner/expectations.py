import re
import typing

EXPECTED_OUTPUT_REGEX: typing.Final = r"// expect: ?(.*)"
EXPECTED_SYNTAX_ERROR_REGEX: typing.Final = (
    r"// (?:\[line (?P<line_number>\d+)\] )?(?P<error>Error.+)"
)
EXPECTED_RUNTIME_ERROR_REGEX: typing.Final = r"// expect runtime error: (.+)"
SYNTAX_ERROR_REGEX: typing.Final = r"^\[line \d+\] Error.+"
STACK_TRACE_REGEX: typing.Final = r"^\[line (\d+)\]"


class Failure(typing.NamedTuple):
    message: str


class _OutputExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class _RuntimeErrorExpectation(typing.NamedTuple):
    expected: str
    line_number: int


class _SyntaxErrorExpectation(typing.NamedTuple):
    expected: str
    line_number: int


_Expectation = typing.Union[
    _OutputExpectation,
    _RuntimeErrorExpectation,
    _SyntaxErrorExpectation,
]


def verify_expectations(
    stdout: str, stderr: str, exit_code: int, path: str
) -> list[Failure]:
    (
        output_expectations,
        runtime_error_expectations,
        syntax_error_expectations,
    ) = _parse_expectations(path)

    output_lines = stdout.splitlines()
    error_lines = stderr.splitlines()

    validation_failures = _validate_expectations(
        output_expectations,
        runtime_error_expectations,
        syntax_error_expectations,
    )

    if validation_failures:
        return validation_failures

    exit_code_failures = _verify_exit_code(
        exit_code, syntax_error_expectations, runtime_error_expectations
    )

    if syntax_error_expectations:
        syntax_error_expectation_failures = _verify_syntax_error_expectations(
            error_lines, syntax_error_expectations
        )
        return syntax_error_expectation_failures + exit_code_failures

    output_expectation_failures = _verify_output_expectations(
        output_lines, output_expectations
    )

    if runtime_error_expectations:
        runtime_error_expectation_failures = (
            _verify_runtime_error_expectations(
                error_lines, runtime_error_expectations
            )
        )
        return (
            output_expectation_failures
            + runtime_error_expectation_failures
            + exit_code_failures
        )

    unexpected_stderr_failures = _verify_empty_stderr(error_lines)

    return (
        output_expectation_failures
        + unexpected_stderr_failures
        + exit_code_failures
    )


def _parse_expectations(
    path: str,
) -> tuple[
    list[_OutputExpectation],
    list[_RuntimeErrorExpectation],
    list[_SyntaxErrorExpectation],
]:
    with open(path, "r") as reader:
        expectations = [
            expectation
            for line_number, line in enumerate(reader)
            if (expectation := _parse_expectation(line, line_number + 1))
        ]

    output_expectations: list[_OutputExpectation] = []
    runtime_error_expectations: list[_RuntimeErrorExpectation] = []
    syntax_error_expectations: list[_SyntaxErrorExpectation] = []

    for expectation in expectations:
        if type(expectation) is _OutputExpectation:
            output_expectations.append(expectation)
        elif type(expectation) is _RuntimeErrorExpectation:
            runtime_error_expectations.append(expectation)
        elif type(expectation) is _SyntaxErrorExpectation:
            syntax_error_expectations.append(expectation)

    return (
        output_expectations,
        runtime_error_expectations,
        syntax_error_expectations,
    )


def _parse_expectation(
    line: str, line_number: int
) -> typing.Optional[_Expectation]:
    if match := re.search(EXPECTED_OUTPUT_REGEX, line):
        expected = match.group(1)
        return _OutputExpectation(expected=expected, line_number=line_number)

    elif match := re.search(EXPECTED_SYNTAX_ERROR_REGEX, line):
        line_number_match = match.groupdict()["line_number"]
        expected_line_number = (
            int(line_number_match) if line_number_match else line_number
        )
        expected = match.groupdict()["error"]
        return _SyntaxErrorExpectation(
            expected=expected, line_number=expected_line_number
        )

    elif match := re.search(EXPECTED_RUNTIME_ERROR_REGEX, line):
        expected = match.group(1)
        return _RuntimeErrorExpectation(
            expected=expected, line_number=line_number
        )

    else:
        return None


def _validate_expectations(
    output_expectations: list[_OutputExpectation],
    runtime_error_expectations: list[_RuntimeErrorExpectation],
    syntax_error_expectations: list[_SyntaxErrorExpectation],
) -> list[Failure]:
    failures: list[Failure] = []

    if syntax_error_expectations and output_expectations:
        failures.append(Failure("Can't expect both syntax errors and output"))

    if syntax_error_expectations and runtime_error_expectations:
        failures.append(
            Failure("Can't expect both syntax errors and runtime errors.")
        )

    if len(runtime_error_expectations) > 1:
        failures.append(Failure("Can't expect more than one runtime error."))

    return failures


def _verify_syntax_error_expectations(
    error_lines: list[str],
    syntax_error_expectations: list[_SyntaxErrorExpectation],
) -> list[Failure]:
    expected_errors = {
        f"[line {expectation.line_number}] {expectation.expected}"
        for expectation in syntax_error_expectations
    }

    found_errors: typing.Set[str] = set()

    failures: list[Failure] = []

    for error_line in error_lines:
        is_syntax_error = bool(re.search(SYNTAX_ERROR_REGEX, error_line))
        is_expected_error = error_line in expected_errors

        if is_syntax_error and is_expected_error:
            found_errors.add(error_line)
        elif is_syntax_error:
            failure = Failure(f"Unexpected syntax error: {error_line}")
            failures.append(failure)
        elif error_line != "":
            failure = Failure(f"Unexpected output on stderr: {error_line}")
            failures.append(failure)

    for expected_error in expected_errors.difference(found_errors):
        failure = Failure(f"Missing expected syntax error: {expected_error}")
        failures.append(failure)

    return failures


def _verify_runtime_error_expectations(
    error_lines: list[str],
    runtime_error_expectations: list[_RuntimeErrorExpectation],
) -> list[Failure]:
    # There will only be one runtime error expectation here since errors have
    # already been validated.
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
        (
            stack_trace_match
            for line in stack_trace_lines
            if (stack_trace_match := re.search(STACK_TRACE_REGEX, line))
        ),
        None,
    )

    if not stack_trace_match:
        failures.append(
            Failure(f"Expected stack trace and got: {stack_trace_lines}")
        )
        return failures

    actual_stack_trace_line_number = int(stack_trace_match.group(1))
    expected_stack_trace_line_number = runtime_error_expectation.line_number

    if actual_stack_trace_line_number != expected_stack_trace_line_number:
        message = (
            f"Expected runtime error on line {expected_stack_trace_line_number}"
            f" but was on line {actual_stack_trace_line_number}."
        )
        failures.append(Failure(message))

    return failures


def _verify_output_expectations(
    output_lines: list[str], output_expectations: list[_OutputExpectation]
) -> list[Failure]:
    if len(output_lines) > len(output_expectations):
        return [Failure("Recieved extra output on stdout.")]

    if len(output_expectations) > len(output_lines):
        return [Failure("Missing expected output on stdout.")]

    return [
        failure
        for actual, expectation in zip(output_lines, output_expectations)
        if (failure := _verify_output_expectation(actual, expectation))
    ]


def _verify_output_expectation(
    actual: str, expectation: _OutputExpectation
) -> typing.Optional[Failure]:
    if actual == expectation.expected:
        return None
    else:
        message = (
            f"Line {expectation.line_number}: "
            f"expected {expectation.expected}, got {actual}."
        )

        return Failure(message)


def _verify_exit_code(
    actual_exit_code: int,
    syntax_error_expectations: list[_SyntaxErrorExpectation],
    runtime_error_expectations: list[_RuntimeErrorExpectation],
) -> list[Failure]:
    expected_exit_code: int
    if runtime_error_expectations:
        expected_exit_code = 70
    elif syntax_error_expectations:
        expected_exit_code = 65
    else:
        expected_exit_code = 0

    if actual_exit_code != expected_exit_code:
        message = (
            f"Expected interpreter exit code to be {expected_exit_code} "
            f"but received {actual_exit_code}"
        )
        return [Failure(message)]
    else:
        return []


def _verify_empty_stderr(error_lines: list[str]) -> list[Failure]:
    if error_lines:
        return [
            Failure(f"Received unexpected output on stderr: {error_lines}")
        ]
    else:
        return []
