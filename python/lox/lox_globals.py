import time
import typing

from lox import lox_callable
from lox import types

if typing.TYPE_CHECKING:
    from lox import interpreter


class ClockGlobal(lox_callable.LoxCallable):
    def arity(self) -> int:
        return 0

    def call(
        self,
        interpreter: "interpreter.Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        return time.perf_counter()

    def to_string(self) -> str:
        return "<native fn>"
