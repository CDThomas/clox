import dataclasses
import lark

# TODO: type hints for this module


class _Ast(lark.ast_utils.Ast):
    # This will be skipped by create_transformer() because it starts with an
    # underscore.
    pass


class _Expression(_Ast):
    # This will be skipped by create_transformer() because it starts with an
    # underscore.
    pass


@dataclasses.dataclass
class Literal(_Expression):
    # TODO: better type for value
    value: object

    def accept(self, visitor):
        return visitor.visitLiteralExpression(self)


@dataclasses.dataclass
class Unary(_Expression):
    operator: str
    right: _Expression

    def accept(self, visitor):
        return visitor.visitUnaryExperssion(self)


@dataclasses.dataclass
class Binary(_Expression):
    left: _Expression
    operator: str
    right: _Expression

    def accept(self, visitor):
        return visitor.visitBinaryExperssion(self)


@dataclasses.dataclass
class Grouping(_Expression):
    expression: _Expression

    def accept(self, visitor):
        return visitor.visitGroupingExperssion(self)
