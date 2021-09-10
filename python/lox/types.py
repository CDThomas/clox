import typing

if typing.TYPE_CHECKING:
    from lox import lox_callable
    from lox import lox_class

Value = typing.Union[
    str, float, bool, "lox_callable.LoxCallable", "lox_class.LoxClass"
]
