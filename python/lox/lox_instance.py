import typing

import lark

from lox import errors
from lox import types

if typing.TYPE_CHECKING:
    from lox import lox_class


class LoxInstance:
    def __init__(self, klass: "lox_class.LoxClass") -> None:
        self.klass = klass
        self.fields: dict[str, typing.Optional[types.Value]] = {}

    def get(self, name: lark.Token) -> typing.Optional[types.Value]:
        if name.value in self.fields:
            return self.fields[name.value]

        raise errors.LoxRuntimeError(name, f"Undefined property {name.value}.")

    def set(
        self, name: lark.Token, value: typing.Optional[types.Value]
    ) -> None:
        self.fields[name.value] = value

    def to_string(self) -> str:
        return f"{self.klass.name} instance"
