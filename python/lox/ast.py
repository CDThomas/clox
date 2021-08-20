import dataclasses
import typing

import lark
from lark import ast_utils

# TODO: type hints for this module

Value = typing.Union[str, float, bool]


# Classes that start with an underscore will be skipped by create_transformer.
class _Ast(ast_utils.Ast):
    pass


class _Expression(_Ast):
    def accept(self, visitor):
        pass


class _Statement(_Ast):
    def accept(self, visitor):
        pass


@dataclasses.dataclass
class VariableDeclaration(_Statement):
    name: lark.Token
    initializer: typing.Optional[_Expression] = None

    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)


@dataclasses.dataclass
class ExpressionStatement(_Statement):
    expression: _Expression

    def accept(self, visitor):
        return visitor.visit_expression_statement(self)


@dataclasses.dataclass
class PrintStatement(_Statement):
    expression: _Expression

    def accept(self, visitor):
        return visitor.visit_print_statement(self)


@dataclasses.dataclass
class Block(_Statement, ast_utils.AsList):
    statements: typing.Optional[list[_Statement]] = None

    def accept(self, visitor):
        return visitor.visit_block_statement(self)


@dataclasses.dataclass
class Literal(_Expression):
    value: typing.Optional[Value]

    def accept(self, visitor):
        return visitor.visit_literal_expression(self)


@dataclasses.dataclass
class Unary(_Expression):
    operator: lark.Token
    right: _Expression

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)


@dataclasses.dataclass
class Binary(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor):
        return visitor.visit_binary_expression(self)


@dataclasses.dataclass
class Grouping(_Expression):
    expression: _Expression

    def accept(self, visitor):
        return visitor.visit_grouping_expression(self)


@dataclasses.dataclass
class Variable(_Expression):
    name: lark.Token

    def accept(self, visitor):
        return visitor.visit_variable_expression(self)


@dataclasses.dataclass
class Assignment(_Expression):
    name: lark.Token
    value: _Expression

    def accept(self, visitor):
        return visitor.visit_assignment_expression(self)
