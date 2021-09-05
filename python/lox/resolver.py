import typing

import lark

from lox import ast
from lox import errors
from lox import interpreter
from lox import visitor


class Resolver(
    visitor.ExpressionVisitor[None], visitor.StatementVisitor[None]
):
    def __init__(self, interpreter: interpreter.Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []

    def resolve(
        self,
        node_or_nodes: typing.Union[
            list[ast._Statement],
            ast._Statement,
            ast._Expression,
        ],
    ) -> None:
        if isinstance(node_or_nodes, list):
            for node in node_or_nodes:
                self.resolve(node)
        else:
            node_or_nodes.accept(self)

    def visit_block_statement(self, statement: ast.Block) -> None:
        self._begin_scope()
        self.resolve(statement.statements)
        self._end_scope()
        return None

    def visit_variable_declaration(
        self, statement: ast.VariableDeclaration
    ) -> None:
        self._declare(statement.name)

        if statement.initializer:
            self.resolve(statement.initializer)

        self._define(statement.name)

        return None

    def visit_variable_expression(self, expression: ast.Variable) -> None:
        if self.scopes and self.scopes[-1][expression.name.value] is False:
            raise errors.LoxRuntimeError(
                expression.name,
                "Can't read local variable in its own initializer.",
            )

        self._resolve_local(expression, expression.name)
        return None

    def visit_assignment_expression(self, expression: ast.Assignment) -> None:
        self.resolve(expression.value)
        self._resolve_local(expression, expression.name)
        return None

    def visit_function_declaration(
        self, statement: ast.FunctionDeclaration
    ) -> None:
        self._declare(statement.name)
        self._define(statement.name)
        self._resolve_function(statement)
        return None

    def visit_expression_statement(
        self, statement: ast.ExpressionStatement
    ) -> None:
        self.resolve(statement.expression)
        return None

    def visit_if_statement(self, statement: ast.IfStatement) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)

        if statement.else_branch:
            self.resolve(statement.else_branch)

        return None

    def visit_print_statement(self, statement: ast.PrintStatement) -> None:
        self.resolve(statement.expression)
        return None

    def visit_return_statement(self, statement: ast.ReturnStatement) -> None:
        if statement.value:
            self.resolve(statement.value)

        return None

    def visit_while_statement(self, statement: ast.WhileStatement) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.body)

        return None

    def visit_binary_expression(self, expression: ast.Binary) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)
        return None

    def visit_call_expression(self, expression: ast.Call) -> None:
        self.resolve(expression.callee)

        for argument in expression.arguments:
            self.resolve(argument)

        return None

    def visit_grouping_expression(self, expression: ast.Grouping) -> None:
        self.resolve(expression.expression)
        return None

    def visit_literal_expression(self, expression: ast.Literal) -> None:
        return None

    def visit_logical_expression(
        self, expression: ast.LogicalExpression
    ) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)
        return None

    def visit_unary_expression(self, expression: ast.Unary) -> None:
        self.resolve(expression.right)
        return None

    def _begin_scope(self) -> None:
        self.scopes.append({})

    def _end_scope(self) -> None:
        self.scopes.pop()

    def _resolve_function(self, func: ast.FunctionDeclaration) -> None:
        self._begin_scope()
        for param in func.params:
            self._declare(param)
            self._define(param)

        self.resolve(func.body)
        self._end_scope()

    def _declare(self, name: lark.Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.value] = False

    def _define(self, name: lark.Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.value] = True

    def _resolve_local(
        self, expression: ast._Expression, name: lark.Token
    ) -> None:
        for index, scope in enumerate(self.scopes):
            if scope[name.value]:
                self.interpreter.resolve(expression, index)
                return
