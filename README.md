# Lox

This repo contains two implementations of the Lox language from [Crafting Interpreters](http://www.craftinginterpreters.com/).

The first implementation, [Pylox](#pylox), is a Python port of the tree-walk interpreter, Jlox, from [part two of the book](https://craftinginterpreters.com/a-tree-walk-interpreter.html).

The second, [Clox](#clox), is the C implementation of the bytecode VM from [part three](https://craftinginterpreters.com/a-bytecode-virtual-machine.html).

This repo also contains a [shared test runner](#test-runner) for testing the two Lox implementations.
## Pylox

Pylox is a port of Jlox to Python. The source code is in the [`python`](./python) directory.

The functionality of Pylox mostly lines up with Jlox, but there are a couple of key differences in the implementation (apart from being written in Python):
1. I've used [Lark](https://lark-parser.readthedocs.io/en/latest/index.html) for parsing in place of implementing the lexer and parser described in the book. I chose this approach out of interest in learning more about parser generators.
1. I've skipped using code to generate the AST classes. This is because the AST implemenation using Python's [Data Classes](https://docs.python.org/3/library/dataclasses.html) isn't much more verbose than the code to generate them would have been.

### Running and Developing

To start the REPL, run:
```
$ ./pylox
```

You can also specify a Lox file to run instead:
```
$ ./pylox my_file.lox
```

To run all tests for Pylox:
```
$ make test_pylox
```

To check types with Mypy:
```
$ make typecheck_pylox
```

## Clox

Clox is lifted directly from the code in the book (apart from some minor differences in formatting). The source code is in the [`c`](./c) directory.

### Running and Developing

To build the Clox interpreter, run:
```
$ make clox
```

After building, you can start the REPL:
```
$ ./clox
```

You can also specify a Lox file to run instead:
```
$ ./clox my_file.lox
```

To run all tests for Clox:
```
$ make test_clox
```

## Test Runner

The Crafting Interpreters text omits tests, but the Github repo for the book includes a [full test suite](https://github.com/munificent/craftinginterpreters/tree/master/test) and [custom test runner](https://github.com/munificent/craftinginterpreters/blob/master/tool/bin/test.dart).

I've included a test runner in this repo (based on the implementation in the book's Github repo) and copied over the test files. The source code is in the [`tooling`](./tooling) directory.

### Usage

The [Makefile](./Makefile) contains convenience targets for running all tests for either Pylox or Clox, but you can also call the test runner directly via [Poetry](https://python-poetry.org/):
```
$ poetry run test interpreter_path test_pattern
```

Usage:
```
test [-h] interpreter_path test_pattern [test_pattern ...]

positional arguments:
  interpreter_path  path to the interpreter executable
  test_pattern      pattern for test(s) to run (supports glob syntax)

optional arguments:
  -h, --help        show this help message and exit
```

### Developing

To run all tests that test the test runner itself:
```
$ make test_tooling
```

To check types with Mypy:
```
$ make typecheck_tooling
```
