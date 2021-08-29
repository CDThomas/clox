import abc
import lark
import time
import typing

from lox import ast
from lox import environment
from lox import errors
from lox import types


class LoxCallable(abc.ABC):
    @abc.abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def call(
        self,
        interpreter: "Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        raise NotImplementedError

    @abc.abstractmethod
    def to_string(self) -> str:
        raise NotImplementedError


class ClockGlobal(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(
        self,
        interpreter: "Interpreter",
        arguments: list[typing.Optional[types.Value]],
    ) -> typing.Optional[types.Value]:
        return time.perf_counter()

    def to_string(self) -> str:
        return "<native fn>"


class Interpreter:
    def __init__(self) -> None:
        global_env = environment.Environment()
        global_env.define("clock", ClockGlobal())

        self.environment = global_env

    def interpret(self, statements: list[ast._Statement]) -> None:
        for statement in statements:
            self._execute(statement)

        return None

    def visit_expression_statement(
        self, statement: ast.ExpressionStatement
    ) -> None:
        self._evaluate(statement.expression)
        return None

    def visit_if_statement(self, statement: ast.IfStatement) -> None:
        if self._is_truthy(self._evaluate(statement.condition)):
            self._execute(statement.then_branch)
        elif statement.else_branch:
            self._execute(statement.else_branch)

    def visit_print_statement(self, statement: ast.PrintStatement) -> None:
        value = self._evaluate(statement.expression)
        print(self._stringify(value))
        return None

    def visit_variable_declaration(
        self, statement: ast.VariableDeclaration
    ) -> None:
        value = None

        if statement.initializer:
            value = self._evaluate(statement.initializer)

        self.environment.define(statement.name.value, value)

        return None

    def visit_while_statement(self, statement: ast.WhileStatement) -> None:
        while self._is_truthy(self._evaluate(statement.condition)):
            self._execute(statement.body)

        return None

    def visit_assignment_expression(
        self, expression: ast.Assignment
    ) -> typing.Optional[types.Value]:
        value = self._evaluate(expression.value)
        self.environment.assign(expression.name, value)
        return value

    def visit_literal_expression(
        self, expression: ast.Literal
    ) -> typing.Optional[types.Value]:
        return expression.value

    def visit_logical_expression(
        self, expression: ast.LogicalExpression
    ) -> typing.Optional[types.Value]:
        left = self._evaluate(expression.left)

        if expression.operator.value == "or":
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expression.right)

    def visit_grouping_expression(
        self, expression: ast.Grouping
    ) -> typing.Optional[types.Value]:
        return self._evaluate(expression.expression)

    def visit_unary_expression(
        self, expression: ast.Unary
    ) -> typing.Optional[types.Value]:
        right = self._evaluate(expression.right)

        if expression.operator.value == "!":
            return not self._is_truthy(right)
        elif expression.operator.value == "-":
            right = self._check_number_operand(expression.operator, right)
            return -right

        # Unreachable.
        return None

    def visit_variable_expression(
        self, expression: ast.Variable
    ) -> typing.Optional[types.Value]:
        return self.environment.get(expression.name)

    def visit_binary_expression(
        self, expression: ast.Binary
    ) -> typing.Optional[types.Value]:
        left = self._evaluate(expression.left)
        right = self._evaluate(expression.right)

        op = expression.operator.value

        if op == ">":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left > right
        elif op == ">=":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left >= right
        elif op == "<":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left < right
        elif op == "<=":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left <= right
        elif op == "-":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left - right
        elif op == "/":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left / right
        elif op == "*":
            left, right = self._check_number_operands(
                expression.operator, left, right
            )
            return left * right
        elif op == "==":
            return self._is_equal(left, right)
        elif op == "!=":
            return not self._is_equal(left, right)
        elif op == "+":
            if isinstance(left, float) and isinstance(right, float):
                return left + right

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise errors.LoxRuntimeError(
                expression.operator,
                "Operands must be two numbers or two strings.",
            )

        # Unreachable.
        return None

    def visit_call_expression(
        self, expression: ast.Call
    ) -> typing.Optional[types.Value]:
        callee = self._evaluate(expression.callee)

        arguments: list[typing.Optional[types.Value]] = []

        if expression.arguments:
            for argument in expression.arguments:
                arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise errors.LoxRuntimeError(
                expression.closing_paren,
                "Can only call functions and classes.",
            )

        if len(arguments) != callee.arity():
            message = (
                f"Expected {callee.arity()} arguments"
                f"but got {len(arguments)}."
            )

            raise errors.LoxRuntimeError(expression.closing_paren, message)

        return callee.call(self, arguments)

    def visit_block_statement(self, statement: ast.Block) -> None:
        self._execute_block(
            statement.statements, environment.Environment(self.environment)
        )

    def _execute(self, statement: ast._Statement) -> None:
        return statement.accept(self)

    def _execute_block(
        self,
        statements: typing.Optional[list[ast._Statement]],
        environment: environment.Environment,
    ) -> None:
        if not statements:
            return

        prevous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = prevous

    def _evaluate(
        self, expression: ast._Expression
    ) -> typing.Optional[types.Value]:
        return expression.accept(self)

    def _is_truthy(self, value: typing.Optional[types.Value]) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def _is_equal(
        self, a: typing.Optional[types.Value], b: typing.Optional[types.Value]
    ):
        return a == b and type(a) == type(b)

    def _stringify(self, value: typing.Optional[types.Value]) -> str:
        if value is None:
            return "nil"

        if value is True:
            return "true"

        if value is False:
            return "false"

        if isinstance(value, float):
            text = str(value)

            if text.endswith(".0"):
                return text[:-2]
            else:
                return text

        if isinstance(value, LoxCallable):
            return value.to_string()

        return value

    def _check_number_operand(
        self, operator: lark.Token, operand: typing.Optional[types.Value]
    ) -> float:
        if isinstance(operand, float):
            return operand

        raise errors.LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(
        self,
        operator: lark.Token,
        left: typing.Optional[types.Value],
        right: typing.Optional[types.Value],
    ) -> tuple[float, float]:
        if isinstance(left, float) and isinstance(right, float):
            return left, right

        raise errors.LoxRuntimeError(operator, "Operands must be numbers.")
