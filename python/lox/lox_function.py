import typing

from lox import ast
from lox import environment
from lox import lox_callable
from lox import lox_return
from lox import types

if typing.TYPE_CHECKING:
    from lox import interpreter


class LoxFunction(lox_callable.LoxCallable):
    def __init__(
        self,
        declaration: ast.Function,
        closure: environment.Environment,
    ) -> None:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(
        self,
        interpreter: "interpreter.Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        env = environment.Environment(self.closure)

        for index, param in enumerate(self.declaration.params):
            env.define(param.value, arguments[index])

        try:
            interpreter._execute_block(self.declaration.body, env)
        except lox_return.LoxReturn as return_value:
            return return_value.value

        return None

    def to_string(self) -> str:
        return f"<fn {self.declaration.name.value}>"
