import typing

if typing.TYPE_CHECKING:
    from lox import lox_callable

Value = typing.Union[str, float, bool, "lox_callable.LoxCallable"]
