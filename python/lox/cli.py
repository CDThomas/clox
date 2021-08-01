import argparse
import enum
import sys

import lark

import lox.errors
import lox.interpreter
import lox.parser


class InterpreterResult(enum.Enum):
    OK = enum.auto()
    SYNTAX_ERROR = enum.auto()
    RUNTIME_ERROR = enum.auto()


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "path", nargs="?", help="path to the Lox file to run"
    )
    args = arg_parser.parse_args()

    if args.path:
        _run_file(args.path)
    else:
        try:
            _run_prompt()
        except KeyboardInterrupt:
            # Suppress error and exit normally.
            pass


def _run_file(path: str) -> None:
    with open(path, "r") as reader:
        result = _run(reader.read())

        if result == InterpreterResult.SYNTAX_ERROR:
            sys.exit(65)

        if result == InterpreterResult.RUNTIME_ERROR:
            sys.exit(70)


def _run_prompt() -> None:
    while True:
        line = input("> ")

        if line == "":
            break

        _run(line)


def _run(code: str) -> InterpreterResult:
    interpreter = lox.interpreter.Interpreter()

    try:
        ast = lox.parser.parse(code)
    except lark.UnexpectedInput as u:
        print("Syntax error:\n")
        print(u)
        return InterpreterResult.SYNTAX_ERROR

    try:
        interpreter.interpret(ast)
    except lox.errors.LoxRuntimeError as error:
        print(error.message, file=sys.stderr)
        print(f"[line {error.token.line}]", file=sys.stderr)
        return InterpreterResult.RUNTIME_ERROR

    return InterpreterResult.OK


if __name__ == "__main__":
    main()
