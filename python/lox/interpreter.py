import lark
import typing

from lox import ast
from lox import errors
from lox import types

# Pick up at 8.3.1: interpreting global variables


class Interpreter:
    def interpret(self, statements: list[ast._Statement]) -> None:
        for statement in statements:
            self._execute(statement)

        return None

    def visit_expression_statement(
        self, statement: ast.ExpressionStatement
    ) -> None:
        self._evaluate(statement.expression)
        return None

    def visit_print_statement(self, statement: ast.PrintStatement) -> None:
        value = self._evaluate(statement.expression)
        print(self._stringify(value))
        return None

    def visit_literal_expression(
        self, expression: ast.Literal
    ) -> typing.Optional[types.Value]:
        return expression.value

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

    def _execute(self, statement: ast._Statement) -> None:
        return statement.accept(self)

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
