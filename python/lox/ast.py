import abc
import dataclasses
import typing

import lark
from lark import ast_utils

if typing.TYPE_CHECKING:
    from lox import visitor

Value = typing.Union[str, float, bool]

S = typing.TypeVar("S")
T = typing.TypeVar("T")


# Classes that start with an underscore will be skipped by create_transformer.
class _Ast(ast_utils.Ast):
    pass


class _Statement(abc.ABC, _Ast):
    @abc.abstractmethod
    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        raise NotImplementedError


class _Expression(abc.ABC, _Ast):
    @abc.abstractmethod
    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        raise NotImplementedError


@dataclasses.dataclass
class FunctionDeclaration(_Statement):
    name: lark.Token
    params: list[lark.Token]
    body: list[_Statement]

    def __init__(
        self,
        name: lark.Token,
        params: typing.Optional[list[lark.Token]],
        block: typing.Optional["Block"],
    ) -> None:
        if params is None:
            params = []

        if block and block.statements:
            body = block.statements
        else:
            body = []

        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_function_declaration(self)


@dataclasses.dataclass
class VariableDeclaration(_Statement):
    name: lark.Token
    # TODO: consider replacing defaults like this with [...] syntax
    # in grammar file
    initializer: typing.Optional[_Expression] = None

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_variable_declaration(self)


@dataclasses.dataclass
class ExpressionStatement(_Statement):
    expression: _Expression

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_expression_statement(self)


@dataclasses.dataclass
class PrintStatement(_Statement):
    expression: _Expression

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_print_statement(self)


@dataclasses.dataclass
class ReturnStatement(_Statement):
    keyword: lark.Token
    value: _Expression

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_return_statement(self)


@dataclasses.dataclass
class WhileStatement(_Statement):
    condition: _Expression
    body: _Statement

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_while_statement(self)


@dataclasses.dataclass
class Block(_Statement, ast_utils.AsList):
    statements: typing.Optional[list[_Statement]] = None

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_block_statement(self)


@dataclasses.dataclass
class IfStatement(_Statement):
    condition: _Expression
    then_branch: _Statement
    else_branch: typing.Optional[_Statement] = None

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_if_statement(self)


@dataclasses.dataclass
class Literal(_Expression):
    value: typing.Optional[Value]

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_literal_expression(self)


@dataclasses.dataclass
class Unary(_Expression):
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_unary_expression(self)


@dataclasses.dataclass
class Binary(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_binary_expression(self)


@dataclasses.dataclass
class Call(_Expression):
    callee: _Expression
    arguments: typing.Optional[list[_Expression]]
    closing_paren: lark.Token

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_call_expression(self)


@dataclasses.dataclass
class Grouping(_Expression):
    expression: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_grouping_expression(self)


@dataclasses.dataclass
class Variable(_Expression):
    name: lark.Token

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_variable_expression(self)


@dataclasses.dataclass
class Assignment(_Expression):
    name: lark.Token
    value: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_assignment_expression(self)


@dataclasses.dataclass
class LogicalExpression(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_logical_expression(self)
