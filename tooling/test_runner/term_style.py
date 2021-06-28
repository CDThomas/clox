import enum


class Ansi_Code(enum.Enum):
    RESET = "\u001b[0m"
    REVERSED = "\u001b[7m"
    BOLD = "\u001b[1m"
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"


def green(text: str) -> str:
    return _format(text, [Ansi_Code.GREEN])


def red(text: str) -> str:
    return _format(text, [Ansi_Code.RED])


def bold(text: str) -> str:
    return _format(text, [Ansi_Code.BOLD])


def green_background(text: str) -> str:
    return _format(text, [Ansi_Code.GREEN, Ansi_Code.REVERSED])


def red_background(text: str) -> str:
    return _format(text, [Ansi_Code.RED, Ansi_Code.REVERSED])


def _format(text: str, ansi_codes: list[Ansi_Code]) -> str:
    ansi_code_str = "".join([ansi_code.value for ansi_code in ansi_codes])
    return f"{ansi_code_str}{text}{Ansi_Code.RESET.value}"
