import typing

from lox import lox_callable
from lox import lox_function
from lox import lox_instance
from lox import types

if typing.TYPE_CHECKING:
    from lox import interpreter


class LoxClass(lox_callable.LoxCallable):
    def __init__(
        self, name: str, methods: dict[str, lox_function.LoxFunction]
    ) -> None:
        self.name = name
        self.methods = methods

    def find_method(
        self, name: str
    ) -> typing.Optional[lox_function.LoxFunction]:
        if name in self.methods:
            return self.methods[name]

        return None

    def call(
        self,
        interpreter: "interpreter.Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        instance = lox_instance.LoxInstance(self)

        if initializer := self.find_method("init"):
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")

        if not initializer:
            return 0

        return initializer.arity()

    def to_string(self) -> str:
        return self.name
