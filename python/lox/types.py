import typing

if typing.TYPE_CHECKING:
    from lox.interpreter import LoxCallable

Value = typing.Union[str, float, bool, "LoxCallable"]
