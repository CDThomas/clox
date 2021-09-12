import enum
import typing

import lark

from lox import ast
from lox import errors
from lox import interpreter
from lox import visitor


class FunctionType(enum.Enum):
    NONE = enum.auto()
    FUNCTION = enum.auto()
    INITIALIZER = enum.auto()
    METHOD = enum.auto()


class ClassType(enum.Enum):
    NONE = enum.auto()
    CLASS = enum.auto()


class Resolver(
    visitor.ExpressionVisitor[None], visitor.StatementVisitor[None]
):
    def __init__(self, interpreter: interpreter.Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

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

    def visit_class_declaration(self, statement: ast.ClassDeclaration) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self._declare(statement.name)
        self._define(statement.name)

        if (
            statement.superclass
            and statement.name.value == statement.superclass.name.value
        ):
            raise errors.LoxResolutionError(
                statement.superclass.name, "A class can't inherit from itself."
            )

        if statement.superclass:
            self.resolve(statement.superclass)

        self._begin_scope()
        self.scopes[-1]["this"] = True

        for method in statement.methods:
            declaration = (
                FunctionType.INITIALIZER
                if method.name.value == "init"
                else FunctionType.METHOD
            )

            self._resolve_function(method, declaration)

        self._end_scope()
        self.current_class = enclosing_class

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
        if self.scopes and self.scopes[-1].get(expression.name.value) is False:
            raise errors.LoxResolutionError(
                expression.name,
                "Can't read local variable in its own initializer.",
            )

        self._resolve_local(expression, expression.name)
        return None

    def visit_assignment_expression(self, expression: ast.Assignment) -> None:
        self.resolve(expression.value)
        self._resolve_local(expression, expression.name)
        return None

    def visit_function(self, statement: ast.Function) -> None:
        self._declare(statement.name)
        self._define(statement.name)
        self._resolve_function(statement, FunctionType.FUNCTION)
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
        if self.current_function == FunctionType.NONE:
            raise errors.LoxResolutionError(
                statement.keyword, "Can't return from top-level code."
            )

        if statement.value:
            if self.current_function == FunctionType.INITIALIZER:
                raise errors.LoxResolutionError(
                    statement.keyword,
                    "Can't return a value from an initializer.",
                )

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

    def visit_get_expression(self, expression: ast.Get) -> None:
        self.resolve(expression.obj)
        return None

    def visit_set_expression(self, expression: ast.Set) -> None:
        self.resolve(expression.value)
        self.resolve(expression.obj)
        return None

    def visit_this_expression(self, expression: ast.This) -> None:
        if self.current_class == ClassType.NONE:
            raise errors.LoxResolutionError(
                expression.keyword, "Can't use 'this' outside of a class."
            )

        self._resolve_local(expression, expression.keyword)

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

    def _resolve_function(
        self, func: ast.Function, func_type: FunctionType
    ) -> None:
        enclosing_function = self.current_function
        self.current_function = func_type
        self._begin_scope()

        for param in func.params:
            self._declare(param)
            self._define(param)

        self.resolve(func.body)
        self._end_scope()
        self.current_function = enclosing_function

    def _declare(self, name: lark.Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]

        if name.value in scope:
            raise errors.LoxResolutionError(
                name, "Already a variable with this name in this scope."
            )

        scope[name.value] = False

    def _define(self, name: lark.Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.value] = True

    def _resolve_local(
        self, expression: ast._Expression, name: lark.Token
    ) -> None:
        for depth, scope in enumerate(reversed(self.scopes)):
            if name.value in scope:
                self.interpreter.resolve(expression, depth)
                return
