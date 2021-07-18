import argparse

from tooling.test_runner import test_runner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "interpreter_path", help="path to the interpreter executable"
    )
    parser.add_argument(
        "test_pattern",
        nargs="+",
        help="pattern for test(s) to run (supports glob syntax)",
    )
    args = parser.parse_args()

    test_runner.run_tests(args.interpreter_path, args.test_pattern)


if __name__ == "__main__":
    main()
