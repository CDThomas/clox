import lark
from lark import ast_utils
import typing

from lox import ast


class ToAst(lark.Transformer):
    # Define extra transformation functions, for rules that don't correspond
    # to an AST class.
    def program(
        self, statements: list[ast._Statement]
    ) -> list[ast._Statement]:
        return statements

    def STRING(self, s: str) -> str:
        # Remove quotation marks
        return s[1:-1]

    def NUMBER(self, n: str) -> float:
        return float(n)

    def IDENTIFIER(self, identifier: str) -> str:
        return identifier

    def const_true(self, _: str) -> typing.Literal[True]:
        return True

    def const_false(self, _: str) -> typing.Literal[False]:
        return False

    def const_nil(self, _: str) -> None:
        return None

    def empty_initializer(self, _: str) -> None:
        return None

    def for_statement(self, args: list[typing.Optional[ast._Ast]]) -> ast._Ast:
        [initializer, condition, increment, body] = args
        assert isinstance(body, ast._Statement)

        if increment:
            assert isinstance(increment, ast._Expression)
            body = ast.Block([body, ast.ExpressionStatement(increment)])

        if not condition:
            condition = ast.Literal(True)

        assert isinstance(condition, ast._Expression)

        body = ast.WhileStatement(condition, body)

        if initializer:
            assert isinstance(initializer, ast._Statement)
            body = ast.Block([initializer, body])

        return body

    def arguments(self, args: list[ast._Expression]) -> list[ast._Expression]:
        return args

    def parameters(self, params: list[lark.Token]) -> list[lark.Token]:
        return params


# Assumes project root is cwd
parser = lark.Lark.open(
    "./python/lox/grammar.lark",
    parser="lalr",
    start="program",
    maybe_placeholders=True,
)

transformer = ast_utils.create_transformer(ast, ToAst())


def parse(text):
    tree = parser.parse(text)
    return transformer.transform(tree)
