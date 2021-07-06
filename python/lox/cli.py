import lark
from lark import ast_utils

import lox.ast


class ToAst(lark.Transformer):
    # Define extra transformation functions, for rules that don't correspond
    # to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def NUMBER(self, n):
        return float(n)

    def const_true(self, _):
        return True

    def const_false(self, _):
        return False

    def const_nil(self, _):
        return None


parser = lark.Lark.open(
    "./lox/grammar.lark", parser="lalr", start="expression"
)

transformer = ast_utils.create_transformer(lox.ast, ToAst())


def parse(text):
    tree = parser.parse(text)
    return transformer.transform(tree)


#
#   Test
#

if __name__ == "__main__":
    print(
        parse(
            """\
(1 + 3) - 2
"""
        )
    )
