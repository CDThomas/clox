import typing

from lox import types


class LoxReturn(Exception):
    def __init__(self, value: typing.Optional[types.Value]) -> None:
        self.value = value
