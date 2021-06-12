import os
import subprocess

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../test/bool/equality.lox')

# start with assertions for single lines without errors

def pluralize(word, count):
  if count == 1:
    return word
  else:
    return word + "s"

def do_test(line, line_number):
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
    print(f"Failure at line {line_number + 1}:")
    print(line)

  return passed

with open(filename, 'r') as reader:
  results = [do_test(line, line_number)
             for line_number, line
             in enumerate(reader) if "expect:" in line]

  if all(results):
    print("All tests passed!")
  else:
    failed_count = results.count(False)

    print(str(failed_count) + " " + pluralize("test", failed_count) + " failed.")
