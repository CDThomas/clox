import argparse
import sys

import lox.interpreter
import lox.parser


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
        had_runtime_error = _run(reader.read())

        if had_runtime_error:
            sys.exit(70)


def _run_prompt() -> None:
    while True:
        line = input("> ")

        if line == "":
            break

        _run(line)


def _run(code: str) -> bool:
    had_runtime_error = False
    interpreter = lox.interpreter.Interpreter()

    # TODO: handle syntax errors
    ast = lox.parser.parse(code)

    try:
        interpreter.interpret(ast)
    except lox.interpreter.LoxRuntimeError as error:
        print(error.message, file=sys.stderr)
        print(f"[line {error.token.line}]", file=sys.stderr)
        had_runtime_error = True

    return had_runtime_error


if __name__ == "__main__":
    main()
