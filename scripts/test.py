import os
import subprocess
import dataclasses
import collections

# TODO:
# - Handle print statements rather than interpreting each line
# - Support expecting errors
# - Support only running certain tests
# - Support choosing an interpreter

# Constants
TEST_DIR = os.path.join(os.path.dirname(__file__), "../test")

RESET = "\u001b[0m"
BOLD = "\u001b[1m"
RED = "\u001b[31;1m"
GREEN = "\u001b[32;1m"

# Data structures
Suite = collections.namedtuple("Suite", ["path", "tests"])
Test = collections.namedtuple("Test", ["expected", "actual", "line_number", "did_pass"])
Summary = dataclasses.make_dataclass("Summary", ["passed", "failed", "total"])

def color(text, color):
  return f"{color}{text}{RESET}"

def green(text):
  return color(text, GREEN)

def red(text):
  return color(text, RED)

def bold(text):
  return color(text, BOLD)

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

# [Suite] -> Summary, Summary
def summarize(suites):
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

# [Suite] -> None
def print_results(suites):
  for suite in suites:
    failures = [test for test in suite.tests if not test.did_pass]
    prefix = "❌" if failures else "✅"

    print(f"{prefix} {os.path.relpath(suite.path)}")

    for failure in failures:
      print(f"  Failure at line {failure.line_number + 1}: expected {failure.expected}, got {failure.actual}\n")

  suite_summary, test_summary = summarize(suites)

  print()
  print(bold("Suites:"), green(f"{suite_summary.passed} passed,"), red(f"{suite_summary.failed} failed,"), f"{suite_summary.total} total")
  print(bold("Tests:"), green(f"{test_summary.passed} passed,"), red(f"{test_summary.failed} failed,"), f"{test_summary.total} total")

# () -> None
def run_suites():
  paths = []
  for dirpath, dirnames, files in os.walk(TEST_DIR):
    for file in files:
      paths.append(os.path.join(dirpath, file))

  suites = [run_suite(path) for path in paths]
  print_results(suites)

run_suites()
