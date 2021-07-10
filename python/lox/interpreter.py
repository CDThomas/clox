import typing

from lox import ast
from lox import token

Value = typing.Union[str, float, bool]


class Interpreter:
    def interpret(self, expression: ast._Expression):
        try:
            value = self._evaluate(expression)
            return self._stringify(value)
        except:
            # TODO: handle runtime errors
            pass

    def visitLiteralExpression(
        self, expression: ast.Literal
    ) -> typing.Optional[Value]:
        return expression.value

    def visitGroupingExpression(
        self, expression: ast.Grouping
    ) -> typing.Optional[Value]:
        return self._evaluate(expression.expression)

    def visitUnaryExpression(
        self, expression: ast.Unary
    ) -> typing.Optional[Value]:
        right = self._evaluate(expression.right)

        if expression.operator.type == token.TokenType.BANG.value:
            return not self._is_truthy(right)
        elif expression.operator.type == token.TokenType.MINUS.value:
            # TODO: remove cast
            return -typing.cast(float, right)

        # Unreachable.
        return None

    def _evaluate(self, expression: ast._Expression) -> typing.Optional[Value]:
        return expression.accept(self)

    def _is_truthy(self, value: typing.Optional[Value]) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def _stringify(self, value: typing.Optional[Value]) -> str:
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
