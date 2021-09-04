import abc
import typing

from lox import ast

S = typing.TypeVar("S")
T = typing.TypeVar("T")


class StatementVisitor(abc.ABC, typing.Generic[S]):
    @abc.abstractmethod
    def visit_expression_statement(
        self, statement: ast.ExpressionStatement
    ) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_function_declaration(
        self, statement: ast.FunctionDeclaration
    ) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_if_statement(self, statement: ast.IfStatement) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_print_statement(self, statement: ast.PrintStatement) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_return_statement(self, statement: ast.ReturnStatement) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_variable_declaration(
        self, statement: ast.VariableDeclaration
    ) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_while_statement(self, statement: ast.WhileStatement) -> S:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_block_statement(self, statement: ast.Block) -> S:
        raise NotImplementedError


class ExpressionVisitor(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def visit_assignment_expression(self, expression: ast.Assignment) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_literal_expression(self, expression: ast.Literal) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_logical_expression(self, expression: ast.LogicalExpression) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_grouping_expression(self, expression: ast.Grouping) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unary_expression(self, expression: ast.Unary) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_variable_expression(self, expression: ast.Variable) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_binary_expression(self, expression: ast.Binary) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_call_expression(self, expression: ast.Call) -> T:
        raise NotImplementedError
