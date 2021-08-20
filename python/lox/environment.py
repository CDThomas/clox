import typing
import lark

from lox import errors
from lox import types


class Environment:
    def __init__(self, enclosing: typing.Optional["Environment"] = None):
        self.values: dict[str, typing.Optional[types.Value]] = {}
        self.enclosing: typing.Optional["Environment"] = enclosing

    def get(self, name: lark.Token) -> typing.Optional[types.Value]:
        if name.value in self.values:
            return self.values[name.value]

        if self.enclosing:
            return self.enclosing.get(name)

        raise errors.LoxRuntimeError(
            name, f"Undefined variable '{name.value}'."
        )

    def define(self, name: str, value: typing.Optional[types.Value]) -> None:
        self.values[name] = value

    def assign(
        self, name: lark.Token, value: typing.Optional[types.Value]
    ) -> None:
        if name.value in self.values:
            self.values[name.value] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise errors.LoxRuntimeError(
            name, f"Undefined variable '{name.value}'."
        )
