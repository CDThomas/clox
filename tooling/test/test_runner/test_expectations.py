import pathlib

from tooling.test_runner import expectations


def test_verify_expectations_with_empty_input(tmp_path: pathlib.Path):
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


def test_verify_expectations_with_passing_output_expectation(
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


def test_verify_expectations_with_multiple_passing_output_expectations(
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


def test_verify_expectations_with_output_expectations_and_empty_std_out(
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


def test_verify_expectations_with_no_output_expectations_and_nonempty_std_out(
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


def test_verify_expectations_with_failing_output_expectation(
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


def test_verify_expectations_with_failing_and_passing_output_expectations(
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
