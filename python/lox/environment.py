import typing
import lark

from lox import errors
from lox import types


class Environment:
    def __init__(self):
        self.values = {}

    def get(self, name: lark.Token) -> typing.Optional[types.Value]:
        if name.value in self.values:
            return self.values[name.value]

        raise errors.LoxRuntimeError(name, f"Undefined variable {name.value}.")

    def define(self, name: str, value: typing.Optional[types.Value]) -> None:
        self.values[name] = value
