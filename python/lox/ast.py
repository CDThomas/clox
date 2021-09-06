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

    def __hash__(self) -> int:
        return hash(id(self))

    def __eq__(self, other) -> bool:
        return self is other


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
    statements: list[_Statement]

    def __init__(self, statements: typing.Optional[list[_Statement]]):
        self.statements = statements or []

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_block_statement(self)


@dataclasses.dataclass
class IfStatement(_Statement):
    condition: _Expression
    then_branch: _Statement
    else_branch: typing.Optional[_Statement] = None

    def accept(self, visitor: "visitor.StatementVisitor[S]") -> "S":
        return visitor.visit_if_statement(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Literal(_Expression):
    value: typing.Optional[Value]

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_literal_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Unary(_Expression):
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_unary_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Binary(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_binary_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Call(_Expression):
    callee: _Expression
    arguments: list[_Expression]
    closing_paren: lark.Token

    def __init__(
        self,
        callee: _Expression,
        arguments: typing.Optional[list[_Expression]],
        closing_paren: lark.Token,
    ) -> None:
        self.callee = callee
        self.arguments = arguments or []
        self.closing_paren = closing_paren

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_call_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Grouping(_Expression):
    expression: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_grouping_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Variable(_Expression):
    name: lark.Token

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_variable_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class Assignment(_Expression):
    name: lark.Token
    value: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_assignment_expression(self)


@dataclasses.dataclass(eq=False, unsafe_hash=True)
class LogicalExpression(_Expression):
    left: _Expression
    operator: lark.Token
    right: _Expression

    def accept(self, visitor: "visitor.ExpressionVisitor[T]") -> "T":
        return visitor.visit_logical_expression(self)
