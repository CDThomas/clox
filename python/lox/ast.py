import dataclasses
import typing

import lark
from lark import ast_utils

# TODO: type hints for this module

Value = typing.Union[str, float, bool]


class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer() because it starts with an
    # underscore.
    pass


class _Expression(_Ast):
    # This will be skipped by create_transformer() because it starts with an
    # underscore.
    def accept(self, visitor):
        pass


@dataclasses.dataclass
class Literal(_Expression):
    value: typing.Optional[Value]

    def accept(self, visitor):
        return visitor.visitLiteralExpression(self)


@dataclasses.dataclass
class Unary(_Expression):
    operator: lark.Token
    right: _Expression

    def accept(self, visitor):
        return visitor.visitUnaryExpression(self)


@dataclasses.dataclass
class Binary(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor):
        return visitor.visitBinaryExperssion(self)


@dataclasses.dataclass
class Grouping(_Expression):
    expression: _Expression

    def accept(self, visitor):
        return visitor.visitGroupingExperssion(self)
