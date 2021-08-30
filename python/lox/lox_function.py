import typing

from lox import ast
from lox import environment
from lox import lox_callable
from lox import types

if typing.TYPE_CHECKING:
    from lox import interpreter


class LoxFunction(lox_callable.LoxCallable):
    def __init__(self, declaration: ast.FunctionDeclaration) -> None:
        self.declaration = declaration

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(
        self,
        interpreter: "interpreter.Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        env = environment.Environment(interpreter.globals)

        for index, param in enumerate(self.declaration.params):
            env.define(param.value, arguments[index])

        interpreter._execute_block(self.declaration.body, env)

        return None

    def to_string(self) -> str:
        return f"<fn {self.declaration.name.value}>"
