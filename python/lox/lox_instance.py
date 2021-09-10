import typing

if typing.TYPE_CHECKING:
    from lox import lox_class


class LoxInstance:
    def __init__(self, klass: "lox_class.LoxClass") -> None:
        self.klass = klass

    def to_string(self) -> str:
        return f"{self.klass.name} instance"
