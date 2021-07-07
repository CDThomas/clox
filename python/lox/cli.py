import argparse

from lox import parser


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
        _run(reader.read())


def _run_prompt() -> None:
    while True:
        line = input("> ")

        if line == "":
            break

        _run(line)


def _run(code: str) -> None:
    print(parser.parse(code))


if __name__ == "__main__":
    main()
