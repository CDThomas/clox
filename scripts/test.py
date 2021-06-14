import os
import subprocess
from collections import namedtuple

test_dir = os.path.join(os.path.dirname(__file__), "../test")

# TODO:
# - Handle print statements rather than interpreting each line
# - Support expecting errors
# - Support only running certain tests
# - Support choosing an interpreter

Suite = namedtuple("Suite", "path, tests")
Test = namedtuple("Test", "expected, actual, line_number, did_pass")

# (word: str, count: int) -> str
def pluralize(word, count):
  if count == 1:
    return word
  else:
    return word + "s"

# (line: str) -> bool
def should_test_line(line):
  return not line.strip().startswith("//") and "expect:" in line

# (line: str, line_number: int) -> Test
def run_test(line, line_number):
  # Remove print statements until these are supported by the interpreter
  line = line.replace("print", "")

  # Remove semis until these are supported by the interpreter
  line = line.replace(";", "")

  expected = line.partition('expect:')[2].strip()

  # Interpret each line individually until printing (writing to stdout) is supported in interpreter.
  # Later, this can passs the filename to `open` and compare the parsed expecations to stdout.
  result = subprocess.run(
    ["./clox"], capture_output=True, text=True, input=line
  )
  actual = result.stdout.split("\n")[-3]

  did_pass = actual == expected

  return Test(expected=expected, actual=actual, line_number=line_number, did_pass=did_pass)

# path -> Suite
def run_suite(path):
  with open(path, 'r') as reader:
    tests = [run_test(line, line_number)
              for line_number, line
              in enumerate(reader) if should_test_line(line)]

    return Suite(path=path, tests=tests)

def print_results(suites):
  for suite in suites:
    failures = [test for test in suite.tests if not test.did_pass]
    prefix = "❌" if failures else "✅"

    print(f"{prefix} {os.path.relpath(suite.path)}")

    for failure in failures:
      print(f"  Failure at line {failure.line_number + 1}: expected {failure.expected}, got {failure.actual}\n")


  passed_suites_count = 0
  total_tests_count = 0
  passed_tests_count = 0

  for suite in suites:
    results = [test.did_pass for test in suite.tests]

    suite_tests_count = len(results)
    suite_passed_tests_count = results.count(True)

    if suite_tests_count == suite_passed_tests_count:
      passed_suites_count += 1

    total_tests_count += suite_tests_count
    passed_tests_count += suite_passed_tests_count

  total_suites_count = len(suites)
  failed_suites_count = total_suites_count - passed_suites_count
  failed_tests_count = total_tests_count - passed_tests_count

  print(f"Suites: {passed_suites_count} passed, {failed_suites_count} failed, {total_suites_count} total")
  print(f"Tests: {passed_tests_count} passed, {failed_tests_count} failed, {total_tests_count} total")


# run_suites
paths = []
for dirpath, dirnames, files in os.walk(test_dir):
  for file in files:
    paths.append(os.path.join(dirpath, file))

suites = [run_suite(path) for path in paths]
print_results(suites)
