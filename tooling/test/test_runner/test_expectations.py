import pathlib

from test_runner import expectations


def test_empty_input(tmp_path: pathlib.Path):
    path = tmp_path / "test.lox"
    path.write_text("")

    stdout = ""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_passing_output_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
"""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_multiple_passing_output_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
print false; // expect: false
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
false
"""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_output_expectations_and_empty_std_out(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message="Missing expected output on stdout.")
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_no_output_expectations_and_nonempty_std_out(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true;
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
"""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message="Recieved extra output on stdout.")
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_failing_output_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print false; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
false
"""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message="Line 1: expected true, got false.")
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_failing_and_passing_output_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
print false; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
false
"""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message="Line 2: expected true, got false.")
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_error_and_output_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true

// [line 5] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 5] Error: Unterminated string.
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Can't expect both syntax errors and output"
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_and_runtime_error_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.

// [line 5] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 5] Error: Unterminated string.
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Can't expect both syntax errors and runtime errors."
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_multiple_runtime_error_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
huh = "what"; // expect runtime error: Undefined variable 'huh'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Undefined variable 'unknown'.
[line 1] in script
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Can't expect more than one runtime error."
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_multiple_expectation_validation_failures(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
huh = "what"; // expect runtime error: Undefined variable 'huh'.

// [line 5] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Can't expect both syntax errors and output"
        ),
        expectations.Failure(
            message="Can't expect both syntax errors and runtime errors."
        ),
        expectations.Failure(
            message="Can't expect more than one runtime error."
        ),
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_output_expectations_and_wrong_exit_code(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
"""
    stderr = ""
    exit_code = 1

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Expected interpreter exit code to be 0 but received 1"
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_passing_runtime_error_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Undefined variable 'unknown'.
[line 1] in script
"""
    exit_code = 70

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_runtime_error_expectation_and_empty_stderr(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 70

    message = (
        "Expected runtime error 'Undefined variable 'unknown'.' and got none."
    )

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_runtime_error_expectation_and_wrong_stderr(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Different runtime error.
[line 1] in script
"""
    exit_code = 70

    message = (
        "Expected runtime error 'Undefined variable 'unknown'.' "
        "and got 'Different runtime error.'"
    )

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_runtime_error_expectation_and_no_stacktrace(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Undefined variable 'unknown'.
Stack trace should be here.
"""
    exit_code = 70

    message = "Expected stack trace and got: ['Stack trace should be here.']"

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_runtime_error_expectation_on_wrong_line(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what";
// expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Undefined variable 'unknown'.
[line 1] in script
"""
    exit_code = 70

    message = "Expected runtime error on line 2 but was on line 1."

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_runtime_error_and_wrong_exit_code(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
Undefined variable 'unknown'.
[line 1] in script
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            message="Expected interpreter exit code to be 70 but received 0"
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_passing_syntax_error_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 2] Error: Unterminated string.
"""
    exit_code = 65

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_error_expectation_and_extra_err(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 2] Error: Unterminated string.
[line 3] Error: different error.
"""
    exit_code = 65

    message = "Unexpected syntax error: [line 3] Error: different error."

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_error_expectation_and_wrong_stderr(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 2] Error: Unterminated string.
Extra output
"""
    exit_code = 65

    message = "Unexpected output on stderr: Extra output"

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_error_expectation_and_no_stderr(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 65

    message = (
        "Missing expected syntax error: [line 2] Error: Unterminated string."
    )

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_syntax_error_expectation_and_wrong_exit_code(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 2] Error: Unterminated string.
"""
    exit_code = 70

    message = "Expected interpreter exit code to be 65 but received 70"

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message)
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_multiple_passing_syntax_error_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 3] Error at '{': Expect expression.
// [line 3] Error at ')': Expect ';' after expression.
for (var a = 1; {}; a = a + 1) {}
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = """\
[line 3] Error at '{': Expect expression.
[line 3] Error at ')': Expect ';' after expression.
"""
    exit_code = 65

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_passing_output_and_runtime_error_expectations(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
unknown = 1; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
"""
    stderr = """\
Undefined variable 'unknown'.
[line 2] in script
"""
    exit_code = 70

    expected_failures: list[expectations.Failure] = []

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_wrong_exit_code_and_failing_output_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
print true; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 1

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message="Missing expected output on stdout."),
        expectations.Failure(
            message="Expected interpreter exit code to be 0 but received 1"
        ),
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_wrong_exit_code_and_failing_runtime_error_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
unknown = "what"; // expect runtime error: Undefined variable 'unknown'.
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 0

    message_one = (
        "Expected runtime error 'Undefined variable 'unknown'.' and got none."
    )
    message_two = "Expected interpreter exit code to be 70 but received 0"

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message_one),
        expectations.Failure(message_two),
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_wrong_exit_code_and_failing_syntax_error_expectation(
    tmp_path: pathlib.Path,
):
    lox_file_content = """\
// [line 2] Error: Unterminated string.
"this string has no close quote
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = ""
    stderr = ""
    exit_code = 0

    message_one = (
        "Missing expected syntax error: [line 2] Error: Unterminated string."
    )
    message_two = "Expected interpreter exit code to be 65 but received 0"

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(message_one),
        expectations.Failure(message_two),
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_no_expectations_and_nonempty_stderr(
    tmp_path: pathlib.Path,
):
    path = tmp_path / "test.lox"
    path.write_text("")

    stdout = ""
    stderr = """\
Error: some error.
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            "Received unexpected output on stderr: ['Error: some error.']"
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures


def test_only_output_expectations_and_nonempty_stderr(tmp_path: pathlib.Path):
    lox_file_content = """\
print true; // expect: true
"""

    path = tmp_path / "test.lox"
    path.write_text(lox_file_content)

    stdout = """\
true
"""
    stderr = """\
Error: some error.
"""
    exit_code = 0

    expected_failures: list[expectations.Failure] = [
        expectations.Failure(
            "Received unexpected output on stderr: ['Error: some error.']"
        )
    ]

    actual_failures = expectations.verify_expectations(
        stdout=stdout, stderr=stderr, exit_code=exit_code, path=str(path)
    )

    assert actual_failures == expected_failures
