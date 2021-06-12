import os
import subprocess

test_dir = os.path.join(os.path.dirname(__file__), "../test")

# start with assertions for single lines without errors

def pluralize(word, count):
  if count == 1:
    return word
  else:
    return word + "s"

def should_test_line(line):
  return not line.strip().startswith("//") and "expect:" in line

def test_line(line, line_number):
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

  passed = actual == expected

  if not passed:
    print("\n")
    print(f"Failure at line {line_number + 1}:")
    print(f"Actual: {actual}")
    print(f"Expected: {expected}")
    print(f"Line: {line}")

  return passed

def test_file(file):
  with open(file, 'r') as reader:
    results = [test_line(line, line_number)
              for line_number, line
              in enumerate(reader) if should_test_line(line)]

    if all(results):
      print("All tests passed!")
    else:
      failed_count = results.count(False)

      print(str(failed_count) + " " + pluralize("test", failed_count) + " failed.")

for dirpath, dirnames, files in os.walk(test_dir):
  for file in files:
    filepath = os.path.join(dirpath, file)
    print(f"Running tests in {os.path.relpath(filepath)} ...")
    test_file(filepath)
    print("\n")
