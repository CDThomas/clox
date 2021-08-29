import abc
import typing

from lox import types

if typing.TYPE_CHECKING:
    from lox import interpreter


class LoxCallable(abc.ABC):
    @abc.abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def call(
        self,
        interpreter: "interpreter.Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        raise NotImplementedError

    @abc.abstractmethod
    def to_string(self) -> str:
        raise NotImplementedError
