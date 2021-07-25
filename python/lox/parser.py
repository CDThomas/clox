import lark
from lark import ast_utils
import typing

import lox.ast


class ToAst(lark.Transformer):
    # Define extra transformation functions, for rules that don't correspond
    # to an AST class.
    def program(
        self, statements: list[lox.ast._Statement]
    ) -> list[lox.ast._Statement]:
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


# Assumes project root is cwd
parser = lark.Lark.open(
    "./python/lox/grammar.lark", parser="lalr", start="program"
)

transformer = ast_utils.create_transformer(lox.ast, ToAst())


def parse(text):
    tree = parser.parse(text)
    return transformer.transform(tree)
